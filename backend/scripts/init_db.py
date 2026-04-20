import psycopg2

DB_PARAMS = "dbname=bikestores user=postgres password=password host=localhost port=5432"


def create_schema():
    commands = [
        # 1. Base Tables (Parents)
        "CREATE TABLE IF NOT EXISTS brands (brand_id INT PRIMARY KEY, brand_name VARCHAR(255) NOT NULL);",
        "CREATE TABLE IF NOT EXISTS categories (category_id INT PRIMARY KEY, category_name VARCHAR(255) NOT NULL);",
        "CREATE TABLE IF NOT EXISTS stores (store_id INT PRIMARY KEY, store_name VARCHAR(255), phone VARCHAR(25), email VARCHAR(255), street VARCHAR(255), city VARCHAR(255), state VARCHAR(10), zip_code VARCHAR(5));",
        "CREATE TABLE IF NOT EXISTS customers (customer_id INT PRIMARY KEY, first_name VARCHAR(255), last_name VARCHAR(255), phone VARCHAR(25), email VARCHAR(255), street VARCHAR(255), city VARCHAR(255), state VARCHAR(10), zip_code VARCHAR(5));",
        # 2. Tables with Foreign Keys (Children)
        """CREATE TABLE IF NOT EXISTS staffs (
            staff_id INT PRIMARY KEY, first_name VARCHAR(50), last_name VARCHAR(50), 
            email VARCHAR(255) UNIQUE, phone VARCHAR(25), active INT, store_id INT REFERENCES stores(store_id), 
            manager_id INT);""",
        """CREATE TABLE IF NOT EXISTS products (
            product_id INT PRIMARY KEY, product_name VARCHAR(255), brand_id INT REFERENCES brands(brand_id), 
            category_id INT REFERENCES categories(category_id), model_year INT, list_price DECIMAL(10,2),
            description TEXT, embedding vector(384));""",  # Added AI columns
        "CREATE TABLE IF NOT EXISTS stocks (store_id INT REFERENCES stores(store_id), product_id INT REFERENCES products(product_id), quantity INT, PRIMARY KEY (store_id, product_id));",
        """CREATE TABLE IF NOT EXISTS orders (
            order_id INT PRIMARY KEY, customer_id INT REFERENCES customers(customer_id), order_status INT, 
            order_date DATE, required_date DATE, shipped_date DATE, store_id INT REFERENCES stores(store_id), 
            staff_id INT REFERENCES staffs(staff_id));""",
        """CREATE TABLE IF NOT EXISTS order_items (
            order_id INT REFERENCES orders(order_id), item_id INT, product_id INT REFERENCES products(product_id), 
            quantity INT, list_price DECIMAL(10,2), discount DECIMAL(4,2), PRIMARY KEY (order_id, item_id));""",
    ]

    conn = psycopg2.connect(DB_PARAMS)
    cur = conn.cursor()
    # Enable vector extension first
    cur.execute("CREATE EXTENSION IF NOT EXISTS vector;")
    for cmd in commands:
        cur.execute(cmd)
    conn.commit()
    print("🚀 Schema created successfully!")


def quick_command():
    conn = psycopg2.connect(DB_PARAMS)
    cur = conn.cursor()
    cur.execute(
        "DROP TABLE IF EXISTS order_items, stocks, orders, products, staffs, customers, stores, categories, brands CASCADE;"
    )
    print("🧹 All tables dropped successfully!")
    cur.close()
    conn.close()


if __name__ == "__main__":
    create_schema()
