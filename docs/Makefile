all: output/schema.html

output:
	mkdir -p $@

output/schema.html: ../backend/sparrow/sql/02-create-tables.sql | sql-to-markdown output
	cat $^ \
	| ./sql-to-markdown \
	| pandoc --standalone -f markdown -o $@
