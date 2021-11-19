#!/usr/bin/env bash

# Usage `bash optimize-database.sh [--dry-run] [database-or-like-pattern ...]`
# Output format: Check `print_status` function

# Arguments will be parsed later
DRY_RUN=0
DB_PATTERNS=""

# Ignore case when matching strings
shopt -s nocasematch

timestamp_ms() {
  date +%s%3N
}

mysql_query() {
  mysql -u root --skip-column-names --batch -e "$1" 2>&1
}

exit_fatal() {
  >&2 echo "$@"
  exit 1
}

print_status() {
  local status="$1" \
        database="$2" \
        table="$3" \
        elapsed_ms="$4" \
        message="$5"

  echo "$status,$database,$table,$elapsed_ms,$message"
}

process_table() {
  local database="$1" \
        table="$2"

    if [[ $DRY_RUN -eq 1 ]]; then
      echo "FAIL,$database,$table,0,Would have optimized table"
      return
    fi

    local start_ms=$(timestamp_ms)
    local result=$(mysql_query "OPTIMIZE TABLE \`$database\`.\`$table\`") \
          elapsed_ms=$(($(timestamp_ms) - $start_ms)) \
          status=$([[ $result =~ "error" ]] && echo 'FAIL' || echo 'SUCCESS')

    print_status "$status" "$database" "$table" $elapsed_ms
}

process_database() {
  local database="$1"

  local tables=$(mysql_query "SHOW TABLES FROM \`$database\`")

  if [[ -z $tables ]]; then
    print_status "FAIL" "$database" "" 0 "No tables found in database"
    continue
  fi

  for table in $tables; do
    process_table "$database" "$table"
  done
}

process_pattern() {
  local pattern="$1"

  # Expand possible DB_PATTERNS
  local databases=$(mysql_query "SHOW DATABASES LIKE '$pattern'")

  if [[ $databases =~ "error" ]]; then
    print_status "FAIL" $pattern "" 0 "Failed to expand pattern"
    return
  fi

  if [[ -z $databases ]]; then
    print_status "FAIL" $pattern "" 0 "No databases found by pattern"
    return
  fi

  for database in $databases; do
    process_database "$database"
  done
}

# If present, --dry-run must be the forst argument
if [ "$1" == "--dry-run" ]; then
  DRY_RUN=1
  shift
fi

DB_PATTERNS="$@"
# If databases or filters are not provided, assume all databases
if [[ $# -eq 0 ]]; then
  DB_PATTERNS=$(mysql_query "SHOW DATABASES")
  [[ $DB_PATTERNS =~ "error" ]] && exit_fatal "Listing databases failed!"
else
  DB_PATTERNS="$@"
fi

for DB_PATTERN in $DB_PATTERNS; do
  process_pattern "$DB_PATTERN"
done
