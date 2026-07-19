import urllib.request
import json
import sys

sys.stdout.reconfigure(encoding='utf-8')
api_key = '3b229e9ff37295a937b9785313d105ac'

url = f"https://api.themoviedb.org/3/search/movie?api_key={api_key}&query=Seven&year=1995"
req = urllib.request.urlopen(url)
data = json.loads(req.read().decode('utf-8'))

print("TMDB Search Results for query 'Seven' in 1995:")
for item in data.get('results', []):
    print(f"ID: {item['id']}, Title: '{item['title']}', Original Title: '{item['original_title']}', Release Date: {item.get('release_date')}, Popularity: {item.get('popularity')}")
