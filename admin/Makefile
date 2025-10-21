# Comando para formatear el código
format:
	poetry run black .
	poetry run isort .

# Comando para resetear la db con sus seeds 
reset:
	poetry run flask reset-db
	poetry run flask seed-db

# Comando para correr la app
run:
	poetry run python app.py

# Comando para verificar pip8
pip8: 
	poetry run flake8 .