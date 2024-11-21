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
from Auth_Followlist import file_existence, rw_tokens, df_writer

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
    'artist': 'https://api.spotify.com/v1/me/following'
}

limit = 50

tokens_dict = {}

env_path = os.path.join(paths['parent'], '.env')
load_dotenv(env_path)
spotify_client_id = os.getenv('SPOTIFY_CLIENT_ID')
spotify_client_secret = os.getenv('SPOTIFY_CLIENT_SECRET')

#scope = 'user-follow-read' # 'playlist-modify-public'

# %%
'''
def get_auth_url() -> dict:
    """
    Generates an authorization URL for Spotify's user-follow-read scope and prints it.
    This function creates a state token and constructs the authorization URL with the necessary
    parameters including client ID, response type, redirect URI, state, and scope. It then makes
    a GET request to Spotify's authorization endpoint to retrieve the full authorization URL.
    The URL is printed to the console for the user to open in their browser.
    Returns:
        dict: A dictionary containing the state token and the authorization URL.
    """

    state = secrets.token_hex(8)

    params = {
        'client_id': spotify_client_id,
        'response_type': 'code',
        'redirect_uri': spotify_redirect_uri,
        'state': state,
        'scope': ' '.join(scopes),
    }

    r = requests.get(SPOTIFY_API_ENDPOINTS['authorize'], params=urlencode(params))

    auth_code_url = r.url
    
    print(f'Open this url in your browser:\n{auth_code_url}')
    
    data = {
        'state': state,
        'auth_code_url': auth_code_url,
    }
    
    return data

def get_code(data: dict) -> str:
    """
    Extracts the authorization code from a given fallback URL.
    Args:
        data (dict): A dictionary containing 'state' and 'auth_code_url' keys.
    Returns:
        str: The extracted authorization code.
    Raises:
        Exception: If the fallback URL is None or does not contain the expected state.
    """

    state = data['state']
    auth_code_url = data['auth_code_url']

    fallback_url = input('Enter fallback url from browser: ')

    if fallback_url is None:
        raise Exception(f"Error: \'authcodeurl\' is None!")
    if state not in fallback_url:
        raise Exception(f"Error: {fallback_url} is not in AUTH_URL {auth_code_url[:16]}")
    
    code = fallback_url.split('code=')[-1].split('&state=')[0]
    print(f'Code: ...{code[6:16]}...\n')

    return code



def get_tokens(auth_code: str | None, refresh_t: str = None) -> tuple:
    """
    Retrieves access and refresh tokens from the Spotify API using either an authorization code or a refresh token.
    Args:
        auth_code (str | None): The authorization code obtained from the Spotify authorization process. 
                                This is required if `refresh_t` is not provided.
        refresh_t (str, optional): The refresh token obtained from a previous token request. 
                                   This is required if `auth_code` is not provided.
    Returns:
        tuple: A tuple containing the access token and refresh token if the request is successful, 
               or None if the request fails.
    """

    auth_code_to_print = auth_code[6:16] if auth_code is not None else auth_code
    refresh_t_to_print = refresh_t[6:16] if refresh_t is not None else refresh_t

    print(f'auth_code: ...{auth_code_to_print}...\nrefresh_t: ...{refresh_t_to_print}...\n')
    refresh_flag = True if refresh_t is not None else False
    print(f'{'REFRESHING TOKENS' if refresh_flag else "CREATING TOKENS"} ... ...')
    payload = {
        'client_id': spotify_client_id,
        'client_secret': spotify_client_secret,
        'grant_type': 'refresh_token' if refresh_flag else 'authorization_code',
    }
    
    c_payload = payload.copy()
    c_payload.update({
        'refresh_token': refresh_t,
    } if refresh_flag else {
        'code': auth_code,
        'redirect_uri': spotify_redirect_uri,
    })
    
    response = requests.post(SPOTIFY_API_ENDPOINTS['token'], data=c_payload)
    
    if response.status_code == 200:
        data = response.json()
        tokens_dict['expiration'] = (datetime.now() + timedelta(hours=1)).isoformat()
        
        return data
    else:
        print(f'HTTP Error{response.status_code}\n{json.dumps(response.json(), indent=4)}')
        return None



def rw_tokens(filepath: str) -> dict:
    """
    Reads, validates, and refreshes authentication tokens from a JSON file.
    If the tokens file exists and the access token is still valid, it reads and returns the tokens.
    If the access token is expired or the file does not exist, it requests new tokens using the refresh token
    or authorization code, updates the expiration time, and writes the new tokens to the file.
    Args:
        filepath (str): The path to the JSON file containing the tokens.
    Returns:
        dict: A dictionary containing the authentication tokens.
    """

    is_file = os.path.isfile(filepath)
    if is_file:

        with open(filepath, 'r') as f:
            print(f'Reading \'{filepath\'...\n')
            tokens = json.load(f)
        
        old_expiration_time = datetime.fromisoformat(tokens['expiration'])
        expired = datetime.now() >= old_expiration_time
        
        if not expired:
            time_left = old_expiration_time - datetime.now()
            total_seconds = int(time_left.total_seconds())
            minutes, seconds = divmod(total_seconds, 60)
            print(f'Access token is still valid for {minutes:02d}:{seconds:02d} minutes...\n')
            print(json.dumps({'access_token': '...' + tokens['access_token'][8:14] + '...', 'expiration': tokens['expiration']}, indent=4), end='\n\n')

            return tokens

        print(f'Access token expired! New request with refresh token: {tokens["refresh_token"][6:16]}...')
    
    else:
        data = get_auth_url()
        code = get_code(data)
        tokens = {}

    expiration_time = datetime.now() + timedelta(hours=1) if not is_file or expired else old_expiration_time
    authorization_code = code if not is_file else None
    refresh_token = None if not is_file else tokens['refresh_token']

    tokens.update(get_tokens(authorization_code, refresh_token))
    tokens['expiration'] = expiration_time.isoformat()
    
    with open(filepath, 'w') as f:
        json.dump(tokens, f, indent=4)
    
    print(f'\nNew tokens written to \'{filepath}\':\n')

    tokens_to_safely_print = {
        'access_token': '...' + tokens['access_token'][8:14] + '...',
        'token_type': tokens['token_type'],
        'expires_in': tokens['expires_in'],
        'refresh_token': '...' + tokens['refresh_token'][6:12] + '...',
        'scope': tokens['scope'],
        'expiration': tokens['expiration'],
    }
    print(json.dumps(tokens_to_safely_print, indent=4))

    return tokens
'''


# %%
def main():

    scopes = ['playlist-modify-private', 'playlist-modify-public', 'user-follow-read', 'user-follow-modify', 'user-library-read', 'user-library-modify', 'user-read-private', 'user-read-email', 'user-top-read']
    tokens_dict = rw_tokens(tokens_json, scopes)

    for key, value in tokens_dict.items():
        print(f'{key}: {value}')

if __name__ == '__main__':
    main()