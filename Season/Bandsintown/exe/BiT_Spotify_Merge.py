# %% MODULES
from subprocess import run, CalledProcessError
from os import listdir, getcwd, path, makedirs
from logging import info, error
from gzip import GzipFile
from time import sleep
from xml.etree import ElementTree as ET
from io import BytesIO
from random import choice, uniform
from requests import get
from pandas import DataFrame, read_csv
from ast import literal_eval
from xml.dom import minidom
from glob import glob

# %% VARIABLES
working_directory = path.dirname(current_directory := getcwd())
data_dir = path.join(working_directory, 'data')

BiT_Home = 'https://www.bandsintown.com'

paths = {   
    'xml_dir': path.join(working_directory, 'xml_dir'),
    'data': {
        'short': path.join(data_dir, 'short'),
        'BiT_Archive': path.join(data_dir, 'BiT_Archive')
    },
    'sitemap': BiT_Home + "/sitemap/sitemap.xml.gz",
}

BiT_data = {
    'BiT_urls_names': path.join(paths['data']['BiT_Archive'], 'BiT_urls_names.csv'),
    'BiT_Spotify_innerjoin': path.join(paths['data']['BiT_Archive'], 'BiT_Spotify_innerjoin.csv'),
}

for folder in [data_dir, paths['xml_dir'], paths['data']['short'], paths['data']['BiT_Archive']]:
    if not path.exists(folder):
        makedirs(folder, exist_ok=True)

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
def subprocess_followlist():
    try:
        run(path.join(getcwd(), 'Auth_Followlist.py'), check=True)
        info('Successfully executed \'Auth_Followlist.py\'')
        print('-'*5, 'Welcome back!', '-'*5, end='\n\n')
    except CalledProcessError as e:
        error(f'Errore durante l\'esecuzione di \'Auth_Followlist.py\': {e.returncode} - {e.stderr}')

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

    print(f'Request for {'cookies...' if first_touch else f'{url}..'}')

    if first_touch:
        r = get(url, headers={**headers_dict, 'User-Agent': choice(user_agents_list)})
    else:
        r = get(url, headers={**headers_dict, 'User-Agent': choice(user_agents_list), **cookies})

    if r.status_code != 200:
        print(f'Error in request: {r.status_code}\n')
        return None

    wait_size = 'S' if first_touch else wait_size
    
    please_wait(wait_size)
    
    return r

def session_cookies(url):
    
    r = slept_req(url)
    r_cookies = r.cookies

    return dict(r_cookies)

def xml_map_save(url):

    def human_readable_size(file):
        size = path.getsize(file)
        for unit in ['', 'K', 'M', 'G', 'T', 'P', 'E', 'Z']:
            if size < 1024.0:
                return f"{size:.2f}{unit}B"
            size /= 1024.0
        return f"{size:.2f}YB"

    fname = path.join(paths['xml_dir'], path.basename(url).replace('.gz', ''))

    if path.exists(fname):
        print(f'\'{path.basename(fname)}\' already exists!\n')
        return
    
    r = slept_req(url, wait_size='M')
    r_content = r.content

    with GzipFile(fileobj=BytesIO(r_content)) as f:
        xml_data = f.read()
        xml_data = minidom.parseString(xml_data).toprettyxml(indent='\t')
    
    with open(fname, 'w') as f:
        f.write(xml_data)

    print(f'Saved: {path.basename(fname)} -> {human_readable_size(fname)} kBytes\n')                                    

def xml_strings(fname):

    if not fname.endswith('.xml'):
        print(f'{fname} is not an XML file\n')
        return

    with open(fname, 'r') as f:
        xml_file = f.read()

    root = ET.fromstring(xml_file) 
    
    locs = []

    key = 'artists' if 'artists' in fname else 'sitemap'

    for sitemap in root.findall(f'.//{{http://www.sitemaps.org/schemas/sitemap/0.9}}{'url' if key == 'artists' else 'sitemap'}'):
        loc = sitemap.find('{http://www.sitemaps.org/schemas/sitemap/0.9}loc').text
        
        if path.exists(path.join(paths['xml_dir'], path.basename(loc).replace('.gz', ''))):
            continue
        
        if key == 'sitemap' and not 'artists' in loc.split('/')[-1]:
            continue
        
        locs.append(loc)

    if len(locs) > 0:
        print(f'\n{len(locs):,} elements found in {path.basename(fname)}.\n')

    return locs

def bit_urls_df(urls_list):

    df = DataFrame(urls_list, columns=['BiT_url'])

    df['BiT_name'] = df['BiT_url'].apply(lambda x: path.basename(x))
    df['BiT_name'] = df['BiT_name'].apply(lambda x: x.split('-', 1)[-1] if '-' in x else '')
    df = df[ ~df['BiT_name'].eq('') ]

    return df

def artist_bit_urls(csv_path):

    if path.exists(csv_path):
        BiT_urls = read_csv(csv_path, sep=';')

    else:
        artists_xml_from_sitemap = glob(path.join(paths['xml_dir'], 'artists*.xml'))
        sitemap_urls_list = []

        for i, file in enumerate(artists_xml_from_sitemap):
            print(f'{i+1}/{len(artists_xml_from_sitemap)}: {path.basename(file)}')
            urls = xml_strings(file)
            sitemap_urls_list.extend(urls)

        BiT_urls = bit_urls_df(sitemap_urls_list)
        BiT_urls.to_csv(csv_path, sep=';', index=False)
    
    print(f'{'Loaded' if path.exists(csv_path) else 'Saved'} {len(BiT_urls):,} urls {'from' if path.exists(csv_path) else 'to'} {path.basename(csv_path)}\nColumns: {list(BiT_urls.columns)}\n')
    
    return BiT_urls

def short_df_loader(csv_path):

    latest_short_df = listdir(csv_path)[-1]
    followlist_short_csv = path.join(csv_path, latest_short_df)
    followlist_short = read_csv(followlist_short_csv, sep=';')

    followlist_short['genres'] = followlist_short['genres'].apply(lambda x: literal_eval(x))
    followlist_short['genres_set'] = followlist_short['genres'].apply(lambda x: set(word for sublist in x for word in sublist.split()))
    followlist_short['BiT_name_check'] = followlist_short['name'].apply(lambda x: x.replace(' ', '-'))

    return followlist_short

# %% MAIN
def main():

    if not paths['data']['short']:
        subprocess_followlist()

    cookies.update(session_cookies(BiT_Home))

    xml_map_save(paths['sitemap'])

    local_xml_sitemap = path.join(paths['xml_dir'], 'sitemap.xml')
    artists_urls = xml_strings(local_xml_sitemap)
    for url in artists_urls:
        xml_map_save(url)

    BiT_urls = artist_bit_urls(BiT_data['BiT_urls_names'])
    
    followlist_short = short_df_loader(paths['data']['short'])
    merged_bit_vs_spot = BiT_urls.merge(followlist_short, left_on='BiT_name', right_on='BiT_name_check', indicator=True, how='right')
    merged_bit_vs_spot.sort_values(by=['popularity', 'followers'], ascending=False, inplace=True)

    no_events = merged_bit_vs_spot[merged_bit_vs_spot['_merge'] == 'right_only'].reset_index(drop=True)
    no_events = no_events[['name', 'genres', 'genres_set', 'followers', 'popularity']]

    inner_bit_vs_spot = merged_bit_vs_spot[merged_bit_vs_spot['_merge'] == 'both'].reset_index(drop=True)
    inner_bit_vs_spot = inner_bit_vs_spot.drop(columns=['_merge', 'BiT_name_check', 'BiT_name', 'specific_genre'])

    inner_bit_vs_spot.to_csv(BiT_data['BiT_Spotify_innerjoin'], sep=';', index=False)

    i = 0
    duplicates_name = []
    nameslist = inner_bit_vs_spot['name'].to_list()
    for name in nameslist:
        count = nameslist.count(name)
        if count > 1:
            duplicates_name.append(name)
        i+=1

    print(f'\nThese artists are not in BiT because they have no events:')
    print('\n'.join(sorted(no_events['name'].tolist())))
    print(f'\nThe following {len(set(duplicates_name))} artists appear twice in \'name\' column: that\'s beacause the \'BiT_url\' in BiT leads to the same band name:')
    print(merged_bit_vs_spot[merged_bit_vs_spot['name'].isin(duplicates_name)][['name', 'BiT_url']])
    print(f'\nThese artists are in BiT and have upcoming events:')
    print('\n'.join(inner_bit_vs_spot['name'].tolist()))
    print(f'\n------------------------------------------------------ !END! ------------------------------------------------------\n')

    return

# %% RUN
if __name__ == '__main__':
    main()
