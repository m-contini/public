# metal_v2.py

import os
import string
from time import sleep
import requests
import pandas as pd
from bs4 import BeautifulSoup

current_dir = os.getcwd()
metallari_folder = os.path.join(current_dir, 'metallari','csv_output')

base_url = 'https://www.metal-archives.com/browse/ajax-letter/l'

def progress_printer(start, step, end, total_records, iniziale):
    """
    Stampa il progresso del processo di recupero dei dati.
    """
    format_start = f'{start:,.0f}'.replace(',', '.')
    format_length = f'{step:,.0f}'.replace(',', '.')
    format_end = f'{end:,.0f}'.replace(',', '.')
    format_total_records = f'{total_records:,.0f}'.replace(',', '.')
    
    if end < total_records:
        print(f'\tProcessando i metallari che iniziano per {iniziale} da {format_start} a {format_end} su {format_total_records} records...')
    else:
        print(f'\tQuasi finito, mancano i metallari che iniziano per {iniziale}, da {format_end} a {format_length} su {format_total_records} records...')

def fetch_some_entries(iniziale):
    """
    Recupera le voci di gruppi metal dall'archivio per la lettera specificata.
    """
    encyclopedia = f'{base_url}/{iniziale}/json/1'
    some_entries = []
    start = 0
    step = 500  # Records per pagina
    end = step
    total_records = None

            # query params omessi... non sono importanti
            # La richiesta parte senza headers

    while True:
                # Effettua la richiesta GET con il parametro 'iDisplayStart' per paginazione
        response = requests.get(encyclopedia, params={'iDisplayStart': start})
        body = response.json()

                # Inizializza total_records se non è impostato
        if total_records is None:
            total_records = body['iTotalRecords']

                # Controlla se la risposta contiene dati
        if not body['aaData']:
            break  # Esci dal ciclo se non vengono restituiti più dati

                # Elabora ogni voce
        for entry in body['aaData']:
            band_link = entry[0]
            band_name = band_link.split('>')[1].split('<')[0]
            country = entry[1]
            genre = entry[2]
            status = entry[3].split('>')[1].split('<')[0]

                    # Effettua la richiesta GET per band_link e recupera i dati del singolo metallaro
            soup = BeautifulSoup(requests.get(band_link).text, 'html.parser')
            band_link, band_name, country, genre, status = soup_cleaning(soup)

                    # Appendi i metallari
            some_entries.append({
                'Name': band_name,
                'Country': country,
                'Genre': genre,
                'Status': status,
                'URL': band_link
            })

                # Stampa il progresso
        progress_printer(start, step, end, total_records, iniziale)
        
                # Incrementa l'indice di inizio per il prossimo batch
        start += step
        end += step

                # Esci dal ciclo se abbiamo recuperato tutti i dati
        if start >= total_records:
            break

    return some_entries

def soup_cleaning(soup):
    """
    Funzione per pulire i dati recuperati da BeautifulSoup.
    """
    band_name = soup.find('h1', class_='band-name').text
    country = soup.find('div', class_='country').text
    genre = soup.find('div', class_='genre').text
    status = soup.find('div', class_='status').text

            # Rimuovi i caratteri non ASCII
    band_name = band_name.encode('ascii', 'ignore').decode('ascii')
    country = country.encode('ascii', 'ignore').decode('ascii')
    genre = genre.encode('ascii', 'ignore').decode('ascii')
    status = status.encode('ascii', 'ignore').decode('ascii')

            # Rimuovi i caratteri speciali
    band_name = band_name.replace('\xa0', ' ')
    country = country.replace('\xa0', ' ')
    genre = genre.replace('\xa0', ' ')
    status = status.replace('\xa0', ' ')

            # Rimuovi gli spazi vuoti iniziali e finali
    band_name = band_name.strip()
    country = country.strip()
    genre = genre.strip()
    status = status.strip()

            # Rimuovi gli spazi vuoti interni
    band_name = ' '.join(band_name.split())
    country = ' '.join(country.split())
    genre = ' '.join(genre.split())
    status = ' '.join(status.split())

            # Rimuovi le virgolette iniziali e finali
    band_name = band_name.strip("'")
    country = country.strip("'")
    genre = genre.strip("'")
    status = status.strip("'")

            # Rimuovi le virgolette interne
    band_name = ' '.join(band_name.split("'"))
    country = ' '.join(country.split("'"))
    genre = ' '.join(genre.split("'"))
    status = ' '.join(status.split("'"))

            # Ricava band_link da <a href={band_link}></a>
    band_link = soup.find('a', class_='band-link')['href']
    
    return band_link,band_name,country,genre,status

        # Opzionalmente, puoi salvare il DataFrame in un file CSV

def df_metallari_info(dataframe):
    """
    Stampa informazioni dettagliate sul DataFrame dei metallari.
    """
            # Stampa le prime 5 righe del DataFrame
    print('df.head():\n', dataframe.head())
    print('-----------------------------')
    sleep(1)

            # Stampa le ultime 5 righe del DataFrame
    print('df.tail():\n', dataframe.tail())
    print('-----------------------------')
    sleep(1)

            # Stampa informazioni dettagliate sul DataFrame (tipo di dato, quantità di righe e colonne, ...)
    print('df.info():\n', dataframe.info())
    print('-----------------------------')
    sleep(1)

            # Stampa statistiche descrittive sul DataFrame (count, mean, std, min, max, ...)
    print('df.describe():\n', dataframe.describe())
    print('-----------------------------')
    sleep(1)

            # Stampa i tipi di dato di ogni colonna del DataFrame (int, float, object)    
    print('df.dtypes:\n', dataframe.dtypes)
    print('-----------------------------')
    sleep(1)

            # Stampa i nomi delle colonne del DataFrame
    print('df.columns:\n', dataframe.columns)
    print('-----------------------------')
    sleep(1)

            # Stampa il numero di righe (r) e colonne (c) del DataFrame come vettore (r, c)
    print('df.shape:\n', dataframe.shape)
    print('-----------------------------')
    sleep(1)

            # Stampa il numero di valori unici per ogni colonna
    print('df.nunique():\n', dataframe.nunique())
    print('-----------------------------')
    sleep(1)

            # Stampa il numero di valori nulli per ogni colonna (NaN = Not a Number)
    print('df.isnull().sum():\n', dataframe.isnull().sum())
    print('-----------------------------')
    sleep(1)

            # Stampa il numero di valori non nulli per ogni colonna
    print('df.notnull().sum():\n', dataframe.notnull().sum())
    print('-----------------------------')
    sleep(1)

            # Stampa il numero di valori duplicati per ogni colonna
    print('df.duplicated().sum():\n', dataframe.duplicated().sum())
    print('-----------------------------')
    sleep(1)

            # Accorpiamo tutte queste informazioni in verticale, in una lista testuale
    letter_infos = []
    for entry in dataframe.itertuples():
        letter_infos.append({
            'Band': entry[1],
            'Paese': entry[2],
            'GENDER!': entry[3],
            'Stato': entry[4],
            'URL': entry[5]
        })

    return letter_infos

def df_save_to_csv(records, text_start):
    """
    Salva i dati in un file CSV con il nome basato su 'text_start'.
    """
            # Creazione df
    data = pd.DataFrame(records)

            # Salvataggio in csv
    output_file = os.path.join(metallari_folder, 'alphabet', f'{text_start}_data.csv')

            # Utilizzo del metodo di salvataggio CSV con encoding specifico
    data.to_csv(output_file, index=False, sep=';', encoding='utf-8')

    print(f'\nDati salvati in {output_file}!')
    return output_file
  

def main():
            # Assicurati che la cartella esista
    if not os.path.exists(metallari_folder):
        os.makedirs(metallari_folder)
        print('\nCartella "metallari/csv_output" creata!')
    else:
        print('\nCartella "metallari/csv_output" già esistente!')

            # Scelta dell'utente
    which = -1
    while which < 1 or which > 2:
        try:
            which = int(input('\nSalverò tutti i metallari nell\'archivio, scegli se:\n1. Salvare tutti i metallari del mondo\n2. Indicare solo la lettera iniziale\nInserisci la tua scelta [1/2]: '))
        except ValueError:
            print('Input non valido. Per favore, inserisci un numero intero [1 o 2].')

            # Opzione scelta: Salvare tutti i metallari
    if which == 1:
        if not os.path.exists(os.path.join(metallari_folder, 'all_infos')):
                os.makedirs(os.path.join(metallari_folder, 'all'))
                print('\nCartella "metallari/csv_output/all_infos" creata!')
        try:
            all_infos = []

                    # Recupero e salvataggio per ogni lettera
            for char in string.ascii_uppercase:
                        # Recupera tutte le voci con la lettera corrente
                entries = fetch_some_entries(char)
                piece = pd.DataFrame(entries)

                        # Salviamo le info sui metallari iterando per ogni lettera in un file txt con metodo append
                letter_infos = df_metallari_info(piece)

                        # Salva il DataFrame in un file CSV
                filename = df_save_to_csv(piece, char)

                        # Aggiungiamo le informazioni sulle voci recuperate
                all_infos.extend(letter_infos)

                    # Salvataggio del totale di voci recuperate
            total_records = len(all_infos)
            format_total_records = f'{total_records:,.0f}'.replace(',', '.')
            print(f'\nNumero totale di voci recuperate: {format_total_records}')
            sleep(2)

                    # Salvataggio in txt
            txt_file = os.path.join(metallari_folder, 'all','all_metallari_info.txt')
            with open(txt_file, 'a', encoding='utf-8') as f:
                for info in all_infos:
                    f.write(f'{info}\n')

            print(f'\nDati salvati in {txt_file}!')
            sleep(1)

            print('\nFinito! I metallari del mondo sono stati recuperati!\n\n')
        except Exception as e:
                    # Gestione eccezioni in caso di fallimento
            print(f'\nArgh niente dati...\t->\t{e}')

            # Opzione scelta: Indicare solo la lettera iniziale
    elif which == 2:
        if not os.path.exists(os.path.join(metallari_folder, 'alphabet')):
                os.makedirs(os.path.join(metallari_folder, 'alphabet'))
                print('\nCartella "metallari/csv_output/alphabet" creata!')        
                # Lettura della lettera
        lettera = input('\nInserisci la lettera iniziale: ').strip().upper()

                # Verifica che l'input sia valido
        if lettera.isalpha() and len(lettera) == 1:
            try:
                        # Recupera tutte le voci con la lettera corrente
                entries = fetch_some_entries(lettera)

                        # Crea il DataFrame
                piece = pd.DataFrame(entries)

                        # Salva le info sui metallari
                total_records = len(piece)
                format_total_records = f'{total_records:,.0f}'.replace(',', '.')
                print(f'\nNumero totale di voci recuperate: {format_total_records}')
                sleep(2)

                        # Salva il DataFrame in un file CSV
                filename = df_save_to_csv(piece, lettera)
                print(f'\nDati salvati in {filename}!')
                sleep(1)

                print(f'\nFinito! I metallari con la lettera {lettera} sono stati recuperati!\n\n')
                sleep(1)
            except Exception as e:
                        # Gestione eccezioni in caso di fallimento
                print(f'\nArgh niente dati...\t->\t{e}')
        else:
            print('Inserisci una lettera valida!')


if __name__ == '__main__':
    main()
