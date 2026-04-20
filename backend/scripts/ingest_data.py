import pandas as pd
import psycopg2
from psycopg2 import extras
import os

# Database Connection
DB_PARAMS = {
    "dbname": os.getenv("DB_NAME", "bikestores"),
    "user": os.getenv("DB_USER", "postgres"),
    "password": os.getenv("DB_PASSWORD", "password"),
    "host": os.getenv("DB_HOST", "localhost"),
    "port": os.getenv("DB_PORT", "5432"),
}
DATA_DIR = "../data"  # Adjusted to match your VS Code explorer


def show_data_description():
    for file_name in os.listdir(DATA_DIR):
        if file_name.endswith(".csv"):
            table_name = file_name.replace(".csv", "")
            print(f"Table: {table_name}")
            df = pd.read_csv(os.path.join(DATA_DIR, file_name))
            print(df.head())
            print("-" * 40)


def load_csv_to_postgres():
    conn = psycopg2.connect(**DB_PARAMS)
    cur = conn.cursor()

    csv_files = [
        "brands.csv",
        "categories.csv",
        "stores.csv",
        "staffs.csv",
        "customers.csv",
        "products.csv",
        "stocks.csv",
        "orders.csv",
        "order_items.csv",
    ]

    for file_name in csv_files:
        table_name = file_name.replace(".csv", "")
        file_path = os.path.join(DATA_DIR, file_name)

        if not os.path.exists(file_path):
            continue

        print(f"Importing {table_name}...")

        # FIX 1: Read everything as strings to avoid "Integer out of range"
        df = pd.read_csv(file_path, dtype=str)

        # FIX 2: Replace Pandas NaN with Python None so Postgres gets actual NULLs
        df = df.where(pd.notnull(df), None)

        columns = ",".join(df.columns)
        values_template = ",".join(["%s"] * len(df.columns))
        insert_query = f"INSERT INTO {table_name} ({columns}) VALUES ({values_template}) ON CONFLICT DO NOTHING"

        # Execute
        extras.execute_batch(cur, insert_query, df.values)
        conn.commit()

    print("✅ All data loaded successfully!")
    cur.close()
    conn.close()


if __name__ == "__main__":
    show_data_description()
    load_csv_to_postgres()
