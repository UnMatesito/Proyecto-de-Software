# Tarea para formatear el código
format:
	poetry run black .
	poetry run isort .

env: 
	eval $(poetry env activate)

reset:
	flask reset-db
	flask seed-db
