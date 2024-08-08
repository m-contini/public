# All_csv_into_one.py
# Append ogni CSV di public/metallari/csv_output/all_infos

import os
import pandas as pd
import glob

# Directory corrente e cartella dei dati
current_dir = os.getcwd()

# Definisci il percorso della cartella dei file CSV
path = os.path.join(current_dir, 'csv_output', 'all_infos')

# Verifica se la cartella esiste
if not os.path.exists(path):
    os.makedirs(path, exist_ok=True)
    print(f'\n>>Cartella {path} creata!')
else:
    print(f'\n>>La cartella {path} esiste!')

# Crea una lista di tutti i file CSV nel percorso specificato
all_files = glob.glob(path + "/?_data.csv")

print(f'\n>>Unione csv di tutti i file di una cartella:\n{path}')

# Crea una lista vuota per contenere i nomi dei file CSV
file_names = []
for file in all_files:
    file_names.append(os.path.basename(file))

# Stampa i nomi dei file CSV
print('\n>>Nomi dei file CSV:\n', file_names)

# Stampa il numero di file CSV
print('\n>>Numero di file CSV: ', len(file_names))

# Crea un DataFrame vuoto
df = pd.DataFrame()

# Leggi tutti i file CSV e concatena in un unico DataFrame
for file in all_files:
	df = pd.concat([df, pd.read_csv(file, sep=';', encoding='utf-8')], ignore_index=True)

# Salva il DataFrame in un file CSV
df.to_csv(os.path.join(path, '0_all_data.csv'), sep=';', encoding='utf-8',index=False)

print(f'\n>>Salvataggio completato col nome {os.path.join(path, "0_all_data.csv")}')

# Stampa il numero di righe e colonne del DataFrame
print('\n>>Numero di righe e colonne del DataFrame (r, c): ', df.shape, '\n')
