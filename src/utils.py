# src/utils.py
import pandas as pd
import mysql.connector
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

def connect_to_db():
    """
    Establishes a connection to the MySQL database.
    Returns the connection object.
    """
    try:
        connection = mysql.connector.connect(
            host=os.getenv('DB_HOST', 'localhost'),
            user=os.getenv('DB_USER', 'root'),
            password=os.getenv('DB_PASSWORD'),
            database=os.getenv('DB_NAME', 'gpu_dashboard')
        )
        return connection
    except mysql.connector.Error as err:
        print(f"Error connecting to database: {err}")
        return None

def carregar_dados():
    """
    Fetches all video card data from the database
    and loads it into a Pandas DataFrame.
    """
    print("Attempting to load data from MySQL...")
    conn = connect_to_db()
    
    if conn is None:
        print("Could not connect to DB. Returning empty DataFrame.")
        return pd.DataFrame() # Return an empty df if connection fails

    try:
        # This is our new "source of truth"
        query = "SELECT * FROM video_cards"
        
        # pd.read_sql is a powerful pandas function that
        # runs a query and returns a DataFrame all in one step.
        df = pd.read_sql(query, conn)
        
        print(f"Successfully loaded {len(df)} rows from database.")
        return df

    except Exception as e:
        print(f"Error reading data from database: {e}")
        return pd.DataFrame()
    finally:
        # Always close the connection
        if conn and conn.is_connected():
            conn.close()