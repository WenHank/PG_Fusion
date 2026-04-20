from fastapi import FastAPI, HTTPException
import psycopg2
from psycopg2.extras import RealDictCursor
import time

app = FastAPI(title="PG-Fusion API")

# Database configuration (Matches your Docker setup)
DB_PARAMS = {
    "dbname": "bikestores",
    "user": "postgres",
    "password": "password",
    "host": "localhost",  # Use 'db' if connecting from another container, 'localhost' if running locally
    "port": "5432",
}


@app.get("/")
def read_root():
    return {"message": "Welcome to PG-Fusion API", "status": "online"}


@app.get("/health")
def health_check():
    """
    Checks if the PostgreSQL database is reachable.
    """
    try:
        # Try to connect and execute a simple query
        conn = psycopg2.connect(**DB_PARAMS)
        cur = conn.cursor()
        cur.execute("SELECT 1;")
        cur.close()
        conn.close()
        return {"status": "healthy", "database": "connected", "timestamp": time.time()}
    except Exception as e:
        # If connection fails, return 503 Service Unavailable
        raise HTTPException(
            status_code=503, detail=f"Database connection failed: {str(e)}"
        )


@app.get("/db-stats")
def get_db_stats():
    try:
        conn = psycopg2.connect(**DB_PARAMS)
        cur = conn.cursor(cursor_factory=RealDictCursor)

        cur.execute(
            "SELECT (SELECT count(*) FROM products) as product_count, (SELECT count(*) FROM categories) as category_count;"
        )
        stats = cur.fetchone()

        cur.close()
        conn.close()
        return {"status": "success", "data": stats}
    except Exception as e:
        return {"status": "error", "message": str(e)}


@app.post("/v1/search")
def hybrid_search(query: str, max_price: float = 100000):
    # 1. 將使用者的問題轉成向量
    query_vector = model.encode(query).tolist()

    with Session(engine) as session:
        # 2. 執行 Hybrid Search SQL
        # <=> 代表餘弦距離 (Cosine Distance)
        sql = """
            SELECT product_name, list_price, description 
            FROM products 
            WHERE list_price <= :price 
            ORDER BY embedding <=> :vector::vector
            LIMIT 5
        """
        results = session.execute(
            text(sql), {"price": max_price, "vector": str(query_vector)}
        ).fetchall()

        return results


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
