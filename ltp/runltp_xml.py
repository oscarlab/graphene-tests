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
import configparser
import logging
import multiprocessing
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

_log = logging.getLogger()

class TestRunner:
    def __init__(self, config):
        self.config = config

        self.loader = [
            str(config.getpath(config.default_section, 'loader').resolve())]
        if self.config.getboolean(config.default_section, 'sgx'):
            self.loader.append('SGX')

        self.bindir = str(
            config.getpath(config.default_section, 'ltproot') / 'testcases/bin')

    def run_test(self, tag, cmd):
        # NOTE that this function is run in multiprocessing.Pool, so the return
        # value is constrained: it should be picklable. Currently we pass a list
        # of etree.Element()s.

        result = XMLTestResultFactory(
            tag, self.config.get(tag, 'junit-classname'))

        if self.config.getboolean(tag, 'skip', fallback=False):
            _log.info('%s: SKIP (config)', tag)
            return 0, [result.skipped('skipped via config')]

        if any(c in cmd for c in ';|&'):
            # This is a shell command which would spawn multiple processes.
            # We don't run those in unit tests.
            _log.info('%s: SKIP (shell command)', tag)
            return 0, [result.skipped('skipped for invalid shell command')]

        xfail = self.config.getintset(tag, 'xfail', fallback=set())

        cmd = [*self.loader, *shlex.split(cmd)]
        timeout = self.config.getfloat(tag, 'timeout')
        _log.info('%s: starting %r with timeout %d', tag, cmd, timeout)
        start_time = time.time()
        proc = subprocess.Popen(cmd,
            cwd=self.bindir,
            stdout=subprocess.PIPE, stderr=subprocess.PIPE,
            preexec_fn=os.setsid,
            close_fds=True)
        try:
            stdout, stderr = proc.communicate(timeout=timeout)
        except subprocess.TimeoutExpired as e:
            _log.warning('%s: -> FAIL (timeout %d s)', tag, timeout)
            if e.stdout is not None:
                result.stdout = e.stdout.decode()
            if e.stderr is not None:
                result.stderr = e.stderr.decode()
            return timeout, [
                result.error('Timed out after {} s.'.format(timeout))]
        finally:
            try:
                os.killpg(os.getpgid(proc.pid), signal.SIGKILL)
            except ProcessLookupError:
                pass

        cmd_time = time.time() - start_time

        assert proc.pid is not None
        _log.debug('%s: finished pid=%d returncode=%d stdout=%r',
            tag, proc.pid, proc.returncode, stdout)
        if stderr:
            _log.info('%s: stderr: %r', stderr)

        result.stdout, result.stderr = stdout.decode(), stderr.decode()
        partial = list(
            self._parse_test_output(tag, result.stdout, result, xfail))
        if not partial:
            partial.append(result.error('binary did not provide any results'))
        return cmd_time, partial

    @staticmethod
    def _parse_test_output(tag, stdout, result, xfail):
        subtest = 0
        for line in stdout.split('\n'):
            _log.debug('%s: <- %r', tag, line)

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

            result.name = '{}/{}'.format(tag, subtest)

            if 'TPASS' in line or 'PASS:' in line:
                if subtest in xfail:
                    _log.warning('%s/%d: -> XFAIL/PASS', tag, subtest)
                    yield result.skipped(line)
                else:
                    _log.info('%s/%d: -> PASS', tag, subtest)
                    yield result.success()
                continue

            if 'TFAIL' in line:
                if subtest in xfail:
                    _log.info('%s/%d: -> XFAIL', tag, subtest)
                    yield result.skipped(line)
                else:
                    _log.warning('%s/%d: -> FAIL', tag, subtest)
                    yield result.failure(line)
                continue

            if any(t in line for t in ('TCONF', 'CONF:', 'TBROK', 'BROK:')):
                _log.warning('%s/%d: -> SKIP', tag, subtest)
                yield result.skipped(line)
                continue

            _log.debug('%s/%d: -> ERROR', tag, subtest)
            yield result.error(line)

class XMLTestResultFactory:
    def __init__(self, name, classname, stdout=None, stderr=None):
        self.name = name
        self.classname = classname
        self.stdout = stdout
        self.stderr = stderr

    def _get_new_element(self):
        element = etree.Element('testcase',
            name=self.name, classname=self.classname)
        if self.stdout is not None:
            etree.SubElement(element, 'system-out').text = self.stdout
        if self.stderr is not None:
            etree.SubElement(element, 'system-err').text = self.stderr
        return element

    def success(self):
        return self._get_new_element()

    def failure(self, message):
        element = self._get_new_element()
        etree.SubElement(element, 'failure', message=message)
        return element

    def error(self, message):
        element = self._get_new_element()
        etree.SubElement(element, 'error').text = message
        return element

    def skipped(self, message):
        element = self._get_new_element()
        etree.SubElement(element, 'skipped').text = message
        return element

class XMLReport:
    def __init__(self):
        self.root = etree.Element('testsuite')

    def inc(self, accumulator, value=1, *, type=int, fmt=''):
        self.root.set(accumulator,
            format(type(self.root.get(accumulator, 0)) + value, fmt))

    def add_result(self, element):
        self.root.append(element)
        self.inc('tests')
        self.inc('failures', len(element.findall('failure')))
        self.inc('skipped', len(element.findall('skipped')))
        self.inc('errors', len(element.findall('error')))

    def write(self, stream):
        etree.ElementTree(self.root).write(stream)

class LTPConfigParser(configparser.ConfigParser):
    # ConfigParser raises NoSectionError for nonexistent sections, even when the
    # option value is set in [DEFAULT]. That's documented and expected, but not
    # what we want. We want to return the default value even for nonexistent
    # sections.
    def get(self, section, *args, **kwds):
        try:
            return super().get(section, *args, **kwds)
        except configparser.NoSectionError:
            return super().get(self.default_section, *args, **kwds)

def _getintset(value):
    return set(int(i) for i in value.strip().split())

def load_config(file):
    config = LTPConfigParser(
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
    logging.basicConfig(format='%(asctime)s %(message)s', level=logging.WARNING)
    args = argparser.parse_args(args)
    _log.setLevel(_log.level - args.verbose * 10)

    config = load_config(args.config)
    for token in args.option:
        key, value = token.split('=', maxsplit=1)
        config[config.default_section][key] = value

    tests = []
    with args.cmdfile as file:
        for line in file:
            if line[0] in '\n#':
                continue
            tag, cmd = line.strip().split(maxsplit=1)
            tests.append((tag, cmd))

    report = XMLReport()
    runner = TestRunner(config)

    # Running parallel tests under SGX is risky, see README. However, if user
    # wanted to do that, we shouldn't stand in the way, just issue a warning.
    has_sgx = self.config.getboolean(config.default_section, 'sgx')
    processes = config.getint(config.default_section, 'jobs',
        fallback=(1 if has_sgx else None))
    if has_sgx and processes != 1:
        _log.warning('WARNING: SGX is enabled and jobs = %d (!= 1);'
            ' expect stability issues', processes)

    total_time = 0
    with multiprocessing.Pool(processes) as pool:
        for cmd_time, partial in pool.starmap(runner.run_test, tests):
            for element in partial:
                report.add_result(element)
            total_time += cmd_time

    report.inc('time', total_time, type=float, fmt='.3f')
    report.write(sys.stdout.buffer)

if __name__ == '__main__':
    main()
