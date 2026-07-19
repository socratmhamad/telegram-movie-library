import sqlite3

conn = sqlite3.connect('database/movies.db')
cursor = conn.cursor()

# Get the two movie IDs
from_movie_id = 5287  # Seven (1995) - incorrect link
to_movie_id = 14495   # Se7en 1995 - correct link

print(f"Merging Movie ID {from_movie_id} into Movie ID {to_movie_id}...")

# Check messages for from_movie
cursor.execute("SELECT id, message_id FROM telegram_messages WHERE movie_id = ?", (from_movie_id,))
from_messages = cursor.fetchall()
print(f"Messages for incorrect Seven (Movie ID {from_movie_id}): {from_messages}")

# Check messages for to_movie
cursor.execute("SELECT id, message_id FROM telegram_messages WHERE movie_id = ?", (to_movie_id,))
to_messages = cursor.fetchall()
print(f"Messages for correct Se7en (Movie ID {to_movie_id}): {to_messages}")

# Update the telegram_messages: move them to to_movie_id
for msg_id_pk, msg_id in from_messages:
    # Avoid duplicate message_id under the same movie if any
    cursor.execute("SELECT id FROM telegram_messages WHERE movie_id = ? AND message_id = ?", (to_movie_id, msg_id))
    existing = cursor.fetchone()
    if existing:
        print(f"  Message {msg_id} already exists on target movie, deleting duplicate message record...")
        cursor.execute("DELETE FROM telegram_messages WHERE id = ?", (msg_id_pk,))
    else:
        print(f"  Moving message {msg_id} to target movie...")
        cursor.execute("UPDATE telegram_messages SET movie_id = ? WHERE id = ?", (to_movie_id, msg_id_pk))

# Now delete the duplicate movie record (from_movie_id)
cursor.execute("DELETE FROM movies WHERE id = ?", (from_movie_id,))
print(f"Deleted duplicate Movie ID {from_movie_id} from movies table.")

conn.commit()
print("SUCCESS: Merge and deletion committed successfully!")

conn.close()
