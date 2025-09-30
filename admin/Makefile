# Tarea para formatear el código
format:
	poetry run black .
	poetry run isort .

env: 
	eval $(poetry env activate)

reset:
	poetry run flask reset-db
	poetry run flask seed-db

run:
	poetry run python app.py