# %% MODULES
from logging import error, info, basicConfig, INFO
from subprocess import run, CalledProcessError
from os import getcwd, path, chdir

# %% VARIABLES
basicConfig(filename='log_master.log', level=INFO, format='%(asctime)s - %(levelname)s - %(message)s')

scripts = ['Auth_Followlist.py', 'BiT_Spotify_Merge.py', 'BiT_Archive_Scraping.py', 'Europe_Events.py']

exe_dir = getcwd()
if not exe_dir.endswith('exe'):
    raise Exception(f'\nThis script must be executed in \'public/Season/Bandsintown/exe\' folder, not in {exe_dir}\n')

# %% RUN
if __name__ == '__main__':

    for script in scripts:
        script_path = path.join(exe_dir, script)
        if not path.exists(script_path):
            error(f'Script {script} not found in {exe_dir}')
            continue

        try:
            run(['python', script_path], check=True)
            info(f'\nSuccessfully executed {script}\n')
        except CalledProcessError as e:
            error(f'Errore durante l\'esecuzione di {script}: {e.returncode} - {e.stderr}')
            break

    querygame = input('\nWould you like to play with my anal queries? (N/n to exit): ').strip().lower()
    if querygame != 'n':
        try:
            chdir(path.dirname(exe_dir))
            queryze_me_path = path.join(getcwd(), 'QueryzeMe.py')
            run(['python', queryze_me_path], check=True)
            info(f'\n\n\t\tThank you for porcodioeing with me')
        except CalledProcessError as e:
            error(f'Errore durante l\'esecuzione di QueryzeMe.py: {e.returncode} - {e.stderr}')
