# %% MODULES
from pandas import read_csv
from os import path, listdir, getcwd
from ast import literal_eval

# %% VARIABLES
working_directory = getcwd()
data_dir = path.join(working_directory, 'data')
short_dir = path.join(data_dir, 'short')

# %% FUNCTIONS
def load_short_df(directory):
    try:
        directory_sorted = sorted(listdir(directory))
        if not directory_sorted:
            raise FileNotFoundError(f'No short dataframes found in {path.relpath(working_directory, short_df)}')
        print('Available short dataframes:', *directory_sorted, sep='\n')
        short_df = path.join(directory, directory_sorted[0])
        df_spotify = read_csv(short_df, sep=';')
    except Exception as e:
        print(f'Error loading short dataframe: {e}')
        return None
    
    df_spotify['specific_genre'] = df_spotify['specific_genre'].apply(lambda x: x.replace('set()', ''))
    df_spotify['genres'] = df_spotify['genres'].apply(lambda x: x.replace('[]', ''))
    print(f'\nLoaded {path.relpath(short_df, working_directory)}:')
    #print(df_spotify.head())

    return df_spotify

def query_game(df, field_name, input_value):
    Y = df.copy()

    for value in input_value.split():
        Y = Y[Y[field_name].str.contains(value, case=False, na=False)]

    Y = Y.reset_index(drop=True)
    Y.index = Y.index + 1

    return Y

def show_all_genres(df):
    x = df.copy()
    if 'specific_genre' not in x.columns:
        print('No specific_genre column found in dataframe\n')
        return

    col = x['specific_genre']

    if not isinstance(col.iloc[0], (set, list)):
        def safe_literal_eval(val):
            try:
                return literal_eval(val)
            except (ValueError, SyntaxError):
                print(f'Error evaluating the porcodio: {'empty specific_genre' if not val else val}')
                return None

        col = col.apply(safe_literal_eval)
        col = col.dropna()

    cumulative = []
    for genreset in col:
        genrelist = list(genreset)
        if genrelist not in cumulative:
            cumulative.extend(genrelist)

    uniques = set(cumulative)
    uniqueslist = list(sorted(uniques))

    return uniqueslist

# %% MAIN
def main():
    
    print('\nCurrent working directory:', working_directory)

    short = load_short_df(short_dir)
    if short is None:
        print('I see you fuck bitches; I also fuck bitches myself...\n(which means there is no short_df csv)')
        exit()
    
    prechoice = input('\nWould you like to see all keywords found in every artist\'s genrelist? (N/n to skip) ').lower()
    if prechoice != 'n':
        uniqueslist = show_all_genres(short)
        for i,rowlist in enumerate(uniqueslist):
            print(f'{i+1}: {rowlist}')

    choice = input('\nEnter querygame or go fuck off? (Q/q to fuckoff) ').lower()
    if choice == 'q':
        print('Ok go fuck yourself then')
        exit()

    print(f'\n{"-"*5}QUERY GAME!{"-"*5}\n')
    col_list = short.columns.tolist()

    cycle = True
    while cycle:
        print('\nColumns available for filtering:')
        print(*col_list, sep=', ')

        selected_column = input('\nBy which column would you like to filter the dataframe (default: \'specific_genre\')? (Q/q to quit): ').strip().lower() or 'specific_genre'
        if selected_column == 'q':
            cycle = False
            continue
        if selected_column not in col_list:
            print('Invalid column name. Please try again.')
            continue

        input_value = input(f'\nEnter the value to filter by {selected_column}: ')

        result = query_game(short, selected_column, input_value)
        result = result[['name', selected_column]]

        if result.empty:
            print(f'\nNo results found for {input_value} in {selected_column}\n')
        else:
            print('\n' + '-'*5 + 'RESULT' + '-'*5)
            print(f'Found {len(result)} rows matching {input_value} in {selected_column}:\n')
            print(result)

        input('Press any key to continue...')

# %% RUN
if __name__ == '__main__':
    main()
