# BandsinTown (BiT) API

Working directory: [./BandsinTown](./)

---
---

## Purpose
This project collects and analyzes data on musical events.  
The scripts in the `./exe` folder are designed to perform various operations such as:
- __Authentication__ to access Spotify personal data (unique scope is `user-follow-read`);
- __Merge__ BiT artists' URLs and names (from BiT _sitemap_) with Spotify _followlist_ obtained at previous step;
- __Scrape__ all BiT URLs corresponding to artists in the Spotify _followlist_. Operation consists in saving all events found in JSON content at each URL, if any;
- __Filter__ all global events found in the previous step despite country, city, date, etc. and save them in a CSV file. Then one can select a subset of events in Europe, getting actual distance from _home_ (=> `Sesto San Giovanni`, Italy) and save them in another CSV file.

---
---

## Scripts

### Auth_Followlist.py
This script handles authentication and management of user's followlist. It uses provided tokens to build the rest of the API.  
Refresh token from [tokens.json](data/tokens.json) will be used if available, otherwise it will be created on behalf of user.  

Example of [tokens.json](data/token.json):
```json
{
    "access_token": "string",
    "token_type": "Bearer",
    "expires_in": 3600, /*seconds*/
    "refresh_token": "string",
    "scope": "user-follow-read",
    "expiration": "3600s from last refresh"
}
```

After authentication, the script will fetch user's followlist and save it in two CSV files:
- `%Y-%m-%d_%H-%M_LONG_follow_dict.csv`: this is the entire follow list as it is returned by Spotify API;
- `%Y-%m-%d_%H-%M_SHORT_follow_dict.csv`: unlike the previous one, this file contains only the most relevant information about each artist.

These files won't be overwritten since every time the script is run, a new file with timestamp will be created:

```python
from os import listdir # to list files in a directory

os.getcwd()
# >>> './BandsinTown'

data_dir = os.path.join(os.getcwd(), 'data')
os.listdir(os.path.join(data_dir, 'short'))
# >>> ['2024-10-18_00-10_SHORT_follow_dict.csv', '2024-10-18_00-15_SHORT_follow_dict.csv', ...]

os.listdir(os.path.join(data_dir, 'long'))
# >>> ['2024-10-18_00-10_LONG_follow_dict.csv', '2024-10-18_00-15_LONG_follow_dict.csv', ...]
```

Example of [./data/short/2024-10-18_00-24_SHORT_follow_dict.csv](data/short/2024-10-18_00-24_SHORT_follow_dict.csv):
| ID                  | Name    | Genres                                                                                             | Followers | Popularity | Specific Genre                                         |
|---------------------|---------|---------------------------------------------------------------------------------------------------|-----------|------------|-------------------------------------------------------|
| 00Uv0804nrBM2RxUBTkyHj | Wobbler | ['c64', 'italian progressive rock', 'neo-progressive', 'norwegian prog', 'progressive rock']      | 18,638    | 18         | {'rock', 'prog', 'c64', 'italian', 'neo-progressive', 'progressive', 'norwegian'} |

Example of [./data/long/2024-10-18_00-24_LONG_follow_dict.csv](data/long/2024-10-18_00-24_LONG_follow_dict.csv):
| Key      | Value                                                                                                                                                                                                                                                                                                                                                                                                                 |
|-------------------|-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| external_urls     | {'spotify': 'https://open.spotify.com/artist/00Uv0804nrBM2RxUBTkyHj'}                                                                                                                                                                                                                                                                                                                                                    |
| followers         | 18,638                                                                                                                                                                                                                                                                                                                                                                                                                  |
| genres            | ['c64', 'italian progressive rock', 'neo-progressive', 'norwegian prog', 'progressive rock']                                                                                                                                                                                                                                                                                                                             |
| href              | https://api.spotify.com/v1/artists/00Uv0804nrBM2RxUBTkyHj                                                                                                                                                                                                                                                                                                                                                                |
| id                | 00Uv0804nrBM2RxUBTkyHj                                                                                                                                                                                                                                                                                                                                                                                                  |
| images            | ![640px](https://i.scdn.co/image/ab6761610000e5eb6ce3b74c2e4c71bf882ed2cf)<br>![320px](https://i.scdn.co/image/ab676161000051746ce3b74c2e4c71bf882ed2cf)<br>![160px](https://i.scdn.co/image/ab6761610000f1786ce3b74c2e4c71bf882ed2cf)                                                                                                                                                                                   |
| name              | wobbler                                                                                                                                                                                                                                                                                                                                                                                                                 |
| popularity        | 18                                                                                                                                                                                                                                                                                                                                                                                                                      |
| type              | artist                                                                                                                                                                                                                                                                                                                                                                                                                  |
| uri               | `spotify:artist:00Uv0804nrBM2RxUBTkyHj`                                                                                                                                                                                                                                                                                                                                                                                 |
| most_genre        | [(5, 'progressive rock'), (4, 'italian progressive rock'), (1, 'norwegian prog'), (1, 'neo-progressive'), (1, 'c64')]                                                                                                                                                                                                                                                                                                     |
| specific_genre    | {'rock', 'prog', 'c64', 'italian', 'neo-progressive', 'progressive', 'norwegian'}                                                                                                                                                                                                                                                                                                                                         |

---

### BiT_Spotify_Merge.py
This script merges the Spotify followlist with the corresponding BiT artists' URLs.  
Actually it gets all URLs from BiT and store them in a CSV file with the corresponding artist name by splitting the URL text.

Example of [./data/BiT_Archive/BiT_urls_names.csv](data/BiT_Archive/BiT_urls_names.csv):
| BiT_url                                                                                          | BiT_name                    |
|----------------------------------------------------------------------------------------------------------|-------------------------------------|
| [https://www.bandsintown.com/a/13661365-university-of-extreme-speed-metal](https://www.bandsintown.com/a/13661365-university-of-extreme-speed-metal) | university-of-extreme-speed-metal   |
| [https://www.bandsintown.com/a/1547463-dead-september](https://www.bandsintown.com/a/1547463-dead-september)                                    | dead-september                      |
| [https://www.bandsintown.com/a/1043347-celebrate-the-tragedy](https://www.bandsintown.com/a/1043347-celebrate-the-tragedy)                      | celebrate-the-tragedy               |

---

### BiT_Archive_Scraping.py
This script scrapes all URLs in `url_series`, which is the first column of [./data/BiT_Archive/BiT_urls_names.csv](data/BiT_Archive/BiT_urls_names.csv).  
Within BeautifulSoup is used the method `.find_all('script', type='application/ld+json')` to collect all events as dictionaries (if any) by parsing the JSON response of each URL.  
Events are finally stored in two CSV files:
- [./data/world_events_followlist_extended.csv](data/world_events_followlist_extended.csv): raw content of every item parsed as JSON response (dictionary);
- [./data/world_events_followlist_short.csv](data/world_events_followlist_short.csv): most relevant information about each planned event.

Example of [world_events_followlist_short.csv](data/world_events_followlist_short.csv):
| Name                                 | Start Date           | URL                                                                                                                                               | Artist          | Country      | Locality  | Street Address       | Postal Code | Coordinates                  |
|--------------------------------------|----------------------|---------------------------------------------------------------------------------------------------------------------------------------------------|----------------|--------------|-----------|-----------------------|-------------|------------------------------|
| Alice in Chains @ Historic Crew Stadium | 2025-05-11T00:00:00  | [https://www.bandsintown.com/e/105971661-alice-in-chains-at-historic-crew-stadium?came_from=209](https://www.bandsintown.com/e/105971661-alice-in-chains-at-historic-crew-stadium?came_from=209)                                              | Alice in Chains | United States | Columbus  | 1 Black and Gold Blvd | 43211       | (40.0095288, -82.99116219999999) |

Example of [world_events_followlist_extended.csv](data/world_events_followlist_extended.csv):
| Key                    | Value                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                 |
|-----------------------------|-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| @context                    | http://schema.org                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                       |
| @type                       | MusicEvent                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                              |
| name                        | Alice in Chains @ Historic Crew Stadium                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                |
| startDate                   | 2025-05-11T00:00:00                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                     |
| endDate                     | 2025-05-11                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                              |
| url                         | [https://www.bandsintown.com/e/105971661-alice-in-chains-at-historic-crew-stadium?came_from=209](https://www.bandsintown.com/e/105971661-alice-in-chains-at-historic-crew-stadium?came_from=209)                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                 |
| location                    | {'@type': 'Place', 'name': 'Historic Crew Stadium', 'address': {'@type': 'PostalAddress', 'addressCountry': 'United States', 'addressRegion': 'OH', 'addressLocality': 'Columbus', 'streetAddress': '1 Black and Gold Blvd', 'postalCode': '43211'}, 'geo': {'@type': 'GeoCoordinates', 'latitude': 40.0095288, 'longitude': -82.99116219999999}}                                                                                                                                                                                                                                                |
| performer                   | {'@type': 'PerformingGroup', 'name': 'Alice in Chains'}                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                 |
| description                 | Sonic Temple Art & Music Festival 2025                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                 |
| image                       | ![Image](https://photos.bandsintown.com/thumb/12226561.jpeg)                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                             |
| eventAttendanceMode         | http://schema.org/OfflineEventAttendanceMode                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                           |
| eventStatus                 | http://schema.org/EventScheduled                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                       |
| offers                      | {'@type': 'Offer', 'url': 'https://www.bandsintown.com/e/105971661-alice-in-chains-at-historic-crew-stadium?came_from=209', 'availability': 'https://schema.org/InStock', 'validFrom': '2000-01-01T00:00:00Z'}                                                                                                                                                                                                                                                                                                                                                                                         |
| organizer                   | {'@type': 'Organization', 'name': 'Alice in Chains', 'url': 'https://www.bandsintown.com/a/908-alice-in-chains?came_from=209'}                                                                                                                                                                                                                                                                                                                                                                                                                                                                         |

---

### Europe_Events.py
This script is specific to musical events in Europe. It collects and analyzes data on events happening in European countries.  
Libraries such as `geopy` allows to filter all worldwide events of all followed artists and select only those happening in Europe, storing data in two CSV files:
- [./data/FinalOutput/Europe_events.csv](data/FinalOutput/Europe_events.csv): as a reference, the script calculates the distance from the user's location (in this case, `Sesto San Giovanni`, Italy) to the event location.
- [./data/FinalOutput/nearHome_events.csv](data/FinalOutput/nearHome_events.csv): this file contains only the events happening within 10km from the reference location.

Example of [Europe_events.csv](data/FinalOutput/Europe_events.csv):
| Artist          | Month | Year | Date               | Days to Event | Address Country | Address Locality | Geocoordinates | Distance from Sesto | Popularity | Specific Genre                                    |
|------------------|-------|------|--------------------|---------------|-----------------|------------------|----------------|---------------------|------------|---------------------------------------------------|
| Gojira           | 7     | 2025 | 29/07/2025 15:00   | 284           | France          | Carcassonne      | (43.21, 2.35) | 605.7               | 67         | {'nu', 'metal', 'groove', 'alternative', 'progressive', 'french', 'death'} |
| Jon Hopkins      | 11    | 2024 | 11/11/2024 19:30   | 24            | United Kingdom   | London           | (51.55, -0.08) | 958.2               | 66         | {'music', 'dance', 'electronica', 'intelligent'} |
| Slowdive         | 4     | 2025 | 10/04/2025 19:30   | 174           | United Kingdom   | London           | (51.47, -0.11) | 954.0               | 65         | {'reading', 'alternative', 'shoegaze', 'rock', 'dream', 'pop', 'indie'}     |

Example of [nearHome_events.csv](data/FinalOutput/nearHome_events.csv):
| Name                                       | Start Date           | Artist              | Address Country | Address Locality | Street Address         | Latitude | Longitude | Distance from Sesto | Geocoordinates | Days to Event | Date                | Genres                                                                                                         | Popularity |
|--------------------------------------------|-----------------------|---------------------|-----------------|------------------|------------------------|----------|-----------|---------------------|----------------|---------------|---------------------|----------------------------------------------------------------------------------------------------------------|------------|
| Kamasi Washington @ Alcatraz              | 2025-04-22 20:00:00   | Kamasi Washington    | Italy           | Milan            | Via Valtellina 25      | 45.49    | 9.18      | 5.9                 | (45.49, 9.18)  | 186           | 22/04/2025 20:00    | ['afrofuturism', 'contemporary jazz', 'indie soul', 'jazz', 'jazz saxophone']                             | 57         |
| Chelsea Wolfe @ Circolo Magnolia           | 2024-11-13 20:00:00   | Chelsea Wolfe        | Italy           | Segrate          | Via Circonvallazione Idroscalo 41 | 45.46    | 9.29      | 9.1                 | (45.46, 9.29)  | 26            | 13/11/2024 20:00    | ['dark pop', 'doomgaze', 'gaian doom', 'sacramento indie']                                              | 51         |
| Alcest @ Alcatraz                         | 2024-11-16 18:30:00   | Alcest              | Italy           | Milan            | Via Valtellina 25      | 45.49    | 9.18      | 5.9                 | (45.49, 9.18)  | 29            | 16/11/2024 18:30    | ['atmospheric black metal', 'blackgaze', 'emotional black metal', 'french black metal', 'french metal', 'french shoegaze', 'post-black metal', 'post-metal', 'shoegaze'] | 48         |

---
---

## Installing Python and Adding it to `%PATH%`

### Steps to Install Python and Add it to `%PATH%`

1. __Download Python__:
   Go to the official Python website and download the [installer](https://www.python.org/downloads/) for the latest release Windows.

2. __Run the Installer__:
   Run the downloaded installer. During installation, make sure to select the option _Add Python to PATH_.

3. __Verify the Installation__:
   After installation, open the Command Prompt (cmd) and verify that Python has been added to `%PATH%` by running:
   ```sh
   python --version
   ```

   You should see the installed Python version. If you see an error, you may need to manually add Python to `%PATH%`.

### Manually Adding Python to `%PATH%`

1. __Find the Python Installation Path__:
   Locate the directory where Python is installed. It is usually something like `C:\Python39` or `C:\Users\YourUsername\AppData\Local\Programs\Python\Python39`.

2. __Add Python to `%PATH%`__:
   - Open the Control Panel.
   - Go to _System and Security_ > _System_.
   - Click on _Advanced system settings_.
   - In the window that opens, click on _Environment Variables_.
   - In the _System variables_ section, find and select the `Path` variable, then click _Edit_.
   - Add the path to the Python directory (e.g., `C:\Python39`) and the Python Scripts directory (e.g., `C:\Python39\Scripts`).

3. __Verify the Addition to `%PATH%`__:
   Close and reopen the Command Prompt, then run:
   ```sh
   python --version
   ```

   You should see the installed Python version.

### Script to Verify and Install Python

You can also create a batch script to automate part of this process. Here is an example of a batch script that checks if Python is installed and, if not, guides the user to download and install it:

```batch
@echo off
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Python is not installed. Please download and install Python from the official website.
    start https://www.python.org/downloads/
    pause
) else (
    echo Python is already installed.
    python --version
)
```

Save this script in a file with a `.bat` extension (e.g., `check_python.bat`) and run it to verify the Python installation.

---
---

## Libraries/Modules

```python
# File and directory management
from os import path, makedirs, getcwd, listdir
from glob import glob

# Data manipulation and analysis
from pandas import DataFrame, Series, Timestamp, read_csv, to_datetime, NaT
from numpy import nan

# .env file summoning
from dotenv import load_dotenv

# HTTP requests and scraping
from requests import get, post, exceptions, RequestException, Response
from bs4 import BeautifulSoup

# Data parsing (JSON, XML, etc.)
from json import load, loads, dump, dumps
from xml.dom import minidom
from xml.etree import ElementTree as ET
from ast import literal_eval

# Datetime management
from datetime import datetime, timedelta
from time import sleep

# Random and safe values
from random import choice, uniform
from secrets import token_hex

# Subprocess running
from subprocess import run, CalledProcessError

# Compress and decompress archives
from gzip import GzipFile
from io import BytesIO

# Querystring parsing
from urllib.parse import urlencode

# Logging
from logging import info, error

# RegEx pattern
from re import match

# Distance measurement
from geopy.distance import geodesic
```

---

### Docstrings from [`modules.py`](exe/modules.py)

#### do_subprocess
```python
def do_subprocess(script_name: str) -> None:
    """
    Executes the specified script as a subprocess.

    Args:
        script_name (str): The name of the script to execute.

    Raises:
        CalledProcessError: If the subprocess execution fails.
    """
```

#### file_existence
```python
def file_existence() -> None:
    """
    Checks the existence of necessary directories and environment variables.
    Creates directories if they do not exist and loads environment variables.

    Raises:
        ValueError: If SPOTIFY_CLIENT_ID or SPOTIFY_CLIENT_SECRET are not set in the .env file.
        FileNotFoundError: If the .env file is not found.
    """
```

#### rw_tokens
```python
def rw_tokens(filepath: str) -> dict:
    """
    Reads and writes Spotify tokens from/to a JSON file.

    Args:
        filepath (str): Path to the JSON file containing the tokens.

    Returns:
        dict: Dictionary containing the tokens.
    """
```

#### get_follow_dict
```python
def get_follow_dict(init_dict: dict | None = None, after_value: str | None = None, access_token: str | None = None) -> dict:
    """
    Retrieves the follow list of artists from Spotify.

    Args:
        init_dict (dict | None): Initial dictionary to store the follow list. Defaults to None.
        after_value (str | None): Cursor value to fetch the next set of results. Defaults to None.
        access_token (str | None): Spotify access token. Must be provided.

    Returns:
        dict: Dictionary containing the follow list of artists.

    Raises:
        Exception: If the access_token is None.
    """
```

#### check_duplicates
```python
def check_duplicates(dictionary: dict) -> DataFrame:
    """
    Checks for duplicate artists in the dictionary and returns a DataFrame of duplicates.

    Args:
        dictionary (dict): The dictionary containing artist data.

    Returns:
        DataFrame: DataFrame containing duplicate artist information.
    """
```

#### df_writer
```python
def df_writer(dictionary: dict, long: bool) -> DataFrame:
    """
    Writes a dictionary to a DataFrame and saves it as a CSV file.

    Args:
        dictionary (dict): The dictionary to write to the DataFrame.
        long (bool): Whether to use the long form of the DataFrame.

    Returns:
        DataFrame: The created DataFrame.

    Raises:
        ValueError: If the input dictionary is empty.
    """
```

#### slept_req
```python
def slept_req(url: str, wait_size: str = 'S') -> Response | None:
    """
    Sends a GET request to the specified URL with a random delay.

    Args:
        url (str): The URL to send the request to.
        wait_size (str): The wait mode. Can be 'S' (short), 'M' (medium), or 'L' (long).

    Returns:
        requests.Response | None: The response object if the request is successful, None otherwise.

    Raises:
        RequestException: If the request fails.
    """
```

#### session_cookies
```python
def session_cookies(url: str) -> dict:
    """
    Retrieves session cookies from the specified URL.

    Args:
        url (str): The URL to retrieve cookies from.

    Returns:
        dict: A dictionary of cookies.
    """
```

#### xml_map_save
```python
def xml_map_save(url: str) -> None:
    """
    Downloads and saves an XML sitemap from a URL.

    Args:
        url (str): The URL of the XML sitemap.

    Raises:
        ValueError: If the URL does not point to a valid XML file.
    """
```

#### xml_strings
```python
def xml_strings(fname: str) -> list[str] | None:
    """
    Extracts URLs from an XML sitemap file.

    Args:
        fname (str): The file path of the XML sitemap.

    Returns:
        list[str] | None: A list of URLs found in the sitemap, or None if the file is not valid.
    """
```

#### artist_bit_urls
```python
def artist_bit_urls(csv_path: str) -> DataFrame:
    """
    Loads or creates a DataFrame of artist URLs from a CSV file.

    Args:
        csv_path (str): The path to the CSV file.

    Returns:
        DataFrame: The loaded or created DataFrame.
    """
```

#### short_df_loader
```python
def short_df_loader(csv_path: str) -> DataFrame:
    """
    Loads the latest short DataFrame from a directory.

    Args:
        csv_path (str): The directory path containing the CSV files.

    Returns:
        DataFrame: The loaded DataFrame.
    """
```

#### human_readable_size
```python
def human_readable_size(file: str) -> str:
    """
    Converts a file size to a human-readable format.

    Args:
        file (str): The file path.

    Returns:
        str: The human-readable file size.
    """
```

#### json_response_eval
```python
def json_response_eval(response_text: str) -> list[dict] | None:
    """
    Evaluates the JSON response from a request and extracts event dictionaries.

    Args:
        response_text (str): The response text from the request.

    Returns:
        list[dict] | None: A list of event dictionaries, or None if no events are found.

    Raises:
        ValueError: If no script tag is found in the HTML.
    """
```

#### fetch_all_urls
```python
def fetch_all_urls(url_series: Series) -> list[dict]:
    """
    Fetches data from all URLs in the given series.

    Args:
        url_series (pd.Series): A series of URLs to fetch data from.

    Returns:
        list[dict]: A list of dictionaries containing the fetched data.

    Raises:
        ValueError: If the input series is empty.
    """
```

#### save_dfs
```python
def save_dfs(datalist: list[dict]) -> None:
    """
    Saves data to CSV files.

    Args:
        datalist (list[dict]): The list of dictionaries to save.
    """
```

#### complexity
```python
def complexity(dataframe: DataFrame) -> DataFrame:
    """
    Adds complexity to the DataFrame by filling empty values, processing coordinates,
    and adding new columns for geocoordinates, days to event, formatted date, and artist name in lowercase.

    Args:
        dataframe (DataFrame): The input DataFrame.

    Returns:
        DataFrame: The modified DataFrame with additional columns.
    """
```

#### mapper
```python
def mapper(df_from: DataFrame, keyword: str, column_returned: str) -> dict:
    """
    Creates a dictionary mapping from a DataFrame based on a keyword and a column to return.

    Args:
        df_from (DataFrame): The input DataFrame.
        keyword (str): The column to use as keys for the dictionary.
        column_returned (str): The column to use as values for the dictionary.

    Returns:
        dict: The created dictionary.
    """
```

#### is_europe
```python
def is_europe(latitude: float, longitude: float) -> bool:
    """
    Checks if the given latitude and longitude are within the bounds of Europe.

    Args:
        latitude (float): The latitude to check.
        longitude (float): The longitude to check.

    Returns:
        bool: True if the coordinates are within Europe, False otherwise.
    """
```

#### year_month
```python
def year_month(dataframe: DataFrame) -> DataFrame:
    """
    Adds 'year' and 'month' columns to the DataFrame based on the 'startDate' column.

    Args:
        dataframe (DataFrame): The input DataFrame.

    Returns:
        DataFrame: The modified DataFrame with 'year' and 'month' columns.
    """
```

#### load_short_df
```python
def load_short_df(directory: str) -> DataFrame | None:
    """
    Loads the latest short DataFrame from a directory.

    Args:
        directory (str): The directory path containing the CSV files.

    Returns:
        DataFrame | None: The loaded DataFrame, or None if an error occurs.
    """
```

#### query_game
```python
def query_game(df: DataFrame, field_name: str, input_value: str) -> DataFrame:
    """
    Filters the DataFrame based on the input value in the specified field.

    Args:
        df (DataFrame): The input DataFrame.
        field_name (str): The field to filter on.
        input_value (str): The value to filter by.

    Returns:
        DataFrame: The filtered DataFrame.
    """
```

#### show_all_genres
```python
def show_all_genres(df: DataFrame) -> list[str] | None:
    """
    Extracts all unique genres from the 'specific_genre' column in the DataFrame.

    Args:
        df (DataFrame): The input DataFrame.

    Returns:
        list[str] | None: A list of unique genres, or None if the 'specific_genre' column is not found.
    """
```

---
---

## Notes
- Ensure you have the correct credentials in the `.env` (in `.gitignore`) in parent directory `Season`, which is before `BandsinTown`. 
- Scripts can be run individually or as part of a larger workflow by launching `./Bandsintown/exe/MASTER.py`.

---

## Installation and Execution

### Prerequisites
- Python 3.x
- Pip (Python package manager)
- Spotify account with API credentials

---

### Installing Python and Pip



---

### Install

1. __Clone the Repository__
   - Open your terminal and clone the repository using the following command:
     ```sh
     git clone https://github.com/m-contini/public.git
     ```
   - Navigate to the `Bandsintown` directory within the cloned repository:
     ```sh
     cd public/Season/Bandsintown/
     ```

2. __Create a Virtual Environment (Optional but Recommended)__
   - It's good practice to create a virtual environment to manage dependencies. Use the command below to create one:
     ```sh
     python -m venv env
     ```
        Using `-m` allows you to execute library modules as scripts. This can be particularly useful because:
       - It provides a clean way to run modules without needing to modify the `PATH`.
       - It ensures that you're using the correct version of the module that's bundled with the Python interpreter you're invoking.

   - __Activate the Virtual Environment:__
     - On __Linux__/__macOS__, use:
       ```sh
       source env/bin/activate
       ```
     - On __Windows__, the command is slightly different:
       ```sh
       env\Scripts\activate
       ```
     - If you encounter an error like `No such file or directory`, ensure you are using the correct path and that the virtual environment was created successfully. You can verify this by checking the contents of the `Bandsintown` directory:
       ```sh
       ls  # or dir on Windows
       ```
       You should see a folder named `env`.

3. __Install Dependencies__
   - With the virtual environment activated, install the required dependencies using:
     ```sh
     pip install -r requirements.txt
     ```

4. __Configure API Credentials__
    Open the `.env` file in your favorite text editor and replace the placeholder values with your actual API credentials.

5. __Run the Application__
   - Once the above steps are completed, you should be able to run the application. Ensure your virtual environment is still activated and execute:
     ```sh
     python exe/MASTER.py
     ```

---

### Troubleshooting Tips

- If you get an error when trying to activate the virtual environment, ensure that:
  - You are in the correct directory where the `env` folder is located.
  - The virtual environment was created successfully. If not, try running the `python -m venv env` command again.
- If you see any permission issues on macOS or Linux, try running the activation command with `sudo`, or check your directory permissions.
