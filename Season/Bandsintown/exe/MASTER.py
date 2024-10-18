# %% MODULES
from logging import error, info, basicConfig, INFO
from subprocess import run, CalledProcessError
from os import getcwd, path, chdir
from termcolor import colored

# %% BANNER
mind_awake = "MIND AWAKE"
body_asleep = "BODY ASLEEP"
print('\n\t-------|| Benvenuto nel mio ano diocane ||-------\n')
print('\t-----------|| ', end='')
print(colored("MIND AWAKE", 'light_red', attrs=['bold'], on_color='on_blue', force_color=True), end='')
print(colored("BODY ASLEEP", 'yellow', attrs=['bold'], on_color='on_red', force_color=True), end='')
print(' ||-----------\n')

# %% VARIABLES
basicConfig(filename='master.log', level=INFO, format='%(asctime)s - %(levelname)s - %(message)s')

scripts = ['Auth_Followlist.py', 'BiT_Spotify_Merge.py', 'BiT_Archive_Scraping.py', 'Europe_Events.py']

#module_names = [script.split('.')[0] for script in scripts]

# %% FUNCTIONS

# %% MAIN
def main():

    if not getcwd().endswith('exe'):
        raise Exception(f'\nThis script must be executed in \'public/Season/Bandsintown/exe\' folder, not in {getcwd()}\n')

    print(f'\nCurrent working directory: {getcwd()}\nFound the following scripts to execute:')
    print(*scripts, sep=', ', end='\n\n')

    if input('Press Enter to continue or N/n to exit: ').strip().lower() == 'n':
        info(f'\n\n\t\tThank you...\n')
        exit()

    for script in scripts:
        script_path = path.join(getcwd(), script)
        if not path.exists(script_path):
            error(f'Script {script} not found in {getcwd()}')
            continue

        try:
            run(['python', script_path], check=True)
            info(f'\nSuccessfully executed {script}\n')
        except CalledProcessError as e:
            error(f'Errore durante l\'esecuzione di {script}: {e.returncode} - {e.stderr}')
            break

    if input('\nWould you like to (simple) query the table of european events? (N/n to exit): ').strip().lower() != 'n':
        try:
            chdir(path.dirname(getcwd()))
            queryze_me_path = path.join(getcwd(), 'QueryzeMe.py')
            run(['python', queryze_me_path], check=True)
            info(f'\n\n\t\tThank you for joining!\n')
        except CalledProcessError as e:
            error(f'Errore calling process \'QueryzeMe.py\':\nCalledProcessError.<returncode {e.returncode}\n\nCalledProcessError.stderr{e.stderr}')

# %% RUN
if __name__ == '__main__':
    main()
