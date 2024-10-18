# %% MODULES
from os import path, getcwd
from pandas import read_csv
from time import sleep

from modules import human_readable_size, fetch_all_urls, session_cookies, save_dfs, do_subprocess

# %% VARIABLES
#working_directory = getcwd()
parent_dir = path.dirname(getcwd())
data_dir = path.join(parent_dir, 'data')

BiT_data = path.join(data_dir, 'BiT_Archive')

csv_files = {
    'all_events_dicts': path.join(data_dir, 'world_events_followlist_extended.csv'),
    'all_events_short': path.join(data_dir, 'world_events_followlist_short.csv'),
    'BiT_Spotify_innerjoin': path.join(BiT_data, 'BiT_Spotify_innerjoin.csv'),
}

BiT_Home = 'https://www.bandsintown.com/'

cookies = {}

# %% MAIN
def main():

    if not path.exists(csv_files['BiT_Spotify_innerjoin']):
        do_subprocess('BiT_Spotify_Merge.py')

    inner_bit_vs_spot = read_csv(csv_files['BiT_Spotify_innerjoin'], sep=';')

    artists_set = set(inner_bit_vs_spot['name'])
    print(f'\nThese {len(artists_set)} artists are in BiT and have upcoming events:')
    sleep(2)
    print(', '.join(artists_set), '\n')
    
    cookies.update(session_cookies(BiT_Home))

    url_series = inner_bit_vs_spot['BiT_url']

    print(f'Number of URLs to scrape: {len(url_series)}')

    existence = path.exists(csv_files['all_events_dicts']) and path.exists(csv_files['all_events_short'])
    if existence:
        print(f'\n\'{path.basename(csv_files['all_events_dicts'])}\' and \'{path.basename(csv_files['all_events_short'])}\' already exist in {path.relpath(data_dir, parent_dir)}\n')
        again = input('Do you want to overwrite them? This is very slow  (press N/n to skip): ')
        if again.lower() == 'n':
            print(f'\n------------------------------------------------------ !END! ------------------------------------------------------\n')
            return

    else:
        datalist = fetch_all_urls(url_series)
        save_dfs(datalist)
        for file in [csv_files['all_events_dicts'], csv_files['all_events_short']]:
            print(f'\n\t\'{path.basename(file)}\' created in {path.relpath(data_dir, parent_dir)}\n')
            print(f'\tSize: {human_readable_size(file)}')
            print(f'\tPath: {path.relpath(file, parent_dir)}\n')
            

    print(f'\n------------------------------------------------------ !END! ------------------------------------------------------\n')

    return

# %% RUN
if __name__ == '__main__':
    main()
