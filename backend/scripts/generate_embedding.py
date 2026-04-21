import os
import psycopg2
from sentence_transformers import SentenceTransformer
import pandas as pd

model = SentenceTransformer("all-MiniLM-L6-v2")

DB_PARAMS = {
    "dbname": os.getenv("DB_NAME", "bikestores"),
    "user": os.getenv("DB_USER", "postgres"),
    "password": os.getenv("DB_PASSWORD", "password"),
    "host": os.getenv("DB_HOST", "localhost"),
    "port": os.getenv("DB_PORT", "5432"),
}


def update_product_embeddings():
    conn = psycopg2.connect(
        f"dbname={DB_PARAMS['dbname']} user={DB_PARAMS['user']} password={DB_PARAMS['password']} host={DB_PARAMS['host']} port={DB_PARAMS['port']}"
    )
    cur = conn.cursor()

    cur.execute("SELECT product_id, product_name, description FROM products")
    rows = cur.fetchall()

    for pid, name, desc in rows:
        text_to_embed = f"{name}. {desc if desc else ''}"

        embedding = model.encode(text_to_embed).tolist()

        cur.execute(
            "UPDATE products SET embedding = %s WHERE product_id = %s", (embedding, pid)
        )

    conn.commit()
    print("✅ All products have been vectorized!")
    cur.close()
    conn.close()


if __name__ == "__main__":
    update_product_embeddings()
