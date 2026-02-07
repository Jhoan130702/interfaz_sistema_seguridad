import bcrypt
import mysql.connector
from mysql.connector import Error

class PasswordManager:
    def __init__(self, host='localhost', user='root', password='Jhoan', database='Sistema_seguridad'):
        self.host = host
        self.user = user
        self.password = password
        self.database = database

    def create_connection(self):
        """Crea una conexión a la base de datos MariaDB."""
        try:
            connection = mysql.connector.connect(
                host=self.host,
                user=self.user,
                password=self.password,
                database=self.database
            )
            return connection
        except Error as e:
            print(f"Error al conectar a la base de datos: {e}")
            return None

    def hash_password(self, password):
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
        return hashed.decode('utf-8'), salt.decode('utf-8')

    def save_user(self, id, cedula, username, apellidos, cargo, password, estado, correo):
        hashed_password, salt = self.hash_password(password)
        with self.create_connection() as conn:
            if conn is not None:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO usuario VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                ''', (id, cedula, username, apellidos, cargo, salt, hashed_password, estado, correo))
                conn.commit()

    def verify_password(self, username, password):
        with self.create_connection() as conn:
            if conn is not None:
                cursor = conn.cursor()
                cursor.execute('SELECT password, salt FROM users WHERE username = %s', (username,))
                result = cursor.fetchone()
                if result:
                    stored_hashed, _ = result
                    return bcrypt.checkpw(password.encode('utf-8'), stored_hashed.encode('utf-8'))
                return False

# Uso de la clase
if __name__ == "__main__":
    pm = PasswordManager(host='localhost', user='root', password='Jhoan', database='Sistema_seguridad')
    pm.save_user('ejem.id', 'ejem.cedula', 'usuario1', 'ejem.apellidos', 'ejem.cargo', 'mi_contraseña_secreta', 'ejem.estado', 'ejem.correo' )
    es_valido = pm.verify_password('usuario1', 'mi_contraseña_secreta')
    print(f'La contraseña es válida: {es_valido}')