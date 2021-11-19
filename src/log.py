import sys


def print_info(format_str: str, *args, **kwargs):
    sys.stdout.write(format_str.format(*args, **kwargs) + "\n")


def print_warn(format_str: str, *args, **kwargs):
    # Gotta figure out how to synchronize stderr and stdout, using stdout until then
    sys.stdout.write("[WARNING] " + format_str.format(*args, **kwargs) + "\n")
