# Database optimization tool

```
usage: python -m src.main [--file <servers-file>] [--dry-run] [--filter [<pattern> ...]]

Optimize MySQL databases across servers

optional arguments:
  --file <servers-file>    file containing list of servers separated by newline
  --dry-run                Simulate work to be done
  --filter [<pattern> ...] Database name(s) and/or like pattern(s) (defaults to all databases)
```

## Defining servers

Servers file should contain newline separated list of server addresses, for example:

```
mysql-1.example.com
mysql-2.example.com
```

> For visual grouping empty lines are allowed

## Example output

```
> python -m src.main --file servers.txt --filter "test_schema" "empty_schema" "not_found" "invalid\'pattern"

Processing server "mysql-1.localhost"
[WARNING] Failed to process "empty_schema", message from server: No tables found in database
[WARNING] Failed to process "not_found", message from server: No databases found by pattern
[WARNING] Failed to process "invalid'pattern", message from server: Failed to expand pattern
2/2 tables optimized in "mysql-1.localhost", took 0.731 seconds

Processing server "mysql-2.localhost"
[WARNING] Failed to process "empty_schema", message from server: No tables found in database
[WARNING] Failed to process "not_found", message from server: No databases found by pattern
[WARNING] Failed to process "invalid'pattern", message from server: Failed to expand pattern
2/2 tables optimized in "mysql-2.localhost", took 0.595 seconds

DONE! All optimizations completed in 1.326 seconds
```