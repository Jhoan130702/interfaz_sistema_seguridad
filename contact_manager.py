# Aplicacion de CRUD con Flet y SQLite
# @autor: Magno Efren
# Youtube: https://www.youtube.com/c/MagnoEfren

import sqlite3

class ContactManager:
    def __init__(self):
        self.connection = sqlite3.connect("data.db",check_same_thread=False)

    def add_contact(self, name, age, email, phone):
        # Crear la tabla si no existe
        create_table_query = '''CREATE TABLE IF NOT EXISTS datos (ID INTEGER PRIMARY KEY AUTOINCREMENT, NOMBRE TEXT, EDAD INTEGER, CORREO TEXT, TELEFONO TEXT)'''
        self.connection.execute(create_table_query)

        # Insertar datos en la tabla
        insert_query = '''INSERT INTO datos (NOMBRE, EDAD, CORREO, TELEFONO) VALUES (?, ?, ?, ?)'''
        self.connection.execute(insert_query, (name, age, email, phone))
        self.connection.commit()

    def get_contacts(self):
        cursor = self.connection.cursor()
        query = "SELECT * FROM datos"
        cursor.execute(query)
        contacts = cursor.fetchall()
        return contacts

    def delete_contact(self, name):
        query = "DELETE FROM datos WHERE NOMBRE = ?"
        self.connection.execute(query, (name,))
        self.connection.commit()

    def update_contact(self, contact_id, name, age, email, phone):
        query = '''UPDATE datos SET NOMBRE = ?, EDAD = ?, CORREO = ?, TELEFONO = ? WHERE ID = ?'''
        self.connection.execute(query, (name, age, email, phone, contact_id))
        self.connection.commit()
        #return self.connection.total_changes

    def close_connection(self):
        self.connection.close()
        print("cerrar")
