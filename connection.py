import mysql.connector

def connection(db_path="Banco/DB.sql"):
    try:
        conn = mysql.connector.connect(
            host="localhost",
            user="root",
            password="admin",
            database="Documents"
        )
        return conn
    except mysql.connector.Error as err:
        print(f"Erro ao conectar ao banco de dados: {err}")
        return None

def close_connection(conn):
    if conn.is_connected():
        conn.close()
