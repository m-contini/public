# _Scraping_

Lo _scraping_ è una tecnica utilizzata per estrarre dati da siti web.  
In questo caso, lo script invia richieste GET all'[endpoint AJAX](https://www.metal-archives.com/browse/ajax-letter/l) sito [Encyclopedia Metallum](https://www.metal-archives.com/) e riceve risposte in formato JSON, che vengono poi elaborate e salvate.

Ciascuno dei seguenti script è stato programmato in __Python__

---
---

# metal_v3_asyncio

`metal_v3_asyncio` è uno script per estrazione e raccolta dati sulle band metal.  
Si utilizzano le librerie `aiohttp` e `asyncio` per richieste HTTP _asincrone_, consentendo un recupero efficiente dei dati per più band __in parallelo__.

## Caratteristiche

- **Recupero dati asincrono**: Utilizza `aiohttp` e `asyncio` per eseguire più richieste HTTP in parallelo.
- **Tracciamento del progresso**: Mostra il progresso del recupero dei dati in tempo reale.
- **Elaborazione dei dati**: Salva i dati recuperati in formato CSV e fornisce informazioni dettagliate sui DataFrame ottenuti con `pandas`.
- **Gestione degli errori**: Include una robusta gestione degli errori per le richieste HTTP.
- **Opzioni flessibili**: Permette agli utenti di recuperare dati per tutte le band o solo per quelle che iniziano con una lettera specifica.

## Installazione

### Configurazione dell'ambiente

**Esegui** digitando `cmd` o `powershell` in `Windows+R`

2. **Python 3.9.6 (amd64)**:
    ```
    curl -o python-installer.exe https://www.python.org/ftp/python/3.9.6/python-3.9.6-amd64.exe
    .\python-installer.exe /quiet InstallAllUsers=0 PrependPath=1
    ```

3.  **pip**:
    ```
    curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py
    python get-pip.py
    ```

4. **git (2.33.9 64bit)**:
    ```
    curl -o git-installer.exe https://github.com/git-for-windows/git/releases/download/v2.33.0.windows.1/Git-2.33.0-64-bit.exe
    .\git-installer.exe /silent
    ```

### Repository

1. **Clona il repository**:
    ```
    git clone https://github.com/m-contini/public
    cd public/metallari
    ```

2. **Dipendenze**:
    ```
    pip install string  os json pandas aiohttp asyncio time
    ```
Anche se non utilizzate in `metal_v3_asyncio`, installiamo anche:
    ```
    pip glob install requests bs4
    ```

## Utilizzo

1. **Esecuzione**:
    - Bash:
      ```bash
      python metal_v3_asyncio.py
      ```
    - Windows (CMD o PowerShell):
      ```
      python metal_v3_asyncio.py
      ```

2. **Opzioni**:
    - __1__. Salva tutte le band;
    - __2__. Salva le band che iniziano con una lettera specifica.

## Dettaglio

- ### `progress_printer(start, end, total_records, iniziale)`
 Stampa il progresso del recupero dei dati.

- ### `fetch_entries_for_batch(session, iniziale, start, step)`
  Recupera un gruppo di voci per una specifica lettera e indice iniziale da passare al processo batch seguente.

- ### `fetch_some_entries(iniziale)`
  Recupera le voci delle band metal per la lettera specificata usando asyncio per richieste parallele.

- ### `print_df_info(dataframe)`
  Stampa informazioni dettagliate sul DataFrame contenente i dati delle band metal.

- ### `df_save_to_csv(records, text_start, path)`
  Salva i dati in un file CSV con il nome basato su `text_start` concatenato a `data.csv`.

- ### `pretty_json(json_data)`
  Formatta un oggetto JSON in modo leggibile.

- ### `measure_execution_time(func)`
  Decorator per misurare il tempo di esecuzione di una funzione.

- ### `main()`
Funzione principale che orchestra l'interazione con l'utente e il recupero dei dati.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

---
---

# metal_v3

## Caratteristiche

- **Recupero dati sincrono**: Utilizza `requests` per eseguire richieste HTTP.
- **Tracciamento del progresso**: Mostra il progresso del recupero dei dati in tempo reale.
- **Elaborazione dei dati**: Salva i dati recuperati in formato CSV e fornisce informazioni dettagliate sui DataFrame.
- **Gestione degli errori**: Include una robusta gestione degli errori per le richieste HTTP.
- **Opzioni flessibili**: Permette agli utenti di recuperare dati per tutte le band o solo per quelle che iniziano con una lettera specifica.

---
---

# All_csv_into_one

`All_csv_into_one` è uno script per unire tutti i file CSV presenti in una cartella in un unico file CSV.  
Utilizza la libreria `pandas` per leggere e concatenare i file.

## Caratteristiche

- **Unione dei file CSV**: Legge tutti i file CSV presenti in una cartella e li concatena in un unico DataFrame.
- **Salvataggio del DataFrame**: Salva il DataFrame risultante in un file CSV.

---
---

# metal_ajax_parser (WIP)

`metal_ajax_parser` è uno script in fase (WIP) per eseguire il parsing dei dati JSON restituiti da un endpoint specifico di Encyclopedia Metallum.  
Lo script gestisce una grande quantità di dati e salva le informazioni estratte in un file CSV.
