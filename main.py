import os
import spotipy

from spotipy.oauth2 import SpotifyOAuth
from datetime import datetime, timedelta

import time

# Set up your Spotify API credentials
client_id = os.getenv("CLIENT_ID")
client_secret = os.getenv("CLIENT_SECRET")
redirect_uri = os.getenv('YOUR_REDIRECT_URI')

print(f"Client ID: {client_id}")
print(f"Client Secret: {client_secret}")
print(f"Redirect URI: {redirect_uri}")

# Create a Spotify API client
scope = "user-library-read playlist-modify-public"  # Add any additional scopes required
sp = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id=client_id, client_secret=client_secret, redirect_uri=redirect_uri, scope=scope))

# Get the current year and month
current_date = datetime.now()
year = current_date.year
month = current_date.month

# Calculate the start and end dates for the current month
if month == 12:
    start_date = datetime(year, month, 1).strftime('%Y-%m-%d')
    end_date = datetime(year + 1, 1, 1).strftime('%Y-%m-%d')
else:
    start_date = datetime(year, month, 1).strftime('%Y-%m-%d')
    end_date = datetime(year, month + 1, 1).strftime('%Y-%m-%d')

print(start_date)
print(end_date)

# Maximum number of tracks to retrieve per request
max_tracks_per_request = 50

# Initialize an empty list to store all the tracks
all_tracks = []

# Retrieve the tracks in batches EVENTUALLY NEED TO ALLOW USER TO INPUT NUMBER OF LIKED TRACKS
offset = 0
while len(all_tracks) < 10000: #month user inputs *200 eventually
    # Retrieve the next batch of tracks
    batch = sp.current_user_saved_tracks(limit=max_tracks_per_request, offset=offset)['items']
    
    # Append the tracks to the list
    all_tracks.extend(batch)
    
    # Update the offset for the next batch
    offset += max_tracks_per_request
    
    # Break the loop if there are no more tracks to retrieve
    if len(batch) < max_tracks_per_request:
        break

    time.sleep(1)

# Filter the recently liked songs based on the retrieved tracks
recently_liked_songs = [
    track['track']['uri']
    for track in all_tracks
    if track['added_at'][:7] == f"{year}-{month:02}"
]

#check if playlist exists already
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
existing_playlists = sp.current_user_playlists(limit=50)

found = False
for playlist in existing_playlists['items']:
    if playlist['name'] == playlist_name:
        playlist_id = playlist['id']
        found = True
        break

if not found:
    new_playlist = sp.user_playlist_create(user=sp.me()['id'], name=playlist_name, public=True, description=playlist_description)
    playlist_id = new_playlist['id']

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