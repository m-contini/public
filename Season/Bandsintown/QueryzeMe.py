# %% MODULES
from os import path, getcwd

from exe.modules import load_short_df, show_all_genres, query_game

# %% VARIABLES
working_directory = getcwd()
data_dir = path.join(working_directory, 'data')
short_dir = path.join(data_dir, 'short')

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
