import os
import psycopg2
import time
from psycopg2.extras import execute_batch


def get_db_connection(max_retries=5, retry_delay=2):
    """Establishes a connection to the PostgreSQL database with retry logic."""
    for attempt in range(max_retries):
        try:
            conn = psycopg2.connect(
                host=os.getenv("DB_HOST", "localhost"),
                dbname=os.getenv("POSTGRES_DB", "bellaterra_db"),
                user=os.getenv("POSTGRES_USER", "bellaterra"),
                password=os.getenv("POSTGRES_PASSWORD", "password"),
                port=os.getenv("DB_PORT", "5432")
            )
            print(f"Successfully connected to database on attempt {attempt + 1}")
            return conn
        except psycopg2.OperationalError as e:
            print(f"Attempt {attempt + 1}/{max_retries}: Error connecting to the database: {e}")
            if attempt < max_retries - 1:
                wait_time = retry_delay * (2 ** attempt)  # Exponential backoff
                print(f"Retrying in {wait_time} seconds...")
                time.sleep(wait_time)
            else:
                print("Max retries reached. Could not connect to database.")
                return None


def create_tables(conn):
    """Creates database tables from the schema.sql file."""
    with conn.cursor() as cur:
        with open("database/schema.sql", "r") as f:
            cur.execute(f.read())
    conn.commit()
    print("Tables created successfully.")


def insert_menu_items(conn, items):
    """Inserts a list of menu items into the database."""
    import json
    
    query = """
    INSERT INTO menu_items (name, description, price, category, is_vegetarian, is_vegan, is_gluten_free, properties)
    VALUES (%(name)s, %(description)s, %(price)s, %(category)s, %(is_vegetarian)s, %(is_vegan)s, %(is_gluten_free)s, %(properties)s)
    ON CONFLICT (name) DO UPDATE SET
        description = EXCLUDED.description,
        price = EXCLUDED.price,
        category = EXCLUDED.category,
        is_vegetarian = EXCLUDED.is_vegetarian,
        is_vegan = EXCLUDED.is_vegan,
        is_gluten_free = EXCLUDED.is_gluten_free,
        properties = EXCLUDED.properties;
    """
    with conn.cursor() as cur:
        # Convert properties dict to JSON string for insertion
        for item in items:
            item['properties'] = json.dumps(item['properties'])
        
        execute_batch(cur, query, items)
    conn.commit()
    print(f"Inserted {len(items)} items into the database.") 