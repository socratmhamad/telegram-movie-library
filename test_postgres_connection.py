import os
import pg8000
import urllib.parse
import ssl

def test_pg8000():
    database_url = os.environ.get("DATABASE_URL")
    print("Testing pg8000 connection...")
    
    parsed = urllib.parse.urlparse(database_url)
    
    try:
        ssl_context = ssl.create_default_context()
        ssl_context.check_hostname = False
        ssl_context.verify_mode = ssl.CERT_NONE
        
        conn = pg8000.connect(
            user=parsed.username,
            password=parsed.password,
            host=parsed.hostname,
            port=parsed.port or 5432,
            database=parsed.path.lstrip('/'),
            ssl_context=ssl_context,
            timeout=10
        )
        cur = conn.cursor()
        cur.execute("SELECT 1;")
        res = cur.fetchone()
        print(f"pg8000 success! SELECT 1 returned: {res[0]}")
        conn.close()
    except Exception as e:
        print(f"pg8000 failed: {type(e).__name__}: {e}")

if __name__ == '__main__':
    test_pg8000()
