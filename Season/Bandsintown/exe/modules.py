# %% LIBRARIES
from os import getenv, path, makedirs, getcwd, listdir
from pandas import DataFrame, Series, Timestamp, read_csv, to_datetime, NaT
from dotenv import load_dotenv
from random import choice, uniform
from secrets import token_hex
from requests import get, post, exceptions, RequestException, Response
from bs4 import BeautifulSoup
from json import load, loads, dump, dumps
from datetime import datetime, timedelta
from subprocess import run, CalledProcessError
from gzip import GzipFile
from io import BytesIO
from xml.dom import minidom
from xml.etree import ElementTree as ET
from ast import literal_eval
from urllib.parse import urlencode
from time import sleep
from dotenv import load_dotenv
from glob import glob
from numpy import nan
from logging import info, error
from re import match
from geopy.distance import geodesic

# %% VARIABLES
load_dotenv()
spotify_client_id = getenv('SPOTIFY_CLIENT_ID')
spotify_client_secret = getenv('SPOTIFY_CLIENT_SECRET')

exe_directory = getcwd()
root_dir = path.dirname(exe_directory)
paths = {
    'xml': path.join(root_dir, 'xml'),
    'data': path.join(root_dir, 'data'),
    'short': path.join(root_dir, 'data', 'short'),
    'long': path.join(root_dir, 'data', 'long'),
    'FinalOutput': path.join(root_dir, 'data', 'FinalOutput'),
    'BiT_Archive': path.join(root_dir, 'data', 'BiT_Archive'),
}

SPOTIFY_API_ENDPOINTS = {
    'authorize': 'https://accounts.spotify.com/authorize',
    'token': 'https://accounts.spotify.com/api/token',
    'artist': 'https://api.spotify.com/v1/me/following',
    'redirect_uri': 'https://open.spotify.com/intl-it',
}

sestosg = (45.53, 9.23)

# %% SUBPROCESS
def do_subprocess(script_name: str) -> None:
    """
    Executes the specified script as a subprocess.

    Args:
        script_name (str): The name of the script to execute.

    Raises:
        CalledProcessError: If the subprocess execution fails.
    """
    try:
        run(path.join(getcwd(), script_name), check=True)
        info(f'Successfully executed \'{script_name}\'')
    except CalledProcessError as e:
        error(f'Error executing \'{script_name}\': {e.returncode} - {e.stderr}')

# %% Auth_Followlist.py
def file_existence() -> None:
    """
    Checks the existence of necessary directories and environment variables.
    Creates directories if they do not exist and loads environment variables.

    Raises:
        ValueError: If SPOTIFY_CLIENT_ID or SPOTIFY_CLIENT_SECRET are not set in the .env file.
        FileNotFoundError: If the .env file is not found.
    """
    global spotify_client_id, spotify_client_secret    

    if spotify_client_id is None or spotify_client_secret is None:
        raise ValueError('Both SPOTIFY_CLIENT_ID and SPOTIFY_CLIENT_SECRET must be set in .env file!\n')
    
    print(f'Acquired SPOTIFY_CLIENT_ID ({f"...{spotify_client_id[6:16]}..."}) and SPOTIFY_CLIENT_SECRET ({f"...{spotify_client_secret[6:16]}..."})!\n')

    # --- Nested function --- #
    def get_values(nested_dict: dict) -> list:
        """
        Recursively retrieves all values from a nested dictionary.

        Args:
            nested_dict (dict): Dictionary from which to retrieve values.

        Returns:
            list: All values found in the nested dictionary.
        """

        folders = [v for value in nested_dict.values() for v in (get_values(value) if isinstance(value, dict) else [value])]
        return folders
    # --- End --- #

    working_directory = getcwd()
    print(f'Checking paths in current directory {working_directory}\n')

    for f in get_values(paths):
        status = 'exists' if path.exists(f) else 'created'
        print(f'{path.basename(f):>12} {status} in {path.abspath(f).split("GitHub\\")[1]}')
        makedirs(f, exist_ok=True)

    env_variables = path.join(root_dir, '.env')

    if not load_dotenv(env_variables):
        raise FileNotFoundError(f'Secrets file not found. Expected path: {path.abspath(env_variables).split("GitHub\\")[1]}')
    
    print('\nBoth directories and .env file exist!\n')

    if not spotify_client_id or not spotify_client_secret:
        raise ValueError('Both SPOTIFY_CLIENT_ID and SPOTIFY_CLIENT_SECRET must be set in .env file!\n')

def rw_tokens(filepath: str) -> dict:
    """
    Reads and writes Spotify tokens from/to a JSON file.

    Args:
        filepath (str): Path to the JSON file containing the tokens.

    Returns:
        dict: Dictionary containing the tokens.
    """
    global spotify_client_id, spotify_client_secret, SPOTIFY_API_ENDPOINTS

    # --- Nested function --- #
    def get_auth_url() -> dict:
        """
        Generates the Spotify authorization URL and state token.

        Returns:
            dict: Dictionary containing the state token and the authorization URL.
        """
        state: str = token_hex(8)

        params: dict = {
            'client_id': spotify_client_id,
            'response_type': 'code',
            'redirect_uri': SPOTIFY_API_ENDPOINTS['redirect_uri'],
            'state': state,
            'scope': 'user-follow-read',
        }

        try:
            r = get(SPOTIFY_API_ENDPOINTS['authorize'], params=urlencode(params))
            r.raise_for_status()
        except exceptions.RequestException as e:
            error(f'Error fetching authorization URL: {e}')
            return {}

        auth_code_url: str = r.url
        print(f'Open this url in your browser:\n{auth_code_url}') 

        vars: dict = {
            'state': state,
            'auth_code_url': auth_code_url,
        }
        
        return vars
    # --- End --- #

    # --- Nested function --- #
    def get_code(data: dict) -> str:
        """
        Extracts the authorization code from the fallback URL provided by the user.

        Args:
            data (dict): A dictionary containing the state token and the authorization URL.

        Returns:
            str: The extracted authorization code.

        Raises:
            ValueError: If the fallback URL is None or does not contain the expected state token.
        """
        state: str = data['state']
        auth_code_url: str = data['auth_code_url']

        fallback_url: str = input('Enter fallback url from browser: ')

        if fallback_url is None:
            raise Exception(f'Error: \'auth_code_url\' is None!')
        if state not in fallback_url:
            raise Exception(f'Error: {fallback_url} is not in AUTH_URL {auth_code_url[:16]}')
        
        code: str = fallback_url.split('code=')[-1].split('&state=')[0]
        print(f'Code: ...{code[6:16]}...\n')

        return code
    # --- End --- #

    # --- Nested function --- #
    def get_tokens(auth_code: str | None, refresh_t: str = None) -> tuple | None:
        """
        Retrieves or refreshes Spotify access tokens.

        Args:
            auth_code (str | None): Authorization code obtained from the Spotify authorization URL.
            refresh_t (str | None): Refresh token, if available.

        Returns:
            tuple | None: A tuple containing the access token and other token information, or None if the request fails.

        Raises:
            ValueError: If both auth_code and refresh_t are None.
        """
        if auth_code is None and refresh_t is None:
            raise ValueError("Either 'auth_code' or 'refresh_t' must be provided.")

        # Mask sensitive information for logging
        auth_code_to_print: str = auth_code[6:16] if auth_code is not None else auth_code
        refresh_t_to_print: str = refresh_t[6:16] if refresh_t is not None else refresh_t

        print(f'auth_code: ...{auth_code_to_print}...\nrefresh_t: ...{refresh_t_to_print}...\n')

        # Determine if we are refreshing tokens or creating new ones
        refresh_flag: bool = refresh_t is not None
        print(f'{"REFRESHING TOKENS" if refresh_flag else "CREATING TOKENS"} ... ...')

        # Base payload for the token request
        payload: dict = {
            'client_id': spotify_client_id,
            'client_secret': spotify_client_secret,
            'grant_type': 'refresh_token' if refresh_flag else 'authorization_code',
        }

        # Update payload with specific parameters
        c_payload: dict = payload.copy()
        c_payload.update({
            'refresh_token': refresh_t,
        } if refresh_flag else {
            'code': auth_code,
            'redirect_uri': SPOTIFY_API_ENDPOINTS['redirect_uri'],
        })

        # Make the request to the Spotify token endpoint
        response = post(SPOTIFY_API_ENDPOINTS['token'], data=c_payload)

        if response.status_code == 200:
            data: dict = response.json()
            tokens['expiration'] = (datetime.now() + timedelta(hours=1)).isoformat()
            return data
        else:
            print(f'HTTP Error {response.status_code}\n{dumps(response.json(), indent=4)}')
            return None
    # --- End --- #

    is_file: bool = path.isfile(filepath)
    if is_file:
        with open(filepath, 'r') as f:
            print('Reading \'tokens.json\'...\n')
            tokens: dict = load(f)
        
        old_expiration_time: datetime = datetime.fromisoformat(tokens['expiration'])
        expired: bool = datetime.now() >= old_expiration_time
        
        if not expired:
            time_left: timedelta = old_expiration_time - datetime.now()
            total_seconds: int = int(time_left.total_seconds())
            minutes, seconds = divmod(total_seconds, 60)
            print(f'Access token is still valid for {minutes:02d}:{seconds:02d} minutes...\n')
            print(dumps({'access_token': '...' + tokens['access_token'][8:14] + '...', 'expiration': tokens['expiration']}, indent=4), end='\n\n')

            return tokens

        print(f'Access token expired! New request with refresh token: {tokens["refresh_token"][6:16]}...')
    
    else:
        data: dict = get_auth_url()
        code: str = get_code(data)
        tokens: dict = {}
        
    expiration_time: datetime = datetime.now() + timedelta(hours=1) if not is_file or expired else old_expiration_time
    authorization_code: str | None = code if not is_file else None
    refresh_token: str | None = None if not is_file else tokens['refresh_token']

    tokens.update(get_tokens(authorization_code, refresh_token))
    tokens['expiration'] = expiration_time.isoformat()
    
    with open(filepath, 'w') as f:
        dump(tokens, f, indent=4)
    
    print('\nNew tokens written to \'tokens.json\':\n')

    tokens_to_safely_print: dict = {
        'access_token': '...' + tokens['access_token'][8:14] + '...',
        'token_type': tokens['token_type'],
        'expires_in': tokens['expires_in'],
        'refresh_token': '...' + tokens['refresh_token'][6:12] + '...',
        'scope': tokens['scope'],
        'expiration': tokens['expiration'],
    }
    print(dumps(tokens_to_safely_print, indent=4))

    return tokens

def get_follow_dict(init_dict: dict | None = None, after_value: str | None = None, access_token: str | None = None) -> dict:
    """
    Retrieves the follow list of artists from Spotify.

    Args:
        init_dict (dict | None): Initial dictionary to store the follow list. Defaults to None.
        after_value (str | None): Cursor value to fetch the next set of results. Defaults to None.
        access_token (str | None): Spotify access token. Must be provided.

    Returns:
        dict: Dictionary containing the follow list of artists.

    Raises:
        Exception: If the access_token is None.
    """
    # --- Nested function --- #
    def extendar(book: dict, pages: dict) -> dict:
        """
        Extends a dictionary with another dictionary, merging lists if necessary.

        Args:
            book (dict): The original dictionary.
            pages (dict): The dictionary to merge into the original.

        Returns:
            dict: The extended dictionary.
        """
        book_copy: dict = book.copy()
        for k, v in pages.items():
            if k in book_copy:  # Should be always True!
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
    # --- End --- #

    if not access_token:
        raise Exception('Error: \'access_token\' is None!\n')

    headers: dict = {
        'Authorization': 'Bearer ' + access_token
    }

    limit = 50
    params: dict = {
        'type': 'artist',
        'limit': limit,
    }

    # Initialize the follow dictionary if not provided
    if not init_dict:
        try:
            response = get(SPOTIFY_API_ENDPOINTS['artist'], params=urlencode(params), headers=headers)
            response.raise_for_status()
            init_dict = response.json()['artists']
            print(f'Initialized \'follow_dict\' {type(init_dict).__name__.upper()} with {len(init_dict["items"])} items and with keys:\n\t{list(init_dict.keys())}.\n')
        except exceptions.RequestException as e:
            error(f'Error in \'get_follow_dict\' function: {str(e)}\n')
            return {}
        
    # Check if the list is already full
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
        error(f'Error in \'get_follow_dict\' function: {str(e)}')
        return {}

def check_duplicates(dictionary: dict) -> DataFrame:
    """
    Checks for duplicate artists in the dictionary and returns a DataFrame of duplicates.

    Args:
        dictionary (dict): The dictionary containing artist data.

    Returns:
        DataFrame: DataFrame containing duplicate artist information.
    """
    # Ensure the dictionary contains the 'items' key
    if 'items' not in dictionary:
        print('Invalid dictionary without \'items\' key:', dictionary.keys())
        return DataFrame()

    # Extract the list of artists
    artists_array: list[dict] = dictionary['items']
    # Create a list of artist names
    names_list: list[str] = [artist['name'] for artist in artists_array]

    # Initialize a list to store duplicates
    duplicates: list[dict] = []
    # Iterate over the list of names to find duplicates
    for i, name in enumerate(names_list):
        count: int = names_list.count(name)
        if count > 1:
            duplicates.append({
                'name': name,
                'position': i,
                'n_followers': artists_array[i]['followers']['total'],
                'id': artists_array[i]['id'],
            })

    print(f'Found {len(duplicates)} duplicates:')
    # Create a DataFrame from the list of duplicates
    df_duplicates: DataFrame = DataFrame(duplicates)

    return df_duplicates

def df_writer(dictionary: dict, long: bool) -> DataFrame:
    """
    Writes a dictionary to a DataFrame and saves it as a CSV file.

    Args:
        dictionary (dict): The dictionary to write to the DataFrame.
        long (bool): Whether to use the long form of the DataFrame.

    Returns:
        DataFrame: The created DataFrame.

    Raises:
        ValueError: If the input dictionary is empty.
    """
    global paths

    if not dictionary:
        raise ValueError('Input dictionary is empty')
   
    track: str = 'LONG' if long else 'SHORT'
    artists_array: list[dict] = dictionary['items']
    relevant_cols: list[str] = artists_array[0].keys() if long else ['id', 'name', 'genres', 'followers', 'popularity']

    dict_for_df: dict = {col: [artists_array[i][col] for i in range(len(artists_array))] for col in relevant_cols}
    df: DataFrame = DataFrame(dict_for_df)

    print(f'{track} form dataframe creation:\n')

    if long:
        print('Exploding genres column into individual rows...')
        genres_df: DataFrame = df['genres'].explode()
        print('Calculating genre frequency...')
        genres_df = genres_df.value_counts().sort_values(ascending=False)
        print('Creating genre frequency dataframe...')
        genres_df = genres_df.to_frame().reset_index()
        print('Resetting index for proper ordering...')
        genres_df = genres_df.reindex(range(len(genres_df)))
        print('Renaming columns for clarity...\n')
        genres_df.columns = ['genre', 'count']

        # --- Nested function --- #
        def most_genre_col(df: DataFrame) -> DataFrame:
            """
            Adds a column with the most frequent genre for each artist.

            Args:
                df (DataFrame): The DataFrame to modify.

            Returns:
                DataFrame: The modified DataFrame.
            """

            # --- Nested function --- #
            def gen_count(genre: str) -> int:
                """
                Retrieves the count of a genre from the genres DataFrame.

                Args:
                    genre (str): The genre to count.

                Returns:
                    int: The count of the genre.
                """
                lookup_result = genres_df.loc[genres_df['genre'] == genre, 'count']
                return lookup_result.values[0] if len(lookup_result) == 1 else lookup_result.iloc[0]
            # --- End --- #

            x: DataFrame = df.copy()
            column = x['genres'].apply(lambda x: sorted([(gen_count(l), l) for l in x], reverse=True))
            x = x.assign(most_genre=column)
            return x
        # --- End --- #

        df = most_genre_col(df)

    print('Converting artist names to lowercase...')
    df['name'] = df['name'].str.lower()
    print('Extracting total followers from dictionary...')
    df['followers'] = df['followers'].apply(lambda x: x['total'])
    print('Extracting specific genres from genres list...\n')
    df['specific_genre'] = df['genres'].apply(lambda x: set(word for sublist in x for word in sublist.split()))
    df.dropna(subset=['specific_genre'], inplace=True)

    print(f'Generated \'{track}_df\' from \'follow_dict\' with columns: {list(df.columns)}.\n')

    now: str = datetime.now().strftime('%Y-%m-%d_%H-%M')

    outdir: str = paths[track.lower()]
    outname: str = f'{now}_{track}_follow_dict.csv'
    outpath: str = path.join(outdir, outname)

    with open(outpath, 'w', encoding='utf-8', newline='') as f:
        df.to_csv(f, index=False, sep=';', encoding='utf-8')
    print(f'Saved {track}_csv: \'{outname}\'.\n')
    
    return df

def human_readable_size(file: str) -> str:
    """
    Converts a file size to a human-readable format.

    Args:
        file (str): The file path.

    Returns:
        str: The human-readable file size.
    """
    size: int = path.getsize(file)
    for unit in ['', 'K', 'M', 'G', 'T', 'P', 'E', 'Z']:
        if size < 1024.0:
            return f"{size:.2f}{unit}B"
        size /= 1024.0
    return f"{size:.2f}YB"
    
# %% BiT_Spotify_Merge.py
def slept_req(url: str, wait_size: str = 'S') -> Response | None:
    """
    Sends a GET request to the specified URL with a random delay.

    Args:
        url (str): The URL to send the request to.
        wait_size (str): The wait mode. Can be 'S' (short), 'M' (medium), or 'L' (long).

    Returns:
        requests.Response | None: The response object if the request is successful, None otherwise.

    Raises:
        RequestException: If the request fails.
    """
    global cookies

    # --- Nested function --- #
    def please_wait(mode: str) -> None:
        """
        Pauses the execution for a random duration based on the specified mode.

        Args:
            mode (str): The wait mode. Can be 'S' (short), 'M' (medium), or 'L' (long).

        Raises:
            ValueError: If the mode is not one of 'S', 'M', or 'L'.
        """
        if mode is None:
            print('No wait_size specified, using default \'S\'\n')
            mode = 'S'
        if mode == 'M':
            sleep(uniform(2.5, 3.75))
        elif mode == 'L':
            sleep(uniform(10, 15))
        elif mode == 'S':
            sleep(0.3)
        else:
            raise ValueError("Invalid mode. Use 'S', 'M', or 'L'.")
    # --- End --- #

    BiT_Home: str = 'https://www.bandsintown.com/'
    first_touch: bool = url == BiT_Home

    print(f'Request for {"cookies..." if first_touch else f"{url}..."}')

    user_agents_list = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.169 Safari/537.3",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.103 Safari/537.3",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.121 Safari/537.3",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.3",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.102 Safari/537.3",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3497.100 Safari/537.3",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3440.106 Safari/537.3",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.99 Safari/537.3",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/66.0.3359.181 Safari/537.3",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.181 Safari/537.3",
        "Mozilla/5.0 (iPhone; CPU iPhone OS 12_2 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/12.1 Mobile/15E148 Safari/604.1",
        "Mozilla/5.0 (iPhone; CPU iPhone OS 12_1_4 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/12.0 Mobile/15E148 Safari/604.1",
        "Mozilla/5.0 (iPhone; CPU iPhone OS 12_1_3 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/12.0 Mobile/15E148 Safari/604.1",
        "Mozilla/5.0 (iPhone; CPU iPhone OS 12_1_2 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/12.0 Mobile/15E148 Safari/604.1",
        "Mozilla/5.0 (iPhone; CPU iPhone OS 12_1_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/12.0 Mobile/15E148 Safari/604.1",
        "Mozilla/5.0 (iPhone; CPU iPhone OS 12_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/12.0 Mobile/15E148 Safari/604.1",
        "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/12.0 Mobile/15E148 Safari/604.1",
        "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/12.0 Mobile/15E148 Safari/604.1",
        "Mozilla/5.0 (iPad; CPU OS 12_2 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/12.1 Mobile/15E148 Safari/604.1",
        "Mozilla/5.0 (iPad; CPU OS 12_1_4 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/12.0 Mobile/15E148 Safari/604.1",
        "Mozilla/5.0 (iPad; CPU OS 12_1_3 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/12.0 Mobile/15E148 Safari/604.1",
        "Mozilla/5.0 (iPad; CPU OS 12_1_2 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/12.0 Mobile/15E148 Safari/604.1",
        "Mozilla/5.0 (iPad; CPU OS 12_1_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/12.0 Mobile/15E148 Safari/604.1",
        "Mozilla/5.0 (iPad; CPU OS 12_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/12.0 Mobile/15E148 Safari/604.1",
        "Mozilla/5.0 (iPad; CPU OS 12_0_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/12.0 Mobile/15E148 Safari/604.1",
        "Mozilla/5.0 (iPad; CPU OS 12_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/12.0 Mobile/15E148 Safari/604.1",
    ]

    headers_dict = {
        "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
        "accept-language": "it-IT,it;q=0.9,en-IT;q=0.8,en;q=0.7,en-US;q=0.6",
        "cache-control": "max-age=0",
        "priority": "u=0, i",
        "sec-ch-ua": "\"Google Chrome\";v=\"129\", \"Not=A?Brand\";v=\"8\", \"Chromium\";v=\"129\"",
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": "\"Windows\"",
        "sec-fetch-dest": "document",
        "sec-fetch-mode": "navigate",
        "sec-fetch-site": "none",
        "sec-fetch-user": "?1",
        "upgrade-insecure-requests": "1",
        "referer": "https://www.google.com/"
    }

    if first_touch:
        r = get(url, headers={**headers_dict, 'User-Agent': choice(user_agents_list)})
    else:
        cookies = session_cookies(BiT_Home) if not cookies else cookies
        r = get(url, headers={**headers_dict, 'User-Agent': choice(user_agents_list), **cookies})

    if r.status_code != 200:
        print(f'Error in request: {r.status_code}\n')
        return None

    wait_size = 'S' if first_touch else wait_size
    
    please_wait(wait_size)
    
    return r

def session_cookies(url: str) -> dict:
    """
    Retrieves session cookies from the specified URL.

    Args:
        url (str): The URL to retrieve cookies from.

    Returns:
        dict: A dictionary of cookies.
    """
    r = slept_req(url)
    r_cookies = r.cookies

    return dict(r_cookies)

def xml_map_save(url: str) -> None:
    """
    Downloads and saves an XML sitemap from a URL.

    Args:
        url (str): The URL of the XML sitemap.

    Raises:
        ValueError: If the URL does not point to a valid XML file.
    """

    fname: str = path.join(paths['xml'], path.basename(url).replace('.gz', ''))

    if path.exists(fname):
        print(f'\'{path.basename(fname)}\' already exists!\n')
        return
    
    r = slept_req(url, wait_size='M')
    r_content: bytes = r.content

    with GzipFile(fileobj=BytesIO(r_content)) as f:
        xml_data: str = f.read()
        xml_data = minidom.parseString(xml_data).toprettyxml(indent='\t')
    
    with open(fname, 'w') as f:
        f.write(xml_data)

    print(f'Saved: {path.basename(fname)} -> {human_readable_size(fname)} kBytes\n')                                    

def xml_strings(fname: str) -> list[str] | None:
    """
    Extracts URLs from an XML sitemap file.

    Args:
        fname (str): The file path of the XML sitemap.

    Returns:
        list[str] | None: A list of URLs found in the sitemap, or None if the file is not valid.
    """
    if not fname.endswith('.xml'):
        print(f'{fname} is not an XML file\n')
        return None

    with open(fname, 'r') as f:
        xml_file: str = f.read()

    root = ET.fromstring(xml_file) 
    
    locs: list[str] = []

    key: str = 'artists' if 'artists' in fname else 'sitemap'

    for sitemap in root.findall(f'.//{{http://www.sitemaps.org/schemas/sitemap/0.9}}{"url" if key == "artists" else "sitemap"}'):
        loc: str = sitemap.find('{http://www.sitemaps.org/schemas/sitemap/0.9}loc').text
        
        if path.exists(path.join(paths['xml'], path.basename(loc).replace('.gz', ''))):
            continue
        
        if key == 'sitemap' and not 'artists' in loc.split('/')[-1]:
            continue
        
        locs.append(loc)

    if len(locs) > 0:
        print(f'\n{len(locs):,} elements found in {path.basename(fname)}.\n')

    return locs

def artist_bit_urls(csv_path: str) -> DataFrame:
    """
    Loads or creates a DataFrame of artist URLs from a CSV file.

    Args:
        csv_path (str): The path to the CSV file.

    Returns:
        DataFrame: The loaded or created DataFrame.
    """

    # --- Nested function --- #
    def bit_urls_df(urls_list: list[str]) -> DataFrame:
        """
        Creates a DataFrame from a list of URLs.

        Args:
            urls_list (list[str]): The list of URLs.

        Returns:
            DataFrame: The created DataFrame.
        """
        df: DataFrame = DataFrame(urls_list, columns=['BiT_url'])

        df['BiT_name'] = df['BiT_url'].apply(lambda x: path.basename(x))
        df['BiT_name'] = df['BiT_name'].apply(lambda x: x.split('-', 1)[-1] if '-' in x else '')
        df = df[~df['BiT_name'].eq('')]

        return df
    # --- Nested function --- #
    
    if path.exists(csv_path):
        BiT_urls: DataFrame = read_csv(csv_path, sep=';')
    else:
        artists_xml_from_sitemap: list[str] = glob(path.join(paths['xml'], 'artists*.xml'))
        sitemap_urls_list: list[str] = []

        for i, file in enumerate(artists_xml_from_sitemap):
            print(f'{i+1}/{len(artists_xml_from_sitemap)}: {path.basename(file)}')
            urls: list[str] = xml_strings(file)
            sitemap_urls_list.extend(urls)

        BiT_urls = bit_urls_df(sitemap_urls_list)
        BiT_urls.to_csv(csv_path, sep=';', index=False)
    
    print(f'{"Loaded" if path.exists(csv_path) else "Saved"} {len(BiT_urls):,} urls {"from" if path.exists(csv_path) else "to"} {path.basename(csv_path)}\nColumns: {list(BiT_urls.columns)}\n')
    
    return BiT_urls

def short_df_loader(csv_path: str) -> DataFrame:
    """
    Loads the latest short DataFrame from a directory.

    Args:
        csv_path (str): The directory path containing the CSV files.

    Returns:
        DataFrame: The loaded DataFrame.
    """
    latest_short_df: str = glob(path.join(csv_path, '*SHORT*'))[-1]
    followlist_short_csv: str = path.join(csv_path, latest_short_df)
    followlist_short: DataFrame = read_csv(followlist_short_csv, sep=';')

    followlist_short['genres'] = followlist_short['genres'].apply(lambda x: literal_eval(x))
    followlist_short['genres_set'] = followlist_short['genres'].apply(lambda x: set(word for sublist in x for word in sublist.split()))
    followlist_short['BiT_name_check'] = followlist_short['name'].apply(lambda x: x.replace(' ', '-'))

    return followlist_short

# %% BiT_Archive_Scraping.py
def json_response_eval(response_text: str) -> list[dict] | None:
    """
    Evaluates the JSON response from a request and extracts event dictionaries.

    Args:
        response_text (str): The response text from the request.

    Returns:
        list[dict] | None: A list of event dictionaries, or None if no events are found.

    Raises:
        ValueError: If no script tag is found in the HTML.
    """

    # --- Nested function --- #
    def dicts_from_soup(jsoups: list) -> list[dict]:
        """
        Extracts dictionaries from a list of BeautifulSoup objects.

        Args:
            jsoups (list): A list of BeautifulSoup objects.

        Returns:
            list[dict]: A list of dictionaries extracted from the BeautifulSoup objects.

        Raises:
            ValueError: If the input is not a list or a dictionary.
        """
        if not all(isinstance(soup, (list, dict)) for soup in jsoups):
            raise ValueError("\nData (\'dicts_from_soup\') is not a list nor a dict")

        artist_dicts: list[dict] = []
        for soup in jsoups:
            if isinstance(soup, list):
                for dictionary in soup:
                    artist_dicts.append(dictionary)
            elif isinstance(soup, dict):
                artist_dicts.append(soup)
            else:
                print(f'ERROR: {type(soup)} not dict nor list')

        events_dicts_list: list[dict] = [artist_dicts[i] for i in range(len(artist_dicts)) if artist_dicts[i]['@type'] == 'MusicEvent']

        return events_dicts_list
    # --- End --- #
    
    zuppa = BeautifulSoup(response_text, 'html.parser')
    script_soup = zuppa.find_all('script', type='application/ld+json')
    
    if not isinstance(script_soup, list):
        raise ValueError("\nNo \'script\' tag in html (\'json_response_eval\')")

    jsoups: list[dict] = [loads(script_soup[i].text) for i in range(len(script_soup))]

    dict_events: list[dict] = dicts_from_soup(jsoups)

    if dict_events is not None:
        print(f'\t{len(dict_events)} events found!')

    return dict_events if dict_events else None

def fetch_all_urls(url_series: Series) -> list[dict]:
    """
    Fetches data from all URLs in the given series.

    Args:
        url_series (pd.Series): A series of URLs to fetch data from.

    Returns:
        list[dict]: A list of dictionaries containing the fetched data.

    Raises:
        ValueError: If the input series is empty.
    """
    if url_series.empty:
        raise ValueError("\nNo \'url_series\' passed (\'fetch_all_urls\')")

    datalist: list[dict] = []

    for i, url in enumerate(url_series):
        name: str = url.split('/')[-1].split('-', 1)[1]
        print(f'\n{i+1}/{len(url_series)}: {name}')

        try:
            r = slept_req(url, wait_size='L')
            r.raise_for_status()
            rtext: str = r.text 
            rstatus: int = r.status_code

            if rstatus == 403:
                print(f'Status 403: {name}')
                print('\n!!Exiting program as you have been blocked!!\n')
                exit()

            if rtext is not None:
                rdata: list[dict] | None = json_response_eval(rtext)

                if rdata is not None:
                    datalist.extend(rdata)
                else:
                    print(f'\tResponse data is None: no events for {name}')
                    
        except RequestException as e:
            print(f"\nError (\'fetch_all_urls\') in request: {e}")
            return []

    return datalist

def save_dfs(datalist: list[dict]) -> None:
    """
    Saves data to CSV files.

    Args:
        datalist (list[dict]): The list of dictionaries to save.
    """
    global working_directory

    # --- Nested function --- #
    def artist_event_df(event_dict_list: list[dict] | dict | int) -> DataFrame:
        """
        Creates a DataFrame from a list of event dictionaries.

        Args:
            event_dict_list (list[dict] | dict | int): The list of event dictionaries.

        Returns:
            DataFrame: The created DataFrame.
        """

        # --- Nested function --- #
        def unwrap(diction: dict) -> dict:
            """
            Unwraps nested dictionaries to extract relevant information.

            Args:
                diction (dict): The dictionary to unwrap.

            Returns:
                dict: The unwrapped dictionary with relevant information.
            """
            location_data_keys: list[str] = ['addressCountry', 'addressLocality', 'streetAddress', 'postalCode']

            x: dict = diction.copy()

            if not isinstance(x, dict):
                print(f'\nNot a dict but {type(x).__name__}')
                return
            elif 'location' not in list(x.keys()):
                print(f'\nNo location key: {list(x.keys())}')
                return
            
            x['artist'] = x['performer']['name']

            location: dict = x['location']['address']
            for i in location.keys():
                if len(i) > 0 and i in location_data_keys:
                    x[i] = location[i]

            x['coordinates'] = (x['location']['geo']['latitude'], x['location']['geo']['longitude'])

            return x
        # --- End --- #

        # --- Nested function --- #
        def keypop(dictionary: dict) -> dict:
            """
            Removes unnecessary keys from a dictionary.

            Args:
                dictionary (dict): The dictionary to clean.

            Returns:
                dict: The cleaned dictionary.
            """
            location_data_keys: list[str] = ['addressCountry', 'addressLocality', 'streetAddress', 'postalCode']
            artist_data_keys: list[str] = ['name', 'url', 'startDate']

            x: dict = dictionary.copy()

            before_keys: list[str] = list(dictionary.keys())
            for k in before_keys:
                if k not in artist_data_keys + location_data_keys + ['coordinates', 'artist']:
                    x.pop(k)

            return x
        # --- End --- #
        
        ev_list: list[dict] = list(filter(lambda x: x is not None, event_dict_list if isinstance(event_dict_list, list) else [event_dict_list]))

        ev_df_list: list[dict] = []
        for ev in ev_list:
            ev = unwrap(ev)
            ev = keypop(ev)
            ev_df_list.append(ev)

        ev_df: DataFrame = DataFrame.from_records(ev_df_list)

        return ev_df
    # --- End --- #

    global csv_files

    data_df_alldicts: DataFrame = DataFrame(datalist)
    print(f'\nHead of \'all_events_dicts\':\n{data_df_alldicts.head(3)}\n')
    data_df_alldicts.to_csv(csv_files['all_events_dicts'], mode='w', sep=';', index=False)
    
    data_df: DataFrame = artist_event_df(datalist)
    print(f'Head of \'all_events_short\':\n{data_df.head(3)}\n')
    data_df.to_csv(csv_files['all_events_short'], mode='w', sep=';', index=False)
    
    print(f'Dataframes saved! in folder {path.relpath(csv_files["all_events_dicts"], path.dirname(working_directory))}')

# %% Europe_Events.py
def complexity(dataframe: DataFrame) -> DataFrame:
    """
    Adds complexity to the DataFrame by filling empty values, processing coordinates,
    and adding new columns for geocoordinates, days to event, formatted date, and artist name in lowercase.

    Args:
        dataframe (DataFrame): The input DataFrame.

    Returns:
        DataFrame: The modified DataFrame with additional columns.
    """

    # --- Nested function --- #
    def coordinates(x: DataFrame) -> DataFrame:
        """
        Processes the 'coordinates' column in the DataFrame, converting it to tuples if necessary,
        and calculates the distance from Sesto San Giovanni.

        Args:
            x (DataFrame): The input DataFrame.

        Returns:
            DataFrame: The modified DataFrame with 'latitude', 'longitude', and 'distance_from_Sesto' columns.
        """
        global sestosg

        if 'coordinates' not in x.columns:
            print('\nNo \'coordinates\' column in dataframe')
            return x
        
        if not all(isinstance(coord, tuple) for coord in x['coordinates']):
            print(f'\n\'coordinates\' column will be converted to tuples...')

            # --- Nested function --- #
            def convert_to_tuple(coord: str) -> tuple | None:
                """
                Converts a coordinate string to a tuple.

                Args:
                    coord (str): The coordinate string.

                Returns:
                    tuple | None: The converted tuple or None if conversion fails.
                """
                try:
                    match_flag = match(r'\(([^,]+), ([^,]+)\)', coord)
                    if match_flag:
                        return (float(match_flag.group(1)), float(match_flag.group(2)))
                    else:
                        raise ValueError(f"Invalid coordinate format: {coord}")
                except Exception as e:
                    print(f"Error converting coordinate: {e}")
                    return None
            # --- End --- #
            
            x['coordinates'] = x['coordinates'].apply(convert_to_tuple)
        
        # --- Nested function --- #
        def distance_from_sesto(home: tuple, lat: float, lon: float) -> float:
            """
            Calculates the distance from Sesto San Giovanni to a given latitude and longitude.

            Args:
                home (tuple): The coordinates of Sesto San Giovanni.
                lat (float): The latitude of the place.
                lon (float): The longitude of the place.

            Returns:
                float: The distance in kilometers, rounded to one decimal place.
            """
            place = (lat, lon)
            distance = geodesic(home, place).km

            return round(distance, 1)
        # --- End --- #
        
        x['latitude'] = x['coordinates'].apply(lambda coord: round(coord[0], 2) if coord else None)
        x['longitude'] = x['coordinates'].apply(lambda coord: round(coord[1], 2) if coord else None)
        x['distance_from_Sesto'] = x.apply(lambda y: distance_from_sesto(sestosg, y['latitude'], y['longitude']), axis=1)
        
        return x
    # --- End --- #

    # --- Nested function --- #
    def date_format(date_time_iso: datetime) -> str | None:
        """
        Formats a datetime object to a string in the format 'dd/mm/yyyy hh:mm'.

        Args:
            date_time_iso (datetime): The datetime object to format.

        Returns:
            str | None: The formatted date string or None if formatting fails.
        """
        try:
            formatted_date: str = date_time_iso.strftime('%d/%m/%Y %H:%M')
            return formatted_date
        except ValueError as e:
            print(f"Error in datetime format conversion: {e}")
            return None
    # --- End --- #

    # --- Nested function --- #
    def fill_empties(dataframe: DataFrame) -> DataFrame:
        """
        Replaces missing values in the DataFrame with an empty string.

        Args:
            dataframe (DataFrame): The input DataFrame.

        Returns:
            DataFrame: The modified DataFrame with missing values replaced.
        """
        x: DataFrame = dataframe.copy()
        missing_values: list = [nan, 'nan', 'NaN', None, 'NULL', 'null', 'N/A', 'n/a', 'NA', 'na', NaT]
        
        return x.replace(to_replace=missing_values, value='')
    # --- End --- #

    today = Timestamp.today()
    x: DataFrame = dataframe.copy()

    x = fill_empties(x)
    x = coordinates(x)
    x['startDate'] = to_datetime(x['startDate'], format='%Y-%m-%dT%H:%M:%S', errors='coerce')

    x['geocoordinates'] = x.apply(lambda x: (x['latitude'], x['longitude']), axis=1)
    x['days_to_event'] = x['startDate'].apply(lambda x: (x - today).days)
    x['Date'] = x['startDate'].apply(lambda y: date_format(y))
    x['artist'] = x['artist'].str.lower()

    x.drop(columns=['url', 'postalCode', 'coordinates'], inplace=True)

    return x

def mapper(df_from: DataFrame, keyword: str, column_returned: str) -> dict:
    """
    Creates a dictionary mapping from a DataFrame based on a keyword and a column to return.

    Args:
        df_from (DataFrame): The input DataFrame.
        keyword (str): The column to use as keys for the dictionary.
        column_returned (str): The column to use as values for the dictionary.

    Returns:
        dict: The created dictionary.
    """
    x: DataFrame = df_from.copy()
    
    return x.set_index(keyword)[column_returned].to_dict()

def is_europe(latitude: float, longitude: float) -> bool:
    """
    Checks if the given latitude and longitude are within the bounds of Europe.

    Args:
        latitude (float): The latitude to check.
        longitude (float): The longitude to check.

    Returns:
        bool: True if the coordinates are within Europe, False otherwise.
    """
    south: float = 34.0
    north: float = 72.0
    east: float = -25.0
    west: float = 45.0

    return south <= latitude <= north and east <= longitude <= west

def year_month(dataframe: DataFrame) -> DataFrame:
    """
    Adds 'year' and 'month' columns to the DataFrame based on the 'startDate' column.

    Args:
        dataframe (DataFrame): The input DataFrame.

    Returns:
        DataFrame: The modified DataFrame with 'year' and 'month' columns.
    """
    x: DataFrame = dataframe.copy()

    x['startDate'] = to_datetime(x['startDate'], errors='coerce')

    x['month'] = x['startDate'].dt.month
    x['year'] = x['startDate'].dt.year

    return x

# %% QueryzeMe.py
def load_short_df(directory: str) -> DataFrame | None:
    """
    Loads the latest short DataFrame from a directory.

    Args:
        directory (str): The directory path containing the CSV files.

    Returns:
        DataFrame | None: The loaded DataFrame, or None if an error occurs.
    """
    try:
        directory_sorted: list[str] = sorted(listdir(directory))
        if not directory_sorted:
            raise FileNotFoundError(f'No short dataframes found in {path.relpath(short_df, path.dirname(working_directory))}')
        print('Available short dataframes:', *directory_sorted, sep='\n')
        short_df: str = path.join(directory, directory_sorted[0])
        df_spotify: DataFrame = read_csv(short_df, sep=';')
    except Exception as e:
        print(f'Error loading short dataframe: {e}')
        return None
    
    working_directory: str = root_dir

    df_spotify['specific_genre'] = df_spotify['specific_genre'].apply(lambda x: x.replace('set()', ''))
    df_spotify['genres'] = df_spotify['genres'].apply(lambda x: x.replace('[]', ''))
    print(f'\nLoaded {path.relpath(short_df, path.dirname(working_directory))}:')

    return df_spotify

def query_game(df: DataFrame, field_name: str, input_value: str) -> DataFrame:
    """
    Filters the DataFrame based on the input value in the specified field.

    Args:
        df (DataFrame): The input DataFrame.
        field_name (str): The field to filter on.
        input_value (str): The value to filter by.

    Returns:
        DataFrame: The filtered DataFrame.
    """
    Y: DataFrame = df.copy()

    for value in input_value.split():
        Y = Y[Y[field_name].str.contains(value, case=False, na=False)]

    Y = Y.reset_index(drop=True)
    Y.index = Y.index + 1

    return Y

def show_all_genres(df: DataFrame) -> list[str] | None:
    """
    Extracts all unique genres from the 'specific_genre' column in the DataFrame.

    Args:
        df (DataFrame): The input DataFrame.

    Returns:
        list[str] | None: A list of unique genres, or None if the 'specific_genre' column is not found.
    """
    x: DataFrame = df.copy()
    if 'specific_genre' not in x.columns:
        print('No specific_genre column found in dataframe\n')
        return None

    col = x['specific_genre']

    if not isinstance(col.iloc[0], (set, list)):
        def safe_literal_eval(val: str) -> set | None:
            """
            Safely evaluates a string to a Python literal.

            Args:
                val (str): The string to evaluate.

            Returns:
                set | None: The evaluated set, or None if evaluation fails.
            """
            try:
                return literal_eval(val)
            except (ValueError, SyntaxError):
                print(f'Error evaluating the value: {"empty specific_genre" if not val else val}')
                return None

        col = col.apply(safe_literal_eval)
        col = col.dropna()

    cumulative: list[str] = []
    for genreset in col:
        genrelist: list[str] = list(genreset)
        if genrelist not in cumulative:
            cumulative.extend(genrelist)

    uniques: set[str] = set(cumulative)
    uniqueslist: list[str] = list(sorted(uniques))

    return uniqueslist

# %% MASTER.py
