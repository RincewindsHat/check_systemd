"""Test the command line interface. The CLI interface is implemented with
argparse."""

import unittest
from .helper import execute_main
import check_systemd
from check_systemd import get_argparser
import subprocess
import io
from contextlib import redirect_stderr


class TestFromFunction(unittest.TestCase):

    def test_default(self):
        opts = get_argparser().parse_args([])
        self.assertEqual('cli', opts.data_source)

    def test_dbus(self):
        opts = get_argparser().parse_args(['--dbus'])
        self.assertEqual('dbus', opts.data_source)

    def test_cli(self):
        opts = get_argparser().parse_args(['--cli'])
        self.assertEqual('cli', opts.data_source)

    def test_exclusive_cli_dbus(self):
        dev_null = io.StringIO()
        with self.assertRaises(SystemExit) as cm, redirect_stderr(dev_null):
            get_argparser().parse_args(['--cli', '--dbus'])
        self.assertEqual(cm.exception.code, 2)


class TestWithMocking(unittest.TestCase):

    def test_without_arguments(self):
        result = execute_main()
        self.assertEqual(result.exitcode, 0)

    def test_help_short(self):
        result = execute_main(argv=['-h'])
        self.assertIn('usage: check_systemd', result.output)

    def test_help_long(self):
        result = execute_main(argv=['--help'])
        self.assertIn('usage: check_systemd', result.output)

    def test_version_short(self):
        result = execute_main(argv=['-V'])
        self.assertIn('check_systemd ' +
                      check_systemd.__version__, result.output)

    def test_version_long(self):
        result = execute_main(argv=['--version'])
        self.assertIn('check_systemd ' +
                      check_systemd.__version__, result.output)


class TestWithSubprocess(unittest.TestCase):

    def test_help(self):
        process = subprocess.run(
            ['./check_systemd.py', '--help'],
            encoding='utf-8',
            stdout=subprocess.PIPE
        )
        self.assertEqual(process.returncode, 0)
        self.assertIn('usage: check_systemd', process.stdout)

    def test_version(self):
        process = subprocess.run(
            ['./check_systemd.py', '--version'],
            encoding='utf-8',
            stdout=subprocess.PIPE
        )
        self.assertEqual(process.returncode, 0)
        self.assertIn('check_systemd ' +
                      check_systemd.__version__, process.stdout)

    def test_exclusive_cli_dbus(self):
        process = subprocess.run(
            ['./check_systemd.py', '--cli', '--dbus'],
            encoding='utf-8',
            stderr=subprocess.PIPE
        )
        self.assertEqual(process.returncode, 2)
        self.assertIn(
            'error: argument --dbus: not allowed with argument --cli',
            process.stderr,
        )

    def test_entry_point(self):
        process = subprocess.run(
            ['check_systemd', '--help'],
            encoding='utf-8',
            stdout=subprocess.PIPE
        )
        self.assertEqual(process.returncode, 0)
        self.assertIn('check_systemd', process.stdout)


if __name__ == '__main__':
    unittest.main()
