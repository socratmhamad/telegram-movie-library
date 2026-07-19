import sqlite3

conn = sqlite3.connect('database/movies.db')
cursor = conn.cursor()

# Get the primary key (id) of Se7en (TMDB ID 807) in tmdb_movies
cursor.execute("SELECT id, title FROM tmdb_movies WHERE tmdb_id = 807")
tmdb_record = cursor.fetchone()

if tmdb_record:
    tmdb_pk = tmdb_record[0]
    print(f"Found Se7en (TMDB ID 807) in tmdb_movies with PK={tmdb_pk}")
    
    # Check current state of Seven (1995) movie (Movie ID 5287)
    cursor.execute("SELECT id, title, tmdb_movie_id FROM movies WHERE id = 5287")
    movie_record = cursor.fetchone()
    
    if movie_record:
        print(f"Current link for Movie ID 5287 ('{movie_record[1]}'): tmdb_movie_id={movie_record[2]}")
        
        # Perform the update
        cursor.execute("UPDATE movies SET tmdb_movie_id = ? WHERE id = 5287", (tmdb_pk,))
        conn.commit()
        
        # Verify the update
        cursor.execute("SELECT id, title, tmdb_movie_id FROM movies WHERE id = 5287")
        updated_record = cursor.fetchone()
        print(f"SUCCESS: Updated Movie ID 5287 to tmdb_movie_id={updated_record[2]}")
    else:
        print("ERROR: Movie ID 5287 not found in movies table.")
else:
    print("ERROR: Se7en (TMDB ID 807) not found in tmdb_movies table.")

conn.close()
