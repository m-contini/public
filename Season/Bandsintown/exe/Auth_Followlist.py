# %% MODULES
from os import getcwd, path
from modules import rw_tokens, file_existence, get_follow_dict, check_duplicates, df_writer

# %% VARIABLES
parent_dir = path.dirname(getcwd())
#data_dir = path.join(parent_dir, 'data')

#data_long = path.join(data_dir, 'long')
#data_short = path.join(data_dir, 'short')

tokens_json = path.join(parent_dir, 'data', 'tokens.json')

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
            print(f'Every artist \'item\' has {len(follow_dict['items'][0])} keys:\n\t{list(follow_dict['items'][0].keys())}\n')
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
