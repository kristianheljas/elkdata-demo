import logging
import argparse
import typing as t
from .server import Server
from .log import print_info, print_warn
from .config import local_optimize_script_path, remote_optimize_script_path
from .utils import build_optimization_cmd, parse_optimizatation_output

# logging.basicConfig(level=logging.DEBUG)
log = logging.getLogger(__name__)

# region Command arguments
parser = argparse.ArgumentParser(description='Optimize MySQL databases across servers', prog='python -m src.main')
parser.add_argument('--file', metavar='<servers-file>', type=argparse.FileType('r', encoding='utf-8'),
                    help='file containing list of servers separated by newline')
parser.add_argument('--dry-run', action='store_true',
                    help='Simulate work to be done')
parser.add_argument('--filter', metavar='<pattern>', type=str, nargs='*', default=[],
                    help='Database name(s) and/or like pattern(s) (defaults to all databases)')

# endregion

if __name__ == '__main__':
    args = parser.parse_args()

    dry_run: bool = args.dry_run
    filters: t.List[str] = args.filter

    if dry_run:
        print_warn('--dry-run specified, simulating optimization')

    total_elapsed_ms = 0
    while server_name := args.file.readline():
        server_name = server_name.strip()

        # Blank lines are allowed
        if len(server_name) == 0:
            continue

        server = Server(server_name)

        print_info('\nProcessing server "{}"', server_name)

        if not server.copyLocalFile(local_optimize_script_path, remote_optimize_script_path):
            print_warn('Transferring optimization script failed, skipping server')
            continue

        # region Run optimizer
        optimization_cmd = build_optimization_cmd(dry_run, filters)
        exit_code, stdout, stderr = server.runCommand(optimization_cmd)
        if exit_code != 0:
            print_warn('Executing optimization script failed, skipping server')
            if stderr:
                print_warn('Message from server: {}', stderr)
            continue

        success_counter, fail_counter, database_elapsed_ms = parse_optimizatation_output(stdout)
        total_elapsed_ms += database_elapsed_ms
        # endregion

        print_info(
            '{}/{} tables optimized in "{}", took {:.3f} seconds',
            success_counter,
            success_counter + fail_counter,
            server_name,
            database_elapsed_ms / 1000
        )

        # region Remove optimization script
        exit_code, stdout, stderr = server.runCommand(['/usr/bin/rm', remote_optimize_script_path])
        if exit_code != 0:
            print_warn('Failed to remove optimization script from remote server')
            if stderr:
                print_warn('Message from server: {}', stderr)
        # endregion

    print_info('\nDONE! All optimizations completed in {:.3f} seconds', total_elapsed_ms / 1000)
