# metal_v2.py

import os
import string
import time
import json
import requests
import pandas as pd
from bs4 import BeautifulSoup
import time

# Directory corrente e cartella dei dati
current_dir = os.getcwd()
metallari_folder = os.path.join(current_dir, 'metallari')

# URL base dell'archivio
base_url = 'https://www.metal-archives.com/browse/ajax-letter/l'

# Aggiunta dell'header User-Agent
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.159 Safari/537.36'
}

def progress_printer(start, end, total_records, iniziale):
    """
    Stampa il progresso del processo di recupero dei dati.
    """
    format_start = f'{start +1 :,.0f}'.replace(',', '.')
    format_end = f'{end:,.0f}'.replace(',', '.')
    format_total_records = f'{total_records:,.0f}'.replace(',', '.')

    if end < total_records:
        print(f'>> Processando i metallari che iniziano per {iniziale} da {format_start} a {format_end} su {format_total_records} records <<')
    else:
        print(f'>> Quasi finito, mancano i metallari che iniziano per {iniziale} da {format_start} a {format_end} su {format_total_records} records <<')

def fetch_some_entries(iniziale, request_counter):
    """
    Recupera le voci di gruppi metal dall'archivio per la lettera specificata.
    """
    encyclopedia = f'{base_url}/{iniziale}/json/1'
    some_entries = []
    start = 0
    step = 500  # Records per pagina
    total_records = None

    try:
        while True:
            # Effettua la richiesta GET con il parametro 'iDisplayStart' per la paginazione
            response = requests.get(encyclopedia, headers=headers, params={'iDisplayStart': start, 'iDisplayLength': step})
            request_counter += 1  # Incrementa il contatore delle richieste
            response.raise_for_status()  # Verifica se la richiesta è stata effettuata con successo
            body = response.json()

            # Inizializza total_records se non è impostato
            if total_records is None:
                total_records = body['iTotalRecords']

            # Controlla se la risposta contiene dati
            if not body['aaData']:
                break  # Esci dal ciclo se non vengono restituiti più dati


            # Calcola l'indice finale per il batch corrente
            end = min(start + step, total_records)
            # Stampa il progresso
            progress_printer(start, end, total_records, iniziale)

            # Elabora ogni voce
            for entry in body['aaData']:
                band_link = entry[0]
                band_name = BeautifulSoup(band_link, 'html.parser').text.strip()  # Usa BeautifulSoup per parsing corretto
                country = entry[1]
                genre = entry[2]
                status = entry[3]

                # Crea un elemento JSON
                json_entry = {
                    'Name': band_name,
                    'Country': country,
                    'Genre': genre,
                    'Status': status.split('>')[1].split('<')[0],
                    'URL': BeautifulSoup(band_link, 'html.parser').find('a')['href']  # Estrai il link corretto
                }

                # Stampa l'elemento JSON
                #   print(f'\nJSON entry:\n\n{json.dumps(json_entry, indent=4)}\n')

                # Appendi i metallari
                some_entries.append(json_entry)

            # Incrementa l'indice di inizio per il prossimo batch
            start += step

            # Esci dal ciclo se abbiamo recuperato tutti i dati
            if start >= total_records:
                break

            # Timer di 600 ms tra una richiesta e l'altra
            time.sleep(0.6)

    except requests.RequestException as e:
        print(f"\nErrore durante il recupero dei dati: {e}")
    
    return some_entries, request_counter
"""
def soup_cleaning(soup):
    # Funzione per pulire i dati recuperati da BeautifulSoup.
    try:
        band_name = soup.find('h1', class_='band_name').text.strip()
        country = soup.find('div', class_='country').text.strip()
        genre = soup.find('div', class_='genre').text.strip()
        status = soup.find('div', class_='status').text.strip()

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
        band_link = soup.find('a', class_='band_link')['href']

    except Exception as e:
        print(f"\nErrore durante il parsing dei dati: {e}")
        band_link, band_name, country, genre, status = None, None, None, None, None

    return band_link, band_name, country, genre, status
"""
# Opzionalmente, puoi salvare il DataFrame in un file CSV
def print_df_info(dataframe):
    """
    Stampa informazioni dettagliate sul DataFrame dei metallari.
    """
    print('\n-----------------------------')
    # Stampa le prime e ultime 5 righe del DataFrame
    print('>>df.head()\nPrime 5 righe del DataFrame:\n', dataframe.head())
    print('\n-----------------------------\n')
    time.sleep(0.6)
    print('>>df.tail()\nUltime 5 righe del DataFrame:\n', dataframe.tail())
    print('\n-----------------------------\n')
    time.sleep(0.6)

    # Stampa informazioni dettagliate sul DataFrame (tipo di dato, quantità di righe e colonne, ...)
    #print('df.info():\n', dataframe.info())
    #print('\n-----------------------------\n')
    #time.sleep(0.6)

    # Stampa statistiche descrittive sul DataFrame (count, mean, std, min, max, ...)
    print('>>df.describe()\nStatistiche descrittive sul DataFrame (count, mean, standard deviation, min, max, quartiles):\n', dataframe.describe())
    print('\n-----------------------------\n')
    time.sleep(0.6)

    # Stampa i tipi di dato di ogni colonna del DataFrame (int, float, object)    
    print('>>df.dtype\nTipi di dato di ogni colonna del DataFrame:\n', dataframe.dtypes)
    print('\n-----------------------------\n')
    time.sleep(0.6)

    # Stampa i nomi delle colonne del DataFrame
    print('>>df.columns\nNomi delle colonne del DataFrame:\n', dataframe.columns)
    print('\n-----------------------------\n')
    time.sleep(0.6)

    # Stampa il numero di righe (r) e colonne (c) del DataFrame come vettore (r, c)
    print('>>df.shape\nNumero di righe e colonne del DataFrame (r, c):\n', dataframe.shape)
    print('\n-----------------------------\n')
    time.sleep(0.6)

    # Stampa il numero di valori non nulli e nulli per ogni colonna
    print('>>df.notnull().sum()\nNumero di valori non nulli per ogni colonna:\n', dataframe.notnull().sum())
    print('\n-----------------------------\n')
    print('>>df.isnull().sum()\nNumero di valori nulli per ogni colonna:\n', dataframe.isnull().sum())
    print('\n-----------------------------\n')
    time.sleep(0.6)

    # Stampa il numero di valori unici per ogni colonna
    print('df.nunique():\n', dataframe.nunique())
    print('\n-----------------------------\n')
    time.sleep(0.6)

    # Stampa il numero di valori duplicati per ogni colonna
    print('df.duplicated().sum():\n', dataframe.duplicated().sum())
    print('\n-----------------------------\n')
    time.sleep(0.6)

    # Accorpiamo tutte queste informazioni in verticale, in una lista testuale
    df_infos = []
    for entry in dataframe.itertuples():
        df_infos.append({
            'Band': entry[1],
            'Paese': entry[2],
            'Genere': entry[3],  # Corretto da 'GENDER!' a 'Genere'
            'Stato': entry[4],
            'URL': entry[5]
        })

    return df_infos

def df_save_to_csv(records, text_start):
    """
    Salva i dati in un file CSV con il nome basato su 'text_start'.
    """
    # Creazione df
    data = pd.DataFrame(records)

    # Salvataggio in csv
    output_file = os.path.join(metallari_folder, f'{text_start}_data.csv')

    # Utilizzo del metodo di salvataggio CSV con encoding specifico
    data.to_csv(output_file, index=False, sep=';', encoding='utf-8')

    return output_file
  

def main():
    # Assicurati che la cartella esista
    if not os.path.exists(metallari_folder):
        os.makedirs(metallari_folder)
        print('\nCartella "metallari" creata!')
    else:
        print('\nCartella "metallari" già esistente!')

    # Scelta dell'utente
    which = 0
    while which < 1 or which > 2:
        try:
            which = int(input('\nSalverò tutti i metallari nell\'archivio, scegli se:\n1. Salvare tutti i metallari del mondo\n2. Indicare solo la lettera iniziale\nInserisci la tua scelta [1/2]: '))
        except ValueError:
            print('Input non valido. Per favore, inserisci un numero intero [1 o 2].')

    # Inizializza il contatore delle richieste
    request_counter = 0

    # Opzione scelta: Salvare tutti i metallari
    if which == 1:
        try:
            all_infos = []

            # Recupero e salvataggio per ogni lettera
            for char in string.ascii_uppercase:
                # Recupera tutte le voci con la lettera corrente
                entries, request_counter = fetch_some_entries(char, request_counter)
                piece = pd.DataFrame(entries)

                # Salviamo le info sui metallari iterando per ogni lettera in un file txt con metodo append
                letter_infos = print_df_info(piece)

                # Salva il DataFrame in un file CSV
                filename = df_save_to_csv(piece, char)

                # Aggiungiamo le informazioni sulle voci recuperate
                all_infos.extend(letter_infos)

            # Salvataggio del totale di voci recuperate
            total_records = len(all_infos)
            format_total_records = f'{total_records:,.0f}'.replace(',', '.')
            print(f'\nNumero totale di voci recuperate: {format_total_records}')
            time.sleep(0.6)

            # Salvataggio in txt
            txt_file = os.path.join(metallari_folder, '0_all_metallari_info.txt')
            with open(txt_file, 'a', encoding='utf-8') as f:
                for info in all_infos:
                    f.write(f'{info}\n')

            print(f'\nInfo salvate in {txt_file}!')
            time.sleep(0.6)

            print('\nFinito! I metallari del mondo sono stati recuperati!\n\n')
        except Exception as e:
            # Gestione eccezioni in caso di fallimento
            print(f'\nArgh niente dati...\t->\t{e}')

    # Opzione scelta: Indicare solo la lettera iniziale
    elif which == 2:
        # Lettura della lettera
        lettera = ''
        while not lettera.isalpha() or len(lettera) != 1:
            lettera = input('\nInserisci la lettera iniziale: ').strip().upper()

            # Verifica che l'input sia valido
            if lettera.isalpha() and len(lettera) == 1:
                break
            else:
                print('Input non valido. Per favore, inserisci una lettera.')

        try:
            # Recupera tutte le voci con la lettera corrente
            entries, request_counter = fetch_some_entries(lettera, request_counter)

            # Crea il DataFrame
            piece = pd.DataFrame(entries)

            # Salva le info sui metallari
            total_records = len(piece)
            format_total_records = f'{total_records:,.0f}'.replace(',', '.')
            print(f'\nNumero totale di voci recuperate: {format_total_records}')
            time.sleep(0.6)

            # Salva il DataFrame in un file CSV
            filename = df_save_to_csv(piece, lettera)
            print(f'\nDati salvati in {filename}:')
            time.sleep(0.6)

            # Aggiungiamo le informazioni sulle voci recuperate
            #df_infos = print_df_info(piece)
            print_df_info(piece)

            print(f'\nFinito! I metallari con la lettera {lettera} sono stati recuperati!\n')
            time.sleep(0.6)
        except Exception as e:
            # Gestione eccezioni in caso di fallimento
            print(f'\nArgh niente dati...\t->\t{e}')
        #else:
        #    print('Inserisci una lettera valida!')

    # Stampa il numero totale di richieste effettuate
    print(f'Numero totale di richieste HTTP eseguite: {request_counter}\n\n')


if __name__ == '__main__':
    main()
