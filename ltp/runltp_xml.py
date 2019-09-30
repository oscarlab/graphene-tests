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

try:
    fspath = os.fspath
except AttributeError:
    fspath = str

DEFAULT_CONFIG = 'ltp.conf'

argparser = argparse.ArgumentParser()
argparser.add_argument('--config', '-c', metavar='FILENAME',
    action='append',
    type=argparse.FileType('r'),
    help='config file (default: {}); may be given multiple times'.format(
        DEFAULT_CONFIG))

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
    config=None,
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
        except (configparser.NoSectionError, KeyError):
            self.cfgsection = self.suite.config[
                self.suite.config.default_section]

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

    def make_manifest(self):
        ((self.suite.bindir / self.cmd[0]).with_suffix('.manifest')
            .symlink_to('manifest'))

    async def _run_cmd(self):
        if self.suite.sgx:
            self.make_manifest()

        cmd = [*self.suite.loader, *self.cmd]
        timeout = self.cfgsection.getfloat('timeout')
        self.log.info('starting %r with timeout %d', cmd, timeout)
        start_time = time.time()

        # pylint: disable=subprocess-popen-preexec-fn
        proc = await asyncio.create_subprocess_exec(
            *cmd,
            cwd=fspath(self.suite.bindir),
            stdout=subprocess.PIPE, stderr=subprocess.PIPE,
            preexec_fn=os.setsid,
            close_fds=True)

        try:
            stdout, stderr = await asyncio.wait_for(
                proc.communicate(), timeout=timeout)

        except asyncio.TimeoutError:
            self.time = time.time() - start_time

            if sys.version_info >= (3, 7):
                # https://bugs.python.org/issue32751 (fixed in 3.7) causes
                # proc.communicate() task inside wait_for() to be cancelled,
                # but it most likely didn't get scheduled, so the coroutine
                # inside is still waiting for CancelledError delivery and is not
                # actually done waiting for stdio. No two tasks should await the
                # same input. Rather than reimplement fix for the bug, better
                # update, hence the warning.
                self.stdout = (await proc.stdout.read()).decode()
                self.stderr = (await proc.stderr.read()).decode()
            else:
                self.log.warning('cannot extract stdio on python < 3.7')

            self.error('Timed out after {} s.'.format(timeout))
            return

        finally:
            try:
                os.killpg(os.getpgid(proc.pid), signal.SIGKILL)
            except ProcessLookupError:
                pass

        self.time = time.time() - start_time

        assert proc.pid is not None
        self.log.info('finished pid=%d time=%.3f returncode=%d stdout=%r',
            proc.pid, self.time, proc.returncode, stdout)
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

        if returncode is None:
            # timed out
            return

        must_pass = self.cfgsection.getintset('must-pass')
        if must_pass is None:
            # must-pass is not set -- report single result
            if returncode == 0:
                self.success()
            else:
                self.failure('returncode={}'.format(returncode))
            return
        else:
            self._parse_test_output(must_pass)

    def _parse_test_output(self, must_pass):
        # pylint: disable=too-many-branches

        not_found = must_pass.copy()

        # on empty must_pass, it is always needed
        maybe_unneeded_must_pass = bool(must_pass)
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
                    'TFAIL', 'FAIL:', 'TCONF', 'CONF:', 'TBROK', 'BROK:')):
                if subtest in must_pass:
                    self.failure(line, subtest=subtest)
                    maybe_unneeded_must_pass = False
                else:
                    self.skipped(line, subtest=subtest)
                has_result = True
                continue

            #self.error(line, subtest=subtest)
            self.log.info('additional info: %s', line)

        for subtest in sorted(not_found):
            self.failure('not even attempted', subtest=subtest)

        if not has_result:
            if must_pass:
                self.error('binary did not provide any subtests')
            else:
                self.log.warning(
                    'binary without subtests, but must_pass is empty')
        elif maybe_unneeded_must_pass and not not_found:
            # all subtests passed and must-pass specified exactly all subtests
            self.error('must-pass is unneeded, remove it from config')

class TestSuite:
    def __init__(self, config):
        self.config = config
        self.sgx = self.config.getboolean(config.default_section, 'sgx')

        self.loader = [
            fspath(config.getpath(config.default_section, 'loader').resolve())]
        if self.sgx:
            self.loader.append('SGX')

        self.bindir = (
            config.getpath(config.default_section, 'ltproot') / 'testcases/bin')

        # Running parallel tests under SGX is risky, see README.
        # However, if user wanted to do that, we shouldn't stand in the way,
        # just issue a warning.
        processes = config.getint(config.default_section, 'jobs',
            fallback=(1 if self.sgx else len(os.sched_getaffinity(0))))
        if self.sgx and processes != 1:
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

    def _get(self, accumulator, *, default=0, type=int):
        return type(self.xml.get(accumulator, default))

    def inc(self, accumulator, value=1, *, type=int, fmt=''):
        # pylint: disable=redefined-builtin
        self.xml.set(accumulator,
            format(self._get(accumulator, type=type) + value, fmt))

    @property
    def returncode(self):
        return min(255, self._get('errors') + self._get('failures'))

    def write_report(self, stream):
        etree.ElementTree(self.xml).write(stream)

    async def execute(self):
        await asyncio.gather(*(runner.execute() for runner in self.queue))


def _getintset(value):
    return set(int(i) for i in value.strip().split())

def load_config(files):
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

    for file in files:
        with file:
            config.read_file(file)

    return config

def main(args=None):
    logging.basicConfig(
        format='%(asctime)s %(name)s: %(message)s',
        level=logging.WARNING)
    args = argparser.parse_args(args)
    _log.setLevel(_log.level - args.verbose * 10)

    if args.config is None:
        args.config = [open(DEFAULT_CONFIG)]

    config = load_config(args.config)
    for token in args.option:
        key, value = token.split('=', maxsplit=1)
        config[config.default_section][key] = value

    suite = TestSuite(config)
    with args.cmdfile as file:
        for line in file:
            if line[0] in '\n#':
                continue
            tag, *cmd = shlex.split(line)
            suite.add_test(tag, cmd)

    try:
        loop = asyncio.get_event_loop()
        loop.run_until_complete(suite.execute())
    finally:
        loop.close()
    suite.write_report(sys.stdout.buffer)
    return suite.returncode

if __name__ == '__main__':
    sys.exit(main())
