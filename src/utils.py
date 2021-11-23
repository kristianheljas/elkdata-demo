import logging
import typing as t
from subprocess import Popen, PIPE

from .config import remote_optimize_script_path
from .log import print_warn

log = logging.getLogger(__name__)


def run_shell_command(command_with_args: t.Sequence[str]) -> t.Tuple[int, str, str]:
    """
    Run shell command locally

    :param command_with_args:
    :return:
    """
    log.info('Executing shell command %s', ' '.join(command_with_args))

    with Popen(command_with_args, stdout=PIPE, stderr=PIPE) as process:
        stdout, stderr = process.communicate()
        exit_code = process.wait()

    if exit_code != 0:
        log.info('Command exited with non-zero status')
        log.debug('- STDOUT: %s', str(stdout))
        log.debug('- STDERR: %s', str(stderr))

    return exit_code, stdout.decode("utf-8"), stderr.decode("utf-8")


def build_optimization_cmd(dry_run: bool = False, filters: t.List[str] = []) -> t.List[str]:
    """
    Generates optixmization command to be run on remote server

    :param dry_run:
    :param filters:
    :return:
    """
    optimization_cmd = ['/bin/bash', remote_optimize_script_path]

    if dry_run:
        optimization_cmd.append('--dry-run')

    if filters:
        optimization_cmd += filters

    return optimization_cmd


def parse_optimizatation_output(output: str) -> t.Tuple[int, int, int]:
    """
    Parse output from optimization script

    returns 3 integers:
    - success_counter (How many tables were optimized)
    - fail_counter (How many tables failed)
    - elapsed_ms (Time it took to optimize in milliseconds)
    """
    success_counter = 0
    fail_counter = 0
    total_elapsed_ms = 0
    for line in output.strip().split('\n'):
        status, database, table, elapsed_ms, message = line.split(',')
        total_elapsed_ms += int(elapsed_ms)

        if not table:  # Missing table name indicates issue with database argument
            print_warn('Failed to process "{}", message from server: {}', database, message)
        elif status == 'FAIL':
            fail_counter += 1
            log.debug('Table {}.{} optimized in {:.3f} ms', database, table, int(elapsed_ms) / 1000)
        elif status == 'SUCCESS':
            success_counter += 1
            log.debug('Table {}.{} optization failed in {:.3f} ms', database, table, int(elapsed_ms) / 1000)
        else:
            print_warn('Unexpected output from server: {}', line)

    return success_counter, fail_counter, total_elapsed_ms
