# %% MODULES
from subprocess import run, CalledProcessError
from logging import info, error
from os import path, getcwd
from pandas import DataFrame, read_csv
from random import choice, uniform
from time import sleep
from requests import get, RequestException
from bs4 import BeautifulSoup
from json import loads

# %% VARIABLES
working_directory = path.dirname(current_directory := getcwd())
data_dir = path.join(working_directory, 'data')

BiT_Home = 'https://www.bandsintown.com'

paths = {   
    'data': {
        'BiT_Archive': path.join(data_dir, 'BiT_Archive'),
    },
    'sitemap': BiT_Home + '/sitemap/sitemap.xml.gz',
}

csv_files = {
    'all_events_dicts': path.join(data_dir, 'world_events_followlist_extended.csv'),
    'all_events_short': path.join(data_dir, 'world_events_followlist_short.csv'),
    'BiT_Spotify_innerjoin': path.join(paths['data']['BiT_Archive'], 'BiT_Spotify_innerjoin.csv'),
}

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

cookies = {}

# %% FUNCTIONS
def human_readable_size(file):

    size = path.getsize(file)
    for unit in ['', 'K', 'M', 'G', 'T', 'P', 'E', 'Z']:
        if size < 1024.0:
            return f"{size:.2f}{unit}B"
        size /= 1024.0

    return f"{size:.2f}YB"

def please_wait(mode: str) -> None:
   
    if mode is None:
        print('No wait_size specified, using deafult \'S\'\n')
        mode = 'S'
    if mode == 'M':
        sleep(uniform(2.5, 3.75))
    elif mode == 'L':
        sleep(uniform(10, 15))
    elif mode == 'S':
        sleep(0.3)

def slept_req(url, wait_size='S'):

    first_touch = url == BiT_Home

    print(f'Request for {'cookies...' if first_touch else f'{url}...'}')

    if first_touch:
        r = get(url, headers={**headers_dict, 'User-Agent': choice(user_agents_list)})
    else:
        r = get(url, headers={**headers_dict, 'User-Agent': choice(user_agents_list), **cookies})

    if r.status_code != 200:
        raise RequestException(f"\nError (\'slept_req\') in request: {r.status_code}")

    wait_size = 'S' if first_touch else wait_size
    
    please_wait(wait_size)
    
    return r

def dicts_from_soup(jsoups: list) -> list[dict]:

    if not all(isinstance(soup, (list, dict)) for soup in jsoups):
        raise ValueError("\nData (\'dicts_from_soup\') is not a list nor a dict")

    artist_dicts = []
    for soup in jsoups:

        if isinstance(soup, list):
            for dictionary in soup:
                artist_dicts.append(dictionary)

        elif isinstance(soup, dict):
            artist_dicts.append(soup)
        else:
            print(f'ERROR: {type(soup)} not dict nor list')

        events_dicts_list = [artist_dicts[i] for i in range(len(artist_dicts)) if artist_dicts[i]['@type'] == 'MusicEvent']

    return events_dicts_list

def json_response_eval(response_text):

    zuppa = BeautifulSoup(response_text, 'html.parser')
    script_soup = zuppa.find_all('script', type='application/ld+json')
    
    if not isinstance(script_soup, list):
        raise ValueError("\nNo \'script\' tag in html (\'json_response_eval\')")
    
    jsoups = [loads(script_soup[i].text) for i in range(len(script_soup))]

    dict_events = dicts_from_soup(jsoups)

    if dict_events is not None:
        print(f'\t{len(dict_events)} events found!')
    
    return dict_events if dict_events else None

def fetch_all_urls(url_series):

    if url_series.empty:
        raise ValueError("\nNo \'url_series\' passed (\'fetch_all_urls\')")
 
    datalist = []

    for i,url in enumerate(url_series):
        name = url.split('/')[-1].split('-',1)[1]
        print(f'\n{i+1}/{len(url_series)}: {name}')

        try:
            r = slept_req(url, wait_size='L')
            r.raise_for_status()
            rtext = r.text 
            rstatus = r.status_code

            if rstatus == 403:
                print(f'Status 403: {name}')
                print('\n!!Exiting program as you have been blocked!!\n')
                exit()

            if rtext is not None:
                rdata = json_response_eval(rtext)

                if rdata is not None:
                    datalist.extend(rdata)
                else:
                    print(f'\tResponse data is None: no events for {name}')
                    
        except RequestException as e:
            print(f"\nError (\'fetch_all_urls\') in request: {e}")
            return []

    return datalist

def session_cookies(url):
    
    r = slept_req(url, wait_size='S')

    return dict(r.cookies)

def unwrap(diction: dict) -> dict:

    location_data_keys = ['addressCountry', 'addressLocality', 'streetAddress', 'postalCode']

    dick = diction.copy()

    if not isinstance(dick, dict):
        print(f'\nNot a dict but {type(dick).__name__}')
        return
    elif 'location' not in list(dick.keys()):
        print(f'\nNo location key: {list(dick.keys())}')
        return
    
    dick['artist'] = dick['performer']['name']

    location = dick['location']['address']
    for i in location.keys():
        if len(i) > 0 and i in location_data_keys:
            dick[i] = location[i]

    dick['coordinates'] = ( dick['location']['geo']['latitude'], dick['location']['geo']['longitude'] )

    #del dick['location']
    #del dick['performer']

    return dick

def keypop(dictionary: dict) -> dict:

    location_data_keys = ['addressCountry', 'addressLocality', 'streetAddress', 'postalCode']
    artist_data_keys = ['name', 'url', 'startDate']
    #artist_data_keys = ['name', 'startDate', 'endDate', 'url', 'description', 'image', 'eventAttendanceMode', 'eventStatus']

    dick = dictionary.copy()

    before_keys = dictionary.keys()
    for k in before_keys:
        if k not in artist_data_keys + location_data_keys + ['coordinates', 'artist']:
            dick.pop(k)

    return dick

def artist_event_df(event_dict_list: list[dict] | dict | int) -> DataFrame:

    ev_list = list(filter(lambda x: x is not None, event_dict_list if isinstance(event_dict_list, list) else [event_dict_list]))

    ev_df_list = []
    for ev in ev_list:
        ev = unwrap(ev)
        ev = keypop(ev)
        ev_df_list.append(ev)

    ev_df = DataFrame.from_records(ev_df_list)

    return ev_df

def save_dfs(datalist):
    data_df_alldicts = DataFrame(datalist)
    print(f'\nHead of \'all_events_dicts\':\n{data_df_alldicts.head(3)}\n')
    data_df_alldicts.to_csv(csv_files['all_events_dicts'], mode='w', sep=';', index=False)
    
    data_df = artist_event_df(datalist)
    print(f'Head of \'all_events_short\':\n{data_df.head(3)}\n')
    data_df.to_csv(csv_files['all_events_short'], mode='w', sep=';', index=False)
    
    print(f'Dataframes saved! in folder {path.relpath(csv_files['all_events_dicts'], working_directory)}')

def subprocess_merging():
    try:
        run(path.join(getcwd(), 'BiT_Spotify_Merge.py'), check=True)
        info('Successfully executed \'BiT_Spotify_Merge.py\'')
        print('-'*5, 'Welcome back!', '-'*5, end='\n\n')
    except CalledProcessError as e:
        error(f'Errore durante l\'esecuzione di \'BiT_Spotify_Merge.py\': {e.returncode} - {e.stderr}')

# %% MAIN
def main():

    if not path.exists(csv_files['BiT_Spotify_innerjoin']):
        subprocess_merging()

    inner_bit_vs_spot = read_csv(csv_files['BiT_Spotify_innerjoin'], sep=';')

    artists_set = set(inner_bit_vs_spot['name'])
    print(f'\nThese {len(artists_set)} artists are in BiT and might have upcoming events:')
    sleep(2)
    print(', '.join(artists_set), '\n')
    
    cookies.update(session_cookies(BiT_Home))

    url_series = inner_bit_vs_spot['BiT_url']

    print(f'Number of URLs to scrape: {len(url_series)}')

    def do_that():
        datalist = fetch_all_urls(url_series)
        save_dfs(datalist)
        for file in [csv_files['all_events_dicts'], csv_files['all_events_short']]:
            print(f'\n\t\'{path.basename(file)}\' created in {path.relpath(working_directory, data_dir)}\n')
            print(f'\tSize: {human_readable_size(file)}')
            print(f'\tPath: {path.relpath(file, working_directory)}\n')

    existence = path.exists(csv_files['all_events_dicts']) and path.exists(csv_files['all_events_short'])
    if existence:
        print(f'\n\'{path.relpath(csv_files['all_events_dicts'], data_dir)}\' and \'{path.relpath(csv_files['all_events_short'], data_dir)}\' already exist\n')
        again = input('Do you want to overwrite them? This is very slow as scraping (N/n to skip): ')
        if again.lower() == 'n':
            print(f'\n------------------------------------------------------ !END! ------------------------------------------------------\n')
            return
        else:
            do_that()

    else:
        do_that()
            

    print(f'\n------------------------------------------------------ !END! ------------------------------------------------------\n')

    return

# %% RUN
if __name__ == '__main__':
    main()
