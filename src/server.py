import typing as t
from .utils import run_shell_command


class Server:
    def __init__(self, server: str) -> None:
        self.server = server

    def copyLocalFile(self, local_file: str, remote_file: str) -> bool:
        """
        Copies local file to remote server

        :param local_file: Path to local file to be copied
        :param remote_file: Destination path for the remote file
        :return: bool
        """
        result, *_ = run_shell_command([
            '/usr/bin/scp',
            local_file,
            f'{self.server}:{remote_file}'
        ])

        return result == 0

    def runCommand(self, command: t.List[str]):
        """
        Executes remote command via SSH

        :param command: Command to execute on remote
        :return:
        """
        return run_shell_command([
            '/usr/bin/ssh',
            self.server,
            *command
        ])
