import os
import psycopg2
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

DB_PARAMS = {
    "dbname": os.getenv("DB_NAME"),
    "user": os.getenv("DB_USER"),
    "password": os.getenv("DB_PASSWORD"),
    "host": os.getenv("DB_HOST"),
    "port": os.getenv("DB_PORT"),
}


def create_schema():
    commands = [
        # 1. Base Tables (Parents)
        "CREATE TABLE IF NOT EXISTS brands (brand_id INT PRIMARY KEY, brand_name VARCHAR(255) NOT NULL);",
        "CREATE TABLE IF NOT EXISTS categories (category_id INT PRIMARY KEY, category_name VARCHAR(255) NOT NULL);",
        "CREATE TABLE IF NOT EXISTS stores (store_id INT PRIMARY KEY, store_name VARCHAR(255), phone VARCHAR(50), email VARCHAR(255), street VARCHAR(255), city VARCHAR(255), state VARCHAR(10), zip_code VARCHAR(10));",
        "CREATE TABLE IF NOT EXISTS customers (customer_id INT PRIMARY KEY, first_name VARCHAR(255), last_name VARCHAR(255), phone VARCHAR(50), email VARCHAR(255), street VARCHAR(255), city VARCHAR(255), state VARCHAR(10), zip_code VARCHAR(10));",
        # 2. Staffs (With corrected phone VARCHAR for your previous error)
        """CREATE TABLE IF NOT EXISTS staffs (
            staff_id INT PRIMARY KEY, 
            first_name VARCHAR(50), 
            last_name VARCHAR(50), 
            email VARCHAR(255) UNIQUE, 
            phone VARCHAR(50), 
            active INT, 
            store_id INT REFERENCES stores(store_id), 
            manager_id INT);""",
        # 3. Products (With Vector support)
        """CREATE TABLE IF NOT EXISTS products (
            product_id INT PRIMARY KEY, 
            product_name VARCHAR(255), 
            brand_id INT REFERENCES brands(brand_id), 
            category_id INT REFERENCES categories(category_id), 
            model_year INT, 
            list_price DECIMAL(10,2),
            description TEXT, 
            embedding vector(384));""",
        # 4. Indexes for Vector Search (HNSW is faster for large datasets)
        "CREATE INDEX IF NOT EXISTS product_embedding_idx ON products USING hnsw (embedding vector_cosine_ops);",
        # 5. Transactional Tables
        "CREATE TABLE IF NOT EXISTS stocks (store_id INT REFERENCES stores(store_id), product_id INT REFERENCES products(product_id), quantity INT, PRIMARY KEY (store_id, product_id));",
        """CREATE TABLE IF NOT EXISTS orders (
            order_id INT PRIMARY KEY, customer_id INT REFERENCES customers(customer_id), order_status INT, 
            order_date DATE, required_date DATE, shipped_date DATE, store_id INT REFERENCES stores(store_id), 
            staff_id INT REFERENCES staffs(staff_id));""",
        """CREATE TABLE IF NOT EXISTS order_items (
            order_id INT REFERENCES orders(order_id), item_id INT, product_id INT REFERENCES products(product_id), 
            quantity INT, list_price DECIMAL(10,2), discount DECIMAL(4,2), PRIMARY KEY (order_id, item_id));""",
    ]

    try:
        conn = psycopg2.connect(**DB_PARAMS)
        cur = conn.cursor()

        # Enable vector extension
        print("🔧 Enabling pgvector extension...")
        cur.execute("CREATE EXTENSION IF NOT EXISTS vector;")

        # Run table creation
        for cmd in commands:
            cur.execute(cmd)

        conn.commit()
        print("🚀 Schema created and Vector Index optimized successfully!")

    except Exception as e:
        print(f"❌ Error creating schema: {e}")
    finally:
        if conn:
            cur.close()
            conn.close()


def drop_all_tables():
    """Safety tool for development only"""
    try:
        conn = psycopg2.connect(**DB_PARAMS)
        cur = conn.cursor()
        cur.execute(
            "DROP TABLE IF EXISTS order_items, stocks, orders, products, staffs, customers, stores, categories, brands CASCADE;"
        )
        conn.commit()
        print("🧹 Database cleaned successfully!")
    except Exception as e:
        print(f"❌ Cleanup failed: {e}")
    finally:
        if conn:
            cur.close()
            conn.close()


if __name__ == "__main__":
    # In professional projects, we usually check an arg to decide whether to drop
    # For now, just run create_schema
    create_schema()
