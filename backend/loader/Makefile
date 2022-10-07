all:
	sparrow compose up -d db
	sparrow build backend
	SPARROW_SECRET_KEY=test sparrow init
	poetry run python ./cache-database-map.py
	sparrow compose down

test:
	poetry run pytest -W ignore

show-schemas:
	poetry run python -W ignore -c "from sparrow.loader import show_loader_schemas; show_loader_schemas()"