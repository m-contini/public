# metal_v3_asyncio.py

import os
import string
import time
import aiohttp
import asyncio
#from bs4 import BeautifulSoup
import json
import pandas as pd

# Directory corrente e cartella dei dati
current_dir = os.getcwd()
metallari_folder = os.path.join(current_dir, 'csv_output')

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
    format_start = f'{start + 1 :,.0f}'.replace(',', '.')
    format_end = f'{end:,.0f}'.replace(',', '.')
    format_total_records = f'{total_records:,.0f}'.replace(',', '.')

    if end < total_records:
        print(f'>> Processando i metallari che iniziano per {iniziale} da {format_start} a {format_end} su {format_total_records} records <<')
    else:
        print(f'>> Quasi finito, mancano i metallari che iniziano per {iniziale} da {format_start} a {format_end} su {format_total_records} records <<')

async def fetch_entries_for_batch(session, iniziale, start, step):
    """
    Fetch a single batch of entries for a specific letter and starting index asynchronously.
    """
    encyclopedia = f'{base_url}/{iniziale}/json/1'
    try:
        async with session.get(encyclopedia, headers=headers, params={'iDisplayStart': start, 'iDisplayLength': step}) as response:
            response.raise_for_status()  # Verifica se la richiesta è stata effettuata con successo
            body = await response.json()
            return body['aaData'], body['iTotalRecords']
    except Exception as e:
        print(f"\nErrore durante il recupero dei dati: {e}")
        return [], 0

async def fetch_some_entries(iniziale):
    """
    Recupera le voci di gruppi metal dall'archivio per la lettera specificata usando asyncio per richieste parallele.
    """
    start = 0
    step = 500  # Records per pagina
    total_records = None
    some_entries = []

    async with aiohttp.ClientSession() as session:
        tasks = []

        # Avvia le richieste batch in parallelo
        while True:
            tasks.append(fetch_entries_for_batch(session, iniziale, start, step))
            start += step
            if total_records is not None and start >= total_records:
                break

        # Processa i risultati
        results = await asyncio.gather(*tasks)
        for batch_entries, batch_total_records in results:
            if total_records is None:
                total_records = batch_total_records

            some_entries.extend(batch_entries)

            # Stampa il progresso
            end = min(start, total_records)
            progress_printer(start - step, end, total_records, iniziale)

    return some_entries

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

def df_save_to_csv(records, text_start, path):
    """
    Salva i dati in un file CSV con il nome basato su 'text_start'.
    """
    # Creazione df
    data = pd.DataFrame(records)

    # Salvataggio in csv
    output_file = os.path.join(path, f'{text_start}_data.csv')
    # Utilizzo del metodo di salvataggio CSV con encoding 'uft-8' e delimiter ';'
    data.to_csv(output_file, index=False, sep=';', encoding='utf-8')

    return output_file

def pretty_json(json_data):
    """
    Formatta un oggetto JSON in modo leggibile.
    """
    # Assicurati che l'input sia un oggetto JSON, non una stringa
    if isinstance(json_data, str):
        return json.loads(json_data)
    return json.dumps(json_data, indent=4, ensure_ascii=False, separators=(',', ': '))

def measure_execution_time(func):
    """
    Calcola il tempo di esecuzione di una funzione.
    """
    # Non ho idea di che cazzo sia, è di ChatGPT
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        execution_time = end_time - start_time
        print(f"\nTempo di esecuzione: {execution_time:.2f} secondi\n")
        return result
    return wrapper

@measure_execution_time
def main():
    # Assicurati che la cartella esista
    if not os.path.exists(metallari_folder):
        os.makedirs(metallari_folder)
        print('\nCartella "metallari/csv_output" creata!\n')
    else:
        print('\nCartella "metallari/csv_output" già esistente!\n')

    # Scelta dell'utente
    which = 0
    while which < 1 or which > 2:
        try:
            which = int(input('\nSalverò tutti i metallari nell\'archivio, scegli se:\n1. Salvare tutti i metallari del mondo\n2. Indicare solo la lettera iniziale\nInserisci la tua scelta [1/2]: '))
        except ValueError:
            print('Input non valido. Per favore, inserisci un numero intero [1 o 2].')

    # Opzione scelta: Salvare tutti i metallari
    if which == 1:
        all_infos_dir = os.path.join(metallari_folder, 'all_infos')
        if not os.path.exists(all_infos_dir):
            os.makedirs(all_infos_dir)
            print('\nCartella "metallari/csv_output/all_infos" creata!\n')
        else:
            print('\nCartella "metallari/csv_output/all_infos" già esistente!\n')        
        try:
            all_infos = []

            # Recupero e salvataggio per ogni lettera
            for char in string.ascii_uppercase:
                # Recupera tutte le voci con la lettera corrente
                entries = asyncio.run(fetch_some_entries(char))
                piece = pd.DataFrame(entries)

                # Salviamo le info sui metallari iterando per ogni lettera in un file txt con metodo append
                letter_infos = print_df_info(piece)

                # Salva il DataFrame in un file CSV
                filename = df_save_to_csv(piece, char, all_infos_dir)

                # Aggiungiamo le informazioni sulle voci recuperate
                all_infos.extend(letter_infos)

            # Salvataggio del totale di voci recuperate
            total_records = len(all_infos)
            format_total_records = f'{total_records:,.0f}'.replace(',', '.')
            print(f'\nNumero totale di voci recuperate: {format_total_records}')
            time.sleep(0.6)

            # Salvataggio in JSON
            json_file = os.path.join(metallari_folder, '0_all_metallari_info.json')
            with open(json_file, 'w', encoding='utf-8') as f:
                json_infos = pretty_json(all_infos)
                f.write(json_infos)
            print(f'\nInfo salvate in {json_file}!')
            time.sleep(0.6)

            print('\nFinito! I metallari del mondo sono stati recuperati!\n\n')
        except Exception as e:
            # Gestione eccezioni in caso di fallimento
            print(f'\nArgh niente dati...\t->\t{e}')

    # Opzione scelta: Indicare solo la lettera iniziale
    elif which == 2:
        alphabet_dir = os.path.join(metallari_folder, 'alphabet')
        if not os.path.exists(alphabet_dir):
                os.makedirs(alphabet_dir)
                print('\nCartella "metallari/csv_output/alphabet" creata!\n')    
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
            entries = asyncio.run(fetch_some_entries(lettera))

            # Crea il DataFrame
            piece = pd.DataFrame(entries)

            # Salva le info sui metallari
            total_records = len(piece)
            format_total_records = f'{total_records:,.0f}'.replace(',', '.')
            print(f'\nNumero totale di voci recuperate: {format_total_records}')
            time.sleep(0.6)

            # Salva il DataFrame in un file CSV
            filename = df_save_to_csv(piece, lettera, alphabet_dir)
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

    # Stampa il numero totale di richieste effettuate
    print(f'\nNumero totale di richieste HTTP eseguite: {len(entries)}\n')

if __name__ == '__main__':
    main()
