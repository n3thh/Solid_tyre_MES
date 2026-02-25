import psycopg2
from psycopg2 import pool
import logging

# =================================================
# CONFIGURATION
# =================================================
# CHANGE THIS to your Ubuntu Server's IP Address!
DB_HOST = "192.168.0.141"  
DB_NAME = "tyre_factory_db"
DB_USER = "postgres"
DB_PASS = "factory123"      # The password you set in Step 1

class DBManager:
    _connection_pool = None

    @staticmethod
    def initialize():
        """Creates a pool of connections to the database for efficiency."""
        if DBManager._connection_pool is None:
            try:
                DBManager._connection_pool = psycopg2.pool.SimpleConnectionPool(
                    1, 10, # Min 1 connection, Max 10 connections
                    user=DB_USER,
                    password=DB_PASS,
                    host=DB_HOST,
                    port="5432",
                    database=DB_NAME
                )
                print(f"✅ Connected to Database at {DB_HOST}")
            except (Exception, psycopg2.DatabaseError) as error:
                print(f"❌ Error connecting to database: {error}")
                return False
        return True

    @staticmethod
    def get_connection():
        """Gets a connection from the pool."""
        if DBManager._connection_pool is None:
            if not DBManager.initialize(): return None
        return DBManager._connection_pool.getconn()

    @staticmethod
    def return_connection(conn):
        """Returns the connection back to the pool so others can use it."""
        if DBManager._connection_pool and conn:
            DBManager._connection_pool.putconn(conn)

    @staticmethod
    def execute_query(query, params=None):
        """Executes INSERT, UPDATE, DELETE queries (No return data)."""
        conn = DBManager.get_connection()
        if not conn: return False
        
        try:
            cursor = conn.cursor()
            cursor.execute(query, params)
            conn.commit() # Save changes
            cursor.close()
            return True
        except (Exception, psycopg2.DatabaseError) as error:
            print(f"SQL Error: {error}")
            conn.rollback() # Undo changes if error
            return False
        finally:
            DBManager.return_connection(conn)

    @staticmethod
    def fetch_data(query, params=None):
        """Executes SELECT queries (Returns data)."""
        conn = DBManager.get_connection()
        if not conn: return None
        
        result = []
        try:
            cursor = conn.cursor()
            cursor.execute(query, params)
            result = cursor.fetchall()
            cursor.close()
        except (Exception, psycopg2.DatabaseError) as error:
            print(f"SQL Error: {error}")
        finally:
            DBManager.return_connection(conn)
            
        return result

# AUTO-INITIALIZE ON IMPORT
DBManager.initialize()