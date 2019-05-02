internal_name=/import/database-dump.pg-dump

until psql -h db -p 5432 -U postgres sparrow > /dev/null 2>&1 ; do
  echo "Waiting for database..."
  sleep 1
done

pg_restore -Fc -v -Upostgres $internal_name
