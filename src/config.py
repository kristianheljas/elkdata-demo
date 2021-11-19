from os import path

optimize_script_name = 'optimize-databases.sh'
local_optimize_script_path = path.realpath(path.join(path.dirname(__file__), '../scripts', optimize_script_name))
remote_optimize_script_path = path.join('/tmp', optimize_script_name)
