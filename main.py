import spotipy
from spotipy.oauth2 import SpotifyOAuth
import os

from bs4 import BeautifulSoup
import requests

CLIENT_ID = os.environ['E_CLIENT_ID']
CLIENT_SECRET = os.environ['E_CLIENT_SECRET']

date = input("'When' do you want to travel to? Enter the date as YYYY-MM-DD: ")

billboard_url = "https://www.billboard.com/charts/hot-100/"

response = requests.get(f"{billboard_url}{date}/")

soup = BeautifulSoup(response.text, "html.parser")

class_name = "c-title  a-no-trucate a-font-primary-bold-s u-letter-spacing-0021 lrv-u-font-size-18@tablet " \
             "lrv-u-font-size-16 u-line-height-125 u-line-height-normal@mobile-max a-truncate-ellipsis u-max-width-330 " \
             "u-max-width-230@tablet-only"

title_list = soup.find_all(name="li", class_="lrv-u-width-100p")

song_list = []

for title in title_list:
    try:
        song_name = title.find(name="h3").getText()
    except AttributeError:
        pass
    else:
        modified_song_name = song_name.replace("\n", "")
        song_list.append(modified_song_name.replace("\t", ""))

for song in song_list:
    print(song)

#Spotify Authentication
sp = spotipy.Spotify(
    auth_manager=SpotifyOAuth(
        scope="playlist-modify-private",
        redirect_uri="http://localhost:8888/callback",
        client_id=CLIENT_ID,
        client_secret=CLIENT_SECRET,
        show_dialog=True,
        cache_path="token.txt"
    )
)

user_id = sp.current_user()["id"]
print(user_id)

#Searching Spotify for songs by title
song_uris = []
year = date.split("-")[0]
for song in song_list:
    result = sp.search(q=f"track:{song} year:{year}", type="track")
    print(result)
    try:
        uri = result["tracks"]["items"][0]["uri"]
        song_uris.append(uri)
    except IndexError:
        print(f"{song} doesn't exist in Spotify. Skipped.")

# print(sp.search(q=f"track:{song_list[0]} year:{year}", type="track")["tracks"]["items"][0]["id"])

#Creating a new private playlist in Spotify
playlist = sp.user_playlist_create(user=user_id, name=f"{date} Billboard 100", public=False)
print(playlist)

#Adding songs found into the new playlist
sp.playlist_add_items(playlist_id=playlist["id"], items=song_uris)

