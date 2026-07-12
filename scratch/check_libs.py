import sqlite3
conn = sqlite3.connect('database/movies.db')
conn.row_factory = sqlite3.Row
cursor = conn.cursor()

# Libraries
cursor.execute("SELECT * FROM libraries")
libs = cursor.fetchall()
print("=== LIBRARIES ===")
for lib in libs:
    print(dict(lib))

# Movies per library
print("\n=== MOVIES PER LIBRARY ===")
cursor.execute("SELECT library_id, COUNT(*) as count FROM movies GROUP BY library_id")
for row in cursor.fetchall():
    print(dict(row))

# Total movies
cursor.execute("SELECT COUNT(*) FROM movies")
print(f"\nTotal movies: {cursor.fetchone()[0]}")

conn.close()
