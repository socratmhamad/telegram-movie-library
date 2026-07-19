import sqlite3
import sys

# Force UTF-8 stdout
sys.stdout.reconfigure(encoding='utf-8')

conn = sqlite3.connect('database/movies.db')
cursor = conn.cursor()

# Search for the movie
cursor.execute("""
    SELECT id, library_id, title, tmdb_movie_id 
    FROM movies 
    WHERE title LIKE '%seven%' 
       OR title LIKE '%se7en%' 
       OR title LIKE '%sevn%'
       OR title LIKE '%sevens%'
""")
movies_found = cursor.fetchall()
print("Movies found in database:")
for m in movies_found:
    print(f"Movie ID: {m[0]}, Library ID: {m[1]}, Title: '{m[2]}', TMDB Movie ID (PK of tmdb_movies): {m[3]}")
    if m[3]:
        cursor.execute("SELECT tmdb_id, title, original_title, release_date, poster_path, backdrop_path, genres FROM tmdb_movies WHERE id = ?", (m[3],))
        tmdb_data = cursor.fetchone()
        if tmdb_data:
            print(f"  TMDB ID: {tmdb_data[0]}, TMDB Title: '{tmdb_data[1]}', Original Title: '{tmdb_data[2]}', Release Date: {tmdb_data[3]}")
            print(f"  Poster Path: {tmdb_data[4]}, Backdrop Path: {tmdb_data[5]}")

conn.close()
