import os
import mysql.connector as my_sql


def get_mysql_connection():
    connection = my_sql.connect(
        host=os.environ.get('MYSQL_HOST'),
        port=os.environ.get('MYSQL_PORT'),
        user=os.environ.get('MYSQL_USER'),
        password=os.environ.get('MYSQL_PASSWORD'),
        database=os.environ.get('MYSQL_DB_NAME'),
    )
    return connection


def mysql_query(f):
    def wrapper(*args, **kwargs):
        conn = get_mysql_connection()
        cursor = conn.cursor()
        try:
            result = f(cursor, *args, **kwargs)
            conn.commit()
            return result
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            cursor.close()
            conn.close()
    return wrapper
