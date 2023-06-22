import os
import spotipy

from spotipy.oauth2 import SpotifyOAuth
from datetime import datetime, timedelta

import time

# Set up your Spotify API credentials
client_id = os.getenv("CLIENT_ID")
client_secret = os.getenv("CLIENT_SECRET")
redirect_uri = os.getenv("YOUR_REDIRECT_URI")

print(f"Client ID: {client_id}")
print(f"Client Secret: {client_secret}")
print(f"Redirect URI: {redirect_uri}")

# Create a Spotify API client
scope = "user-library-read playlist-modify-public"  # Add any additional scopes required
sp = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id=client_id, client_secret=client_secret, redirect_uri=redirect_uri, scope=scope))

# Get X number of recently liked tracks
max_tracks_per_request = 50
all_tracks = []
offset = 0
for i in range(0, 501, max_tracks_per_request):

    batch = sp.current_user_saved_tracks(limit=max_tracks_per_request, offset=offset)['items']
    all_tracks.extend(batch)
    offset += max_tracks_per_request

    time.sleep(1)

# Get liked songs in desired date range
current_date = datetime.now()
year = current_date.year
month = current_date.month

if month == 12:
    start_date = datetime(year, month, 1).strftime('%Y-%m-%d')
    end_date = datetime(year + 1, 1, 1).strftime('%Y-%m-%d')
else:
    start_date = datetime(year, month, 1).strftime('%Y-%m-%d')
    end_date = datetime(year, month + 1, 1).strftime('%Y-%m-%d')

recently_liked_songs = [
    track['track']['uri']
    for track in all_tracks
    if track['added_at'][:7] == f"{year}-{month:02}"
]

#check if playlist exists already
max_playlists_per_request = 50
existing_playlists = []
offset = 0
for i in range(0, 101, max_playlists_per_request):
    existing_playlists.extend(sp.current_user_playlists(limit=50, offset=offset))
    offset += max_playlists_per_request

date_look_up = {
    1: 'January',
    2: 'February',
    3: 'March',
    4: 'April',
    5: 'May',
    6: 'June',
    7: 'July',
    8: 'August',
    9: 'September',
    10: 'October',
    11: 'November',
    12: 'December'
}

playlist_name = date_look_up[month] + ' ' + str(year)
playlist_description = 'A playlist with songs liked/added in ' + date_look_up[month] + ' ' + str(year)

found = False
for playlist in existing_playlists['items']:
    if playlist['name'] == playlist_name:
        playlist_id = playlist['id']
        found = True
        break

if not found:
    new_playlist = sp.user_playlist_create(user=sp.me()['id'], name=playlist_name, public=True, description=playlist_description)
    playlist_id = new_playlist['id']

# add songs to playlist
existing_songs = sp.playlist_items(playlist_id=playlist_id, fields='items(track(uri))')['items']
existing_song_uris = [song['track']['uri'] for song in existing_songs]

filtered_songs = [song for song in recently_liked_songs if song not in existing_song_uris]

if len(filtered_songs) > 0:

    length = len(filtered_songs)
    cur = 0
    while cur < length:
        sp.playlist_add_items(playlist_id=playlist_id, items=filtered_songs[cur:cur + 100])
        cur += 100
    print("Songs added to the playlist.")
else:
    print("No new songs to add to the playlist.")