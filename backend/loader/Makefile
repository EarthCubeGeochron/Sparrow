all:
	sparrow compose up -d db
	sparrow build backend
	SPARROW_SECRET_KEY=test sparrow init
	poetry run python ./cache-database-map.py
	sparrow compose down