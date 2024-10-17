# %% MODULES
from os import getcwd, path, getenv, makedirs
from dotenv import load_dotenv
from secrets import token_hex
from requests import get, post, exceptions
from urllib.parse import urlencode
from datetime import datetime, timedelta
from json import dumps, dump, load
from pandas import DataFrame
from logging import error

# %% VARIABLES
working_directory = path.dirname(current_directory := getcwd())
parent_dir = path.dirname(working_directory)
data_dir = path.join(working_directory, 'data')
data_long = path.join(data_dir, 'long')
data_short = path.join(data_dir, 'short')
tokens_json = path.join(data_dir, 'tokens.json')

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

load_dotenv()
spotify_client_id = getenv('SPOTIFY_CLIENT_ID')
spotify_client_secret = getenv('SPOTIFY_CLIENT_SECRET')

# %% FUNCTIONS
def get_values(nested_dict):
    folders = []
    for value in nested_dict.values():
        if isinstance(value, dict):
            folders.extend(get_values(value))
        else:
            folders.append(value)
    return folders

def file_existence() -> None:

    if spotify_client_id is None or spotify_client_secret is None:
        raise ValueError('Both SPOTIFY_CLIENT_ID and SPOTIFY_CLIENT_SECRET must be set in .env file!\n')
    
    else:
        print(f'Acquired SPOTIFY_CLIENT_ID ({'...' + spotify_client_id[6:16] + '...'}) and SPOTIFY_CLIENT_SECRET ({'...' + spotify_client_secret[6:16] + '...'})!\n')

    print(f'Checking paths in current directory {working_directory}\n')
    for f in get_values(paths):
        print(f'{path.basename(f):>12} {f'exists' if path.exists(f) else f'created'} in {path.abspath(f).split('GitHub\\')[1]}')
        makedirs(f, exist_ok=True)

    env_variables = path.join(paths['parent'], '.env')

    if not load_dotenv(env_variables):
        raise FileNotFoundError(f'Secrets file not found. Expected path: {path.abspath(env_variables).split("GitHub\\")[1]}')
    
    print('\nBoth directories and .env file exist!\n')

    if not spotify_client_id or not spotify_client_secret:
        raise ValueError('Both SPOTIFY_CLIENT_ID and SPOTIFY_CLIENT_SECRET must be set in .env file!\n')

def get_auth_url() -> None:

    state = token_hex(8)

    params = {
        'client_id': spotify_client_id,
        'response_type': 'code',
        'redirect_uri': spotify_redirect_uri,
        'state': state,
        'scope': 'user-follow-read',
    }

    r = get(SPOTIFY_API_ENDPOINTS['authorize'], params=urlencode(params))

    auth_code_url = r.url
    
    print(f'Open this url in your browser:\n{auth_code_url}') 
    
    data = {
        'state': state,
        'auth_code_url': auth_code_url,
    }
    
    return data

def get_code(data: dict) -> str:

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
    
    response = post(SPOTIFY_API_ENDPOINTS['token'], data=c_payload)
    
    if response.status_code == 200:
        data = response.json()
        tokens_dict['expiration'] = (datetime.now() + timedelta(hours=1)).isoformat()
        
        return data
    else:
        print(f'HTTP Error{response.status_code}\n{dumps(response.json(), indent=4)}')
        return None

def rw_tokens(filepath):

    is_file = path.isfile(filepath)
    if is_file:

        with open(filepath, 'r') as f:
            print('Reading \'tokens.json\'...\n')
            tokens = load(f)
        
        old_expiration_time = datetime.fromisoformat(tokens['expiration'])
        expired = datetime.now() >= old_expiration_time
        
        if not expired:
            time_left = old_expiration_time - datetime.now()
            total_seconds = int(time_left.total_seconds())
            minutes, seconds = divmod(total_seconds, 60)
            print(f'Access token is still valid for {minutes:02d}:{seconds:02d} minutes...\n')
            print(dumps({'access_token': '...' + tokens['access_token'][8:14] + '...', 'expiration': tokens['expiration']}, indent=4), end='\n\n')

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
        dump(tokens, f, indent=4)
    
    print('\nNew tokens written to \'tokens.json\':\n')

    tokens_to_safely_print = {
        'access_token': '...' + tokens['access_token'][8:14] + '...',
        'token_type': tokens['token_type'],
        'expires_in': tokens['expires_in'],
        'refresh_token': '...' + tokens['refresh_token'][6:12] + '...',
        'scope': tokens['scope'],
        'expiration': tokens['expiration'],
    }
    print(dumps(tokens_to_safely_print, indent=4))

    return tokens

def extendar(book: dict, pages: dict) -> dict:

    book_copy = book.copy()
    for k, v in pages.items():

        if k in book_copy: # Should be always True!
            if isinstance(book_copy[k], list):
                if isinstance(v, list):
                    book_copy[k] = book_copy[k] + v
                else:
                    book_copy[k].append(v)
            else:
                book_copy[k] = [book_copy[k], v]
        else:
            book_copy[k] = v

    return book_copy

def df_writer(dicty: dict, long: bool) -> DataFrame:

    if not dicty:
        raise ValueError("Input dictionary is empty")
   
    track = 'LONG' if long else 'SHORT'
    artists_array = dicty['items']
    relevant_cols = artists_array[0].keys() if long else ['id', 'name', 'genres', 'followers', 'popularity']

    dict_for_df = {col: [artists_array[i][col] for i in range(len(artists_array))] for col in relevant_cols}
    df = DataFrame(dict_for_df)

    print(f'{track} form dataframe creation:\n')

    if long:
        print('Exploding genres column into individual rows...')
        genres_df = df['genres'].explode()
        print('Calculating genre frequency...')
        genres_df = genres_df.value_counts().sort_values(ascending=False)
        print('Creating genre frequency dataframe...')
        genres_df = genres_df.to_frame().reset_index()
        print('Resetting index for proper ordering...')
        genres_df = genres_df.reindex(range(len(genres_df)))
        print('Renaming columns for clarity...\n')
        genres_df.columns = ['genre', 'count']

        def most_genre_col(df):

            def gen_count(genre):
                lookup_result = genres_df.loc[genres_df['genre'] == genre, 'count']
                
                return lookup_result.values[0] if len(lookup_result) == 1 else lookup_result.iloc[0]
            
            x = df.copy()
            column = x['genres'].apply(lambda x: sorted([(gen_count(l), l) for l in x], reverse=True))
            x = x.assign(most_genre=column)
            return x

        df = most_genre_col(df)

    print('Converting artist names to lowercase...')
    df['name'] = df['name'].str.lower()
    print('Extracting total followers from dictionary...')
    df['followers'] = df['followers'].apply(lambda x: x['total'])
    print('Extracting specific genres from genres list...\n')
    df['specific_genre'] = df['genres'].apply(lambda x: set(word for sublist in x for word in sublist.split()))
    df.dropna(subset=['specific_genre'], inplace=True)

    print(f'Generated \'{track}_df\' from \'follow_dict\' with columns: {list(df.columns)}.\n')

    now = datetime.now().strftime("%Y-%m-%d_%H-%M")

    outdir = paths['data_dir'][track.lower()]
    outname = f'{now}_{track}_follow_dict.csv'
    outpath = path.join(outdir, outname)

    with open(outpath, 'w', encoding='utf-8', newline='') as f:
        df.to_csv(f, index=False, sep=';', encoding='utf-8')   
    print(f'Saved {track}_csv: \'{outname}\'.\n')
    
    return df

def get_follow_dict(init_dict: dict | None = None, after_value: str | None = None, access_token: str | None = None) -> dict:

    if not access_token:
        raise Exception('Error: \'access_token\' is None!\n')

    headers = {
        'Authorization': 'Bearer ' + access_token
    }

    params = {
        'type': 'artist',
        'limit': limit,
    }

    if not init_dict:
        try:
            response = get(SPOTIFY_API_ENDPOINTS['artist'], params=urlencode(params), headers=headers)
            response.raise_for_status()
            init_dict = response.json()['artists']
            print(f'Initialized \'follow_dict\' {type(init_dict).__name__.upper()} with {len(init_dict["items"])} items and with keys:\n\t{list(init_dict.keys())}.\n')
        except exceptions.RequestException as e:
            error(f"Error in 'get_follow_list' function: {str(e)}\n")
            return {}
        
    if not after_value:
        if len(init_dict['items']) == init_dict['total']:
            print(f'LIST IS FULL!!\n')
            return init_dict
        after_value = init_dict['cursors']['after']

    params['after'] = after_value
    try:
        response = get(SPOTIFY_API_ENDPOINTS['artist'], params=urlencode(params), headers=headers)
        response.raise_for_status()
        data = response.json()['artists']

        return extendar(init_dict, data)
    
    except exceptions.RequestException as e:
        error(f"Error in 'get_follow_list' function: {str(e)}")

def check_duplicates(dicty: dict) -> dict:
    
    if not 'items' in dicty.keys():
        print('Invalid dictionary without \'items\' key:', dicty.keys())
        return
    
    artists_array = dicty['items']
    names_list = [artists_array[i]['name'] for i in range(len(artists_array))]

    i = 0
    duplicates = []
    for name in names_list:
        count = names_list.count(name)
        if count > 1:
    
            duplicates.append({
                'name': name,
                'position': i,
                'n_followers': artists_array[i]['followers']['total'],
                'id': artists_array[i]['id'],
            })
        
        i+=1

    print(f'Found {len(duplicates)} duplicates:')
    df_duplicates = DataFrame(duplicates)
    
    return df_duplicates

# %% MAIN
def main():
    
    file_existence()

    tokens_dict = rw_tokens(tokens_json)

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

    check_duplicates(follow_dict)

    df_writer(follow_dict, long=True)
    df_writer(follow_dict, long=False)

    print(f'\n------------------------------------------------------ !END! ------------------------------------------------------\n')

    return

# %% RUN
if __name__ == '__main__':
    main()
