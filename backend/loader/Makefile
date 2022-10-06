all:
	sparrow compose up -d db
	SPARROW_SECRET_KEY=test sparrow init
	poetry run python ./cache-database-map.py
	sparrow compose down