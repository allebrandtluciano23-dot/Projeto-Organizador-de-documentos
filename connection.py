import pymysql

def connect():
    print("Tentando conectar ao MySQL...")

    try:
        conn = pymysql.connect(
            host='localhost',
            user='root',
            password='admin',
            database='documents'
        )
        if conn.open:
            return conn

    except pymysql.MySQLError as e:
        print(f"Erro de conexão: {e}")
        
def closeConnection(conn):
    try:
        if conn:
            conn.close()
            print("Conexão fechada.")
    except pymysql.MySQLError as e:
        print(f"Erro ao fechar a conexão: {e}")
