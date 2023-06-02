import psycopg2
from config.config import dbconfig

def connect():
    try:
        conn = psycopg2.connect(
            database=dbconfig['database'],
            user=dbconfig['username'],
            password=dbconfig['password'],
            host=dbconfig['hostname'],
            port=dbconfig['port'])
        cur = conn.cursor()
        return conn, cur
    except psycopg2.Error as error:
        print(error)
