# %% MODULES
from subprocess import run, CalledProcessError
from logging import info, error
from os import path, getcwd
from pandas import read_csv, NaT, to_datetime, Timestamp
from numpy import nan
from geopy.distance import geodesic
from re import match
from ast import literal_eval

# %% VARIABLES
working_directory = path.dirname(current_directory := getcwd())
data_dir = path.join(working_directory, 'data')
BiT_Archive = path.join(data_dir, 'BiT_Archive')

csv_files = {
    'all_events_short': path.join(data_dir, 'world_events_followlist_short.csv'),
    'BiT_Spotify_innerjoin': path.join(BiT_Archive, 'BiT_Spotify_innerjoin.csv'),
    'europe_events': path.join(working_directory, 'Europe_events.csv'),
    'nearHome_events': path.join(working_directory, 'nearHome_events.csv'),
}

today = Timestamp.today()
sestosg = (45.53, 9.23)

# %% FUNCTIONS
def coordinates(x):

    if 'coordinates' not in x.columns:
        print('\nNo \'coordinates\' column in dataframe')
        return x
    
    if not all(isinstance(coord, tuple) for coord in x['coordinates']):
        print(f'\n\'coordinates\' column will be converted to tuples...')

        def convert_to_tuple(coord):
            try:
                match_flag = match(r'\(([^,]+), ([^,]+)\)', coord)
                if match_flag:
                    return (float(match_flag.group(1)), float(match_flag.group(2)))
                else:
                    raise ValueError(f"Invalid coordinate format: {coord}")
            except Exception as e:
                print(f"Error converting coordinate: {e}")
                return None
        
        x['coordinates'] = x['coordinates'].apply(convert_to_tuple)
    
    def distance_from_sesto(home, lat, lon):

        place = (lat, lon)
        distance = geodesic(home, place).km

        return round(distance, 1)
    
    x['latitude'] = x['coordinates'].apply(lambda coord: round(coord[0], 2) if coord else None)
    x['longitude'] = x['coordinates'].apply(lambda coord: round(coord[1], 2) if coord else None)
    x['distance_from_Sesto'] = x.apply(lambda y: distance_from_sesto(sestosg, y['latitude'], y['longitude']), axis=1)
    
    return x

def date_format(date_time_iso):

    x = date_time_iso

    try:
        #x = datetime.strptime(x, '%Y-%m-%dT%H:%M:%S')
        x = x.strftime('%d/%m/%Y %H:%M')

        return x
    
    except ValueError as e:
        print(f"Error in datetime format conversion: {e}")

        return None

def fill_empties(dataframe):

    x = dataframe.copy()
    missing_values = [nan, 'nan', 'NaN', None, 'NULL', 'null', 'N/A', 'n/a', 'NA', 'na', NaT]
    
    return x.replace(to_replace=missing_values, value='')

def complexity(dataframe):

    x = dataframe.copy()

    x = fill_empties(x)
    x = coordinates(x)
    x['startDate'] = to_datetime(x['startDate'], format='%Y-%m-%dT%H:%M:%S', errors='coerce')

    x['geocoordinates'] = x.apply(lambda x: (x['latitude'], x['longitude']), axis=1)
    x['days_to_event'] = x['startDate'].apply(lambda x: (x - today).days)
    x['Date'] = x['startDate'].apply(lambda y: date_format(y))
    x['artist'] = x['artist'].str.lower()

    x.drop(columns=['url', 'postalCode', 'coordinates'], inplace=True)

    return x

def mapper(df_from, keyword, column_returned):

    x = df_from.copy()
    
    return x.set_index(keyword)[column_returned].to_dict()

def is_europe(latitude, longitude):

    south = 34
    north = 72
    east = -25
    west = 45

    if south <= latitude <= north and east <= longitude <= west:

        return True

    return False

def year_month(dataframe):

    x = dataframe.copy()

    x['startDate'] = to_datetime(x['startDate'], errors='coerce')

    x['month'] = x['startDate'].dt.month
    x['year'] = x['startDate'].dt.year

    return x

def subprocess_scraping():
    try:
        run(path.join(getcwd(), 'BiT_Archive_Scraping.py'), check=True)
        info('Successfully executed \'BiT_Archive_Scraping.py\'')
        print('-'*5, 'Welcome back!', '-'*5, end='\n\n')
    except CalledProcessError as e:
        error(f'Errore durante l\'esecuzione di \'BiT_Archive_Scraping.py\': {e.returncode} - {e.stderr}')

# %% MAIN
def main():

    if not path.exists(csv_files['all_events_short']):
        print(f'\nNo \'world_events_followlist_short.csv\' found in folder {working_directory}.\nLaunching \'BiT_Archive_Scraping.py\'... BRB!\n')
        subprocess_scraping()

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
    print(f'\nEurope events saved in \'{path.relpath(csv_files['europe_events'], path.dirname(working_directory))}\'\n')
    print(df_europe.head())

    print('\nEvents near Sesto San Giovanni (within 10 km):\n')
    nearHome = all_events_df[ all_events_df['distance_from_Sesto'] < 10 ]
    nearHome.sort_values(by='startDate', ascending=True)
    nearHome.to_csv(csv_files['nearHome_events'], sep=';', index=False, encoding='utf-8')
    print(nearHome.head())
    print(f'\nEurope events saved in \'{path.relpath(csv_files['nearHome_events'], path.dirname(working_directory))}\'\n')

    return

# %% RUN
if __name__ == '__main__':
    main()
