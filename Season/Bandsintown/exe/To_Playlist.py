# %% MODULES
import os
from dotenv import load_dotenv
import secrets
import requests
from urllib.parse import urlencode
from datetime import datetime, timedelta
import json
import pandas as pd
from logging import error
from Auth_Followlist import rw_tokens, get_follow_dict
from glob import glob

# %% VARIABLES
working_directory = os.getcwd()
parent_dir = os.path.dirname(working_directory)
data_dir = os.path.join(working_directory, 'data')
data_long = os.path.join(data_dir, 'long')
data_short = os.path.join(data_dir, 'short')
tokens_json = os.path.join(data_dir, 'tokens_mutta.json')

spotify_redirect_uri = 'https://open.spotify.com/intl-it'

paths = {
    'parent': parent_dir,
    'data_dir': {
        'data': data_dir,
        'long': data_long,
        'short': data_short,
    },
}

SPOTIFY_API_ENDPOINTS = {
    'authorize': 'https://accounts.spotify.com/authorize',
    'token': 'https://accounts.spotify.com/api/token',
    'artist': 'https://api.spotify.com/v1/artists',
    'me': 'https://api.spotify.com/v1/me',
    'users': 'https://api.spotify.com/v1/users',
    'playlists': 'https://api.spotify.com/v1/playlists'
}

limit = 50

tokens_dict = {}

env_path = os.path.join(paths['parent'], '.env')
load_dotenv(env_path)
spotify_client_id = os.getenv('SPOTIFY_CLIENT_ID')
spotify_client_secret = os.getenv('SPOTIFY_CLIENT_SECRET')

# %% FUNCTIONS
def get_artist_albums(artist_id, token):

    headers = {
        'Authorization': 'Bearer ' + token
    }
    params = {
        'limit': limit,
        'market': 'IT',
        'include_groups': 'album'
    }

    url = f'{SPOTIFY_API_ENDPOINTS['artist']}/{artist_id}/albums'
    response = requests.get(url, params=urlencode(params), headers=headers)
    if response.status_code == 200:
        print(f'Success! -> Response {response.status_code}\n')
    data = response.json()

    print(f'Found {len(data['items'])} elements (note that only FULL albums are included):')
    for item in data['items']:
        print(f'\t- {item['name']} ({item['release_date'][:4]})')

    return data['items']

def get_profile(token):
    headers = {
        'Authorization': 'Bearer ' + token
    }

    profile = requests.get(SPOTIFY_API_ENDPOINTS['me'], headers=headers)
    if profile.status_code == 200:
        id = profile.json()['id']
        name = profile.json()['display_name']
        print(f'\nObtained id for \'{name}\': \'{id}\'\n')
    else:
        print(f'\nError {profile.status_code}: {profile.json()}\n')
        id = None

    return id

def public_playlist(user_id, token):

    headers = {
        'Authorization': 'Bearer ' + token,
        'Content-Type': 'application/json'
    }

    name = input('Choose a name for the playlist: ')
    description = input(f'Choose a description for the playlist \'{name}\': ')
    public = input('Do you want the playlist to be public? (Y/N): ')
    payload = {
        'name': name,
        'description': description,
        'public': True if public.lower() == 'y' else False
    }

    url = f'{SPOTIFY_API_ENDPOINTS['users']}/{user_id}/playlists'
    response = requests.post(url, headers=headers, data=json.dumps(payload))

    if response.status_code == 201:
        print(f'\nPlaylist \'{name}\' created successfully!\n')
    else:
        print(f'\nError {response.status_code}: {response.json()}\n')

    return response.json()

def album_track_ids(album, token):
    url = album['href']
    response = requests.get(url, headers={'Authorization': 'Bearer ' + token})
    album_dict = response.json()
    tracks = album_dict['tracks']
    track_ids = [track['id'] for track in tracks['items']]

    return track_ids

def extend_playlist(playlist_id, track_ids, token):
    headers = {
        'Authorization': 'Bearer ' + token,
        'Content-Type': 'application/json'
    }
    url = f'{SPOTIFY_API_ENDPOINTS['playlists']}/{playlist_id}/tracks'
    payload = {
        'uris': [f'spotify:track:{track_id}' for track_id in track_ids]
    }
    response = requests.post(url, headers=headers, data=json.dumps(payload))

    if response.status_code == 201:
        print(f'Added {len(track_ids)} tracks to the playlist!')
    else:
        print(f'Error {response.status_code}: {response.json()}')

    return    

# %%
def main():

    scopes_playlists = ['playlist-modify-private', 'playlist-modify-public', 'user-follow-read', 'user-read-private', 'user-read-email']
    tokens_dict = rw_tokens(tokens_json, scopes_playlists)

    total = 0
    after_value = ''
    while after_value is not None:
        follow_dict = None if not total else follow_dict
        after_value = None if not total else after_value
        follow_dict = get_follow_dict(follow_dict, after_value, tokens_dict['access_token'])

        if not total:    
            total = follow_dict['total'][-1]
        actual = len(follow_dict['items'])

        print(f'Fetched {actual}/{total} artists...\n')

        if actual >= total:
            print(f'{'-'*5} List is full! {type(follow_dict).__name__.upper()} has {actual} artists {'-'*5}')
            print(f'Every artist \'item\' has {len(follow_dict["items"][0])} keys:\n\t{list(follow_dict["items"][0].keys())}\n')
            break

        after_value = follow_dict['cursors'][-1]['after']
    
    artists_fetched = {item['name']: item['id'] for item in follow_dict['items']}
    print(f'{len(artists_fetched)} artists fetched:')
    for idx, (artist, id) in enumerate(artists_fetched.items(), start=1):
        print(f'\t{idx}: \'{artist}\' /// \'{id}\'')

    chosen_artist = input('\nChoose an artist to get the albums by index (integer) or id (string) or name (string) [or Q\\q to exit]: ')
    if chosen_artist.lower() == 'q':
        print('Bye!')
        exit()
    if chosen_artist.isdigit():
        while int(chosen_artist) < 1 or int(chosen_artist) > len(artists_fetched):
            chosen_artist = input('Invalid index... Try again! ')
        chosen_artist = list(artists_fetched.keys())[int(chosen_artist)-1]
        chosen_artist_id = list(artists_fetched.values())[list(artists_fetched.keys()).index(chosen_artist)].strip()
    elif chosen_artist.lower() in [name.lower() for name in artists_fetched.keys()]:
        chosen_artist = [name for name in artists_fetched.keys() if name.lower() == chosen_artist.lower()][0]
        chosen_artist_id = artists_fetched[chosen_artist].strip()
    elif chosen_artist in artists_fetched.values():
        chosen_artist_id = chosen_artist.strip()


    print(f'You chose !!{chosen_artist}!!\n')

    albums = get_artist_albums(chosen_artist_id, tokens_dict['access_token'])
    user_id = get_profile(tokens_dict['access_token'])
    playlist_obj = public_playlist(user_id, tokens_dict['access_token'])

    all_tracks_ids = []
    for album in albums:
        tracks = album_track_ids(album, tokens_dict['access_token'])
        all_tracks_ids.append(tracks)

    all_tracks_ids = [track for sublist in all_tracks_ids for track in sublist]
    
    progress = 0
    while progress < len(all_tracks_ids):
        print(f'\nPROGRESS: {progress}\\{len(all_tracks_ids)} in range from {progress+1} to {progress+100 if progress+100 < len(all_tracks_ids) else len(all_tracks_ids)}')
        extend_playlist(playlist_obj['id'], all_tracks_ids[progress:100+progress], tokens_dict['access_token'])
        #all_tracks_ids = all_tracks_ids[100:]
        progress += 100

if __name__ == '__main__':
    main()