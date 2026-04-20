import psycopg2
from sentence_transformers import SentenceTransformer
import pandas as pd

model = SentenceTransformer("all-MiniLM-L6-v2")


def update_product_embeddings():
    conn = psycopg2.connect(
        "dbname=bikestores user=postgres password=password host=localhost"
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
