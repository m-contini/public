# %% MODULES
from os import path, getcwd
from pandas import read_csv, Timestamp
from ast import literal_eval

from modules import do_subprocess, mapper, complexity, is_europe, year_month

# %% VARIABLES

parent_dir = path.dirname(getcwd())
data_dir = path.join(parent_dir, 'data')

BiT_data = path.join(data_dir, 'BiT_Archive')

csv_files = {
    'all_events_short': path.join(data_dir, 'world_events_followlist_short.csv'),
    'BiT_Spotify_innerjoin': path.join(BiT_data, 'BiT_Spotify_innerjoin.csv'),
    'europe_events': path.join(data_dir, 'FinalOutput', 'Europe_events.csv'),
    'nearHome_events': path.join(data_dir, 'FinalOutput', 'nearHome_events.csv'),
}

today = Timestamp.today()

# %% MAIN
def main():

    if not path.exists(csv_files['all_events_short']):
        print(f'\nNo \'world_events_followlist_short.csv\' found in folder {parent_dir}.\nLaunching \'BiT_Archive_Scraping.py\'... BRB!\n')
        do_subprocess('BiT_Archive_Scraping.py')

    all_events_df = read_csv(csv_files['all_events_short'], sep=';', encoding='utf-8')
    all_events_df = complexity(all_events_df)
    all_events_df = all_events_df[all_events_df['startDate'] > today]

    print('Sorting by startDate...\n')        
    all_events_df.sort_values(by='startDate', ascending=True)

    BiT_Spot_inner = read_csv(csv_files['BiT_Spotify_innerjoin'], sep=';')
    all_events_df['genres'] = all_events_df['artist'].map(mapper(BiT_Spot_inner, 'name', 'genres'))
    all_events_df['popularity'] = all_events_df['artist'].map(mapper(BiT_Spot_inner, 'name', 'popularity'))

    print(all_events_df.head())
    
    '''
    genres_map = BiT_Spot_inner.set_index('name')['genres'].to_dict()
    popularity_map = BiT_Spot_inner.set_index('name')['popularity'].to_dict()
    '''

    df_europe = all_events_df.copy()
    df_europe = df_europe[df_europe.apply(lambda row: is_europe(row['latitude'], row['longitude']), axis=1)]
    df_europe = year_month(df_europe)
    df_europe['genres'] = df_europe['genres'].apply(lambda x: literal_eval(x))
    df_europe['specific_genre'] = df_europe['genres'].apply(lambda x: set(word for sublist in x for word in sublist.split() ))

    df_europe = df_europe[['artist', 'month', 'year', 'Date', 'days_to_event', 'addressCountry', 'addressLocality', 'geocoordinates', 'distance_from_Sesto', 'popularity', 'specific_genre']]

    df_europe.to_csv(csv_files['europe_events'], sep=';', index=False, encoding='utf-8')
    print(f'\nEurope events saved in \'{path.relpath(csv_files['europe_events'], path.dirname(parent_dir))}\'\n')
    print(df_europe.head())

    print('\nEvents near Sesto San Giovanni (within 10 km):\n')
    nearHome = all_events_df[ all_events_df['distance_from_Sesto'] < 10 ]
    nearHome.sort_values(by='startDate', ascending=True)
    nearHome.to_csv(csv_files['nearHome_events'], sep=';', index=False, encoding='utf-8')
    print(nearHome.head())
    print(f'\nEurope events saved in \'{path.relpath(csv_files['nearHome_events'], path.dirname(parent_dir))}\'\n')

    return

# %% RUN
if __name__ == '__main__':
    main()
