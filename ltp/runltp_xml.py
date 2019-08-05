#!/usr/bin/env python3

#
# Copyright (C) 2019  Wojtek Porczyk <woju@invisiblethingslab.com>
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as
# published by the Free Software Foundation; either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.
#

import argparse
import asyncio
import configparser
import logging
import os
import pathlib
import shlex
import signal
import subprocess
import sys
import time

import xml.etree.ElementTree as etree

argparser = argparse.ArgumentParser()
argparser.add_argument('--config', '-c', metavar='FILENAME',
    type=argparse.FileType('r'),
    help='config file (default: %(default)s)')

argparser.add_argument('--option', '-o', metavar='KEY=VALUE',
    action='append',
    help='set an option')

argparser.add_argument('--verbose', '-v',
    action='count',
    help='increase verbosity')

argparser.add_argument('cmdfile', metavar='FILENAME',
    type=argparse.FileType('r'),
    nargs='?',
    help='cmdfile (default: stdin)')

argparser.set_defaults(
    config='ltp.conf',
    option=[],
    verbose=0,
    cmdfile='-')

_log = logging.getLogger('LTP')  # pylint: disable=invalid-name

class TestRunner:
    # pylint: disable=too-few-public-methods
    def __init__(self, suite, tag, cmd):
        self.suite = suite
        self.tag = tag
        self.cmd = cmd

        try:
            self.cfgsection = self.suite.config[self.tag]
        except configparser.NoSectionError:
            self.cfgsection = self.suite.config[
                self.suite.config.defaultsection]

        self.classname = self.cfgsection.get('junit-classname')
        self.log = _log.getChild(self.tag)

        self.stdout = None
        self.stderr = None
        self.time = None

        self._added_result_with_time = False


    def _get_subtest_logger(self, subtest):
        return self.log if subtest is None else self.log.getChild(str(subtest))

    def _add_result(self, subtest):
        element = etree.Element('testcase',
            classname=self.classname,
            name=('{}/{}'.format(self.tag, subtest)
                if subtest is not None
                else self.tag))

        self.suite.add_result(element)
        self.suite.inc('tests')

        if self.time is not None and subtest is None:
            assert not self._added_result_with_time
            self._added_result_with_time = True
            element.set('time', '{:.3f}'.format(self.time))
            self.suite.inc('time', self.time, type=float, fmt='.3f')

        if self.stdout is not None:
            etree.SubElement(element, 'system-out').text = self.stdout
        if self.stderr is not None:
            etree.SubElement(element, 'system-err').text = self.stderr

        return element

    def success(self, *, subtest=None):
        # pylint: disable=redefined-outer-name
        self._get_subtest_logger(subtest).info('-> PASS')
        self._add_result(subtest)

    def failure(self, message, *, subtest=None):
        # pylint: disable=redefined-outer-name
        self._get_subtest_logger(subtest).warning('-> FAIL (%s)', message)
        etree.SubElement(self._add_result(subtest), 'failure', message=message)
        self.suite.inc('failures')

    def error(self, message, *, subtest=None):
        # pylint: disable=redefined-outer-name
        self._get_subtest_logger(subtest).error('-> ERROR (%s)', message)
        etree.SubElement(self._add_result(subtest), 'error').text = message
        self.suite.inc('errors')

    def skipped(self, message, *, subtest=None):
        # pylint: disable=redefined-outer-name
        self._get_subtest_logger(subtest).warning('-> SKIP (%s)', message)
        etree.SubElement(self._add_result(subtest), 'skipped').text = message
        self.suite.inc('skipped')


    async def _run_cmd(self):
        cmd = [*self.suite.loader, *shlex.split(self.cmd)]
        timeout = self.cfgsection.getfloat('timeout')
        self.log.info('starting %r with timeout %d', cmd, timeout)
        start_time = time.time()

        # pylint: disable=subprocess-popen-preexec-fn
        proc = await asyncio.create_subprocess_exec(
            *cmd,
            cwd=self.suite.bindir,
            stdout=subprocess.PIPE, stderr=subprocess.PIPE,
            preexec_fn=os.setsid,
            close_fds=True)

        try:
            stdout, stderr = await asyncio.wait_for(
                proc.communicate(), timeout=timeout)

        except subprocess.TimeoutExpired as err:
            if err.stdout is not None:
                self.stdout = err.stdout.decode()
            if err.stderr is not None:
                self.stderr = err.stderr.decode()
            self.error('Timed out after {} s.')
            return

        finally:
            try:
                os.killpg(os.getpgid(proc.pid), signal.SIGKILL)
            except ProcessLookupError:
                pass

        self.time = time.time() - start_time

        assert proc.pid is not None
        self.log.debug('finished pid=%d returncode=%d stdout=%r',
            proc.pid, proc.returncode, stdout)
        if stderr:
            self.log.info('stderr=%r', stderr)

        self.stdout, self.stderr = stdout.decode(), stderr.decode()

        return proc.returncode

    async def execute(self):
        if self.cfgsection.getboolean('skip', fallback=False):
            self.skipped('skipped via config')
            return

        if any(c in self.cmd for c in ';|&'):
            # This is a shell command which would spawn multiple processes.
            # We don't run those in unit tests.
            if 'must-pass' in self.cfgsection:
                self.error('invalid shell command with must-pass')
            else:
                self.skipped('invalid shell command')
            return

        async with self.suite.semaphore:
            returncode = await self._run_cmd()

        try:
            must_pass = self.cfgsection.getset('must-pass')
        except configparser.NoOptionError:
            # must-pass is not set -- report single result
            if returncode == 0:
                self.success()
            else:
                self.failure('failed')
            return
        else:
            self._parse_test_output(must_pass)

    def _parse_test_output(self, must_pass):
        # pylint: disable=too-many-branches

        not_found = must_pass.copy()
        maybe_unneeded_must_pass = True
        has_result = False

        subtest = 0
        for line in self.stdout.split('\n'):
            self.log.debug('<- %r', line)

            if line == 'Summary:':
                break

            # Drop this line so that we get consistent offsets
            if line == 'WARNING: no physical memory support, process creation may be slow.':
                continue

            tokens = line.split()
            if len(tokens) < 2:
                continue

            if 'INFO' in line:
                continue

            if tokens[1].isdigit():
                subtest = int(tokens[1])
            else:
                subtest += 1

            try:
                not_found.remove(subtest)
            except KeyError:
                # subtest is not in must-pass
                maybe_unneeded_must_pass = False

            if 'TPASS' in line or 'PASS:' in line:
                self.success(subtest=subtest)
                has_result = True
                continue

            if any(t in line for t in (
                    'TFAIL', 'TCONF', 'CONF:', 'TBROK', 'BROK:')):
                if subtest in must_pass:
                    self.failure(line, subtest=subtest)
                    maybe_unneeded_must_pass = False
                else:
                    self.skipped(line, subtest=subtest)
                has_result = True
                continue

            self.error(line, subtest=subtest)

        for subtest in sorted(not_found):
            self.failure('not even attempted', subtest=subtest)

        if maybe_unneeded_must_pass and not not_found:
            # all subtests passed and must-pass specified exactly all subtests
            self.error('must-pass is unneeded, remove it from config')

        if not has_result:
            self.error('binary did not provide any subtests')

class TestSuite:
    def __init__(self, config):
        self.config = config

        self.loader = [
            str(config.getpath(config.default_section, 'loader').resolve())]
        if self.config.getboolean(config.default_section, 'sgx'):
            self.loader.append('SGX')

        self.bindir = str(
            config.getpath(config.default_section, 'ltproot') / 'testcases/bin')

        # Running parallel tests under SGX is risky, see README.
        # However, if user wanted to do that, we shouldn't stand in the way,
        # just issue a warning.
        has_sgx = config.getboolean(config.default_section, 'sgx')
        processes = config.getint(config.default_section, 'jobs',
            fallback=(1 if has_sgx else None))
        if has_sgx and processes != 1:
            _log.warning('WARNING: SGX is enabled and jobs = %d (!= 1);'
                ' expect stability issues', processes)

        self.semaphore = asyncio.BoundedSemaphore(processes)
        self.queue = []
        self.xml = etree.Element('testsuite')
        self.time = 0

    def add_test(self, tag, cmd):
        self.queue.append(TestRunner(self, tag, cmd))

    def add_result(self, element):
        self.xml.append(element)

    def inc(self, accumulator, value=1, *, type=int, fmt=''):
        # pylint: disable=redefined-builtin
        self.xml.set(accumulator,
            format(type(self.xml.get(accumulator, 0)) + value, fmt))


    def write_report(self, stream):
        etree.ElementTree(self.xml).write(stream)

    async def execute(self):
        await asyncio.gather(*(runner.execute() for runner in self.queue))


def _getintset(value):
    return set(int(i) for i in value.strip().split())

def load_config(file):
    config = configparser.ConfigParser(
        converters={
            'path': pathlib.Path,
            'intset': _getintset,
        },
        defaults={
            'timeout': '30',
            'sgx': 'false',
            'loader': './pal_loader',
            'ltproot': './opt/ltp',
            'junit-classname': 'LTP',
        })

    with file:
        config.read_file(file)

    return config

def main(args=None):
    logging.basicConfig(
        format='%(asctime)s %(name)s: %(message)s',
        level=logging.WARNING)
    args = argparser.parse_args(args)
    _log.setLevel(_log.level - args.verbose * 10)

    config = load_config(args.config)
    for token in args.option:
        key, value = token.split('=', maxsplit=1)
        config[config.default_section][key] = value

    suite = TestSuite(config)
    with args.cmdfile as file:
        for line in file:
            if line[0] in '\n#':
                continue
            tag, cmd = line.strip().split(maxsplit=1)
            suite.add_test(tag, cmd)

    loop = asyncio.get_event_loop()
    loop.run_until_complete(suite.execute())
    suite.write_report(sys.stdout.buffer)

if __name__ == '__main__':
    main()
