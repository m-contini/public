# %% MODULES
from os import getcwd, path
from modules import session_cookies, do_subprocess, xml_map_save, xml_strings, artist_bit_urls, short_df_loader

# %% VARIABLES
BiT_Home = 'https://www.bandsintown.com/'
sitemap = BiT_Home + 'sitemap.xml'

parent_dir = path.dirname(getcwd())
xml_dir = path.join(parent_dir, 'xml')
data_dir = path.join(parent_dir, 'data')

BiT_data = path.join(data_dir, 'BiT_Archive')
data_long = path.join(data_dir, 'long')
data_short = path.join(data_dir, 'short')

cookies = {}

# %% MAIN
def main():

    if not data_short:
        do_subprocess('Auth_Followlist.py')

    cookies.update(session_cookies(BiT_Home))

    xml_map_save(sitemap)

    local_xml_sitemap = path.join(xml_dir, 'sitemap.xml')
    artists_urls = xml_strings(local_xml_sitemap)
    for url in artists_urls:
        xml_map_save(url)

    BiT_urls = artist_bit_urls(path.join(BiT_data, 'BiT_urls_names.csv'))
    
    followlist_short = short_df_loader(data_short)
    merged_bit_vs_spot = BiT_urls.merge(followlist_short, left_on='BiT_name', right_on='BiT_name_check', indicator=True, how='right')
    merged_bit_vs_spot.sort_values(by=['popularity', 'followers'], ascending=False, inplace=True)

    no_events = merged_bit_vs_spot[merged_bit_vs_spot['_merge'] == 'right_only'].reset_index(drop=True)
    no_events = no_events[['name', 'genres', 'genres_set', 'followers', 'popularity']]

    inner_bit_vs_spot = merged_bit_vs_spot[merged_bit_vs_spot['_merge'] == 'both'].reset_index(drop=True)
    inner_bit_vs_spot = inner_bit_vs_spot.drop(columns=['_merge', 'BiT_name_check', 'BiT_name', 'specific_genre'])

    print(f'\nThese artists are in BiT and have upcoming events:')
    print('\n'.join(inner_bit_vs_spot['name'].tolist()))
    print(f'\nThese artists are not in BiT because they have no events:')
    print('\n'.join(no_events['name'].tolist()))

    inner_bit_vs_spot.to_csv(path.join(BiT_data, 'BiT_Spotify_innerjoin.csv'), sep=';', index=False)

    i = 0
    duplicates_name = []
    nameslist = inner_bit_vs_spot['name'].to_list()
    for name in nameslist:
        count = nameslist.count(name)
        if count > 1:
            duplicates_name.append(name)
        i+=1

    print(f'\nThe following {len(set(duplicates_name))} artists appear twice in \'name\' column: that\'s beacause the \'BiT_url\' in BiT leads to the same band name:')
    print(merged_bit_vs_spot[merged_bit_vs_spot['name'].isin(duplicates_name)][['name', 'BiT_url']])

    print(f'\n------------------------------------------------------ !END! ------------------------------------------------------\n')

    return

# %% RUN
if __name__ == '__main__':
    main()
