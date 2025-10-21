import psycopg2
from psycopg2.extras import RealDictCursor

# Conexión a la base de datos
conn = psycopg2.connect(
    dbname="proyecto",
    user="proyecto_user",
    password="123456",
    host="localhost",
    port=5432
)

# Crear un cursor
cur = conn.cursor()

# Obtener todos los usuarios
cur.execute('SELECT * FROM "user";')
users = cur.fetchall()
print(users)

# Obtener un usuario por su ID
cur.execute('SELECT * FROM "user" WHERE id = %s;', (1,))
user = cur.fetchone()
print(user)

# Obtener un usuario por su email
cur.execute('SELECT * FROM "user" WHERE email = %s;', ('admin@sistema.com',))
user = cur.fetchone()
print(user)

# Cerrar conexión
cur.close()
conn.close()
