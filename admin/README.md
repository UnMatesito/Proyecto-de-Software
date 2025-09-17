# Grupo 09

## Para instalar dependencias
```bash
poetry install
```

## Para entrar en el entorno virtual
```bash
# Acceder a la carpeta de admin 
cd admin 

# y ejecutar
eval $(poetry env activate)
```

## Para iniciar el servidor
```bash
poetry run python app.py
```

## Para ejecutar tests
```bash
poetry run pytest
```

## Para linteo
Formateo y linteo
```bash
poetry run black .
```
Ordenar imports
```bash
poetry run isort .
```
Chequear cumplimiento con PEP8
```bash
poetry run flake8 --show-source .
```
Correr todo junto
```bash
poetry run black . ; poetry run isort . ; poetry run flake8 --show-source .
```

## Para configurar el .env
1. Hacer una copia del .env.example de la carpeta admin y renombrarla a .env
2. Rellenar los campos
3. Para rellenar el campo de SECRET_KEY, ejecutar lo siguiente y copiar el resultado
```py
python -c "import secrets;print(secrets.token_hex(32))"
```
5. Para rellenar el campo de la base de datos usar la siguiete plantilla y reemplazar los campos
- usuario
- contraseña
- host
- puerto
- nombre_db
```
postgresql://usuario:contraseña@host:puerto/nombre_db
```
6. Hacer una copia del .env.example de la carpeta docker y renombrarla a .env en esa misma carpeta
7. Para rellenar configuraciones de base de datos hay que completar los siguientes campos
- POSTGRES_USER
- POSTGRES_PASSWORD
- POSTGRES_DB
- PGADMIN_PASSWORD

## Info acceder a pgadmin y la base de datos
- Pgadmin: http://localhost:5050
- Usuario: admin@proyecto.com
- Contraseña: La que pongan en el .env de la carpeta docker en el campo PGADMIN_PASSWORD

- Host de la base de datos: db
- Puerto: 5432
- Usuario: El que pongan en el .env de la carpeta docker en el campo POST
- Contraseña: La que pongan en el .env de la carpeta docker en el campo POSTGRES_PASSWORD
- Nombre de la base de datos: El que pongan en el .env de la carpeta docker en el campo POSTGRES_DB
- Puerto de la base de datos: 5432