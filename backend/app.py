import os
from fastapi import FastAPI, HTTPException
import psycopg2
from psycopg2.extras import RealDictCursor
import time
from sqlalchemy import text
from sqlalchemy.orm import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sentence_transformers import SentenceTransformer

from api_schema import SearchRequest

app = FastAPI(title="PG-Fusion API")

model = SentenceTransformer("all-MiniLM-L6-v2")

# 1. Configuration from Environment Variables
DB_PARAMS = {
    "dbname": os.getenv("DB_NAME", "bikestores"),
    "user": os.getenv("DB_USER", "postgres"),
    "password": os.getenv("DB_PASSWORD", "password"),
    "host": os.getenv("DB_HOST", "127.0.0.1"),  # Changed to 127.0.0.1 for stability
    "port": os.getenv("DB_PORT", "5432"),
}


def get_engine():
    """Constructs the URL and creates the SQLAlchemy engine."""
    url = f"postgresql://{DB_PARAMS['user']}:{DB_PARAMS['password']}@{DB_PARAMS['host']}:{DB_PARAMS['port']}/{DB_PARAMS['dbname']}"
    return create_engine(url)


# 2. Initialize the engine once globally
engine = get_engine()

# 3. Create a SessionLocal class for dependency injection
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


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


@app.post("/v1/compare-search")
def compare_search(request: SearchRequest):
    query = request.query
    max_price = request.max_price
    print(f"Received search query: '{query}' with max price: {max_price}")

    # FIX: Removed the brackets
    query_vector = model.encode(query).tolist()

    with Session(engine) as session:
        # FTS Search
        fts_sql = """
            SELECT product_name, list_price, 'Full-Text Search' as method
            FROM products 
            WHERE list_price <= :price 
            AND (to_tsvector('english', product_name) @@ plainto_tsquery('english', :query))
            LIMIT 5
        """
        fts_results = session.execute(
            text(fts_sql), {"price": max_price, "query": query}
        ).fetchall()

        # Vector Search
        # FIX: Removed the brackets
        vector_sql = """
            SELECT product_name, list_price, 'Vector Search' as method
            FROM products 
            WHERE list_price <= :price 
            ORDER BY embedding <=> CAST(:vector AS vector)
            LIMIT 5
        """
        vector_results = session.execute(
            text(vector_sql),
            {
                "price": max_price,
                "vector": str(
                    query_vector
                ),  # Ensure this matches the variable name in SQL
            },
        ).fetchall()

        # 2. Execute FTS
        fts_raw = session.execute(
            text(fts_sql), {"price": max_price, "query": query}
        ).fetchall()
        # Convert to list of dicts
        fts_results = [dict(row._mapping) for row in fts_raw]

        # 3. Execute Vector Search
        vector_raw = session.execute(
            text(vector_sql), {"price": max_price, "vector": str(query_vector)}
        ).fetchall()
        # Convert to list of dicts
        vector_results = [dict(row._mapping) for row in vector_raw]

        # 4. Return
        return {
            "query": query,
            "fts_results": fts_results,
            "vector_results": vector_results,
        }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
