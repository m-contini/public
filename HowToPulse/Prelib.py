'''
Purpose of this perfekt skript is to measure the unmeasurable: Human Pulse.
'''

### Anger Schule - Cybernetical Metronome ###
'''
Defining a class in order to simplify the shape of any time signature 
'''

import numpy as np # Of course... based
import time as abs_time # As imposed by the stress-energy tensor
from subprocess import run, CalledProcessError as KILL # It will be clear later to fix and impress the counting method

class Pulse: # Nothing to do with the heart
    def __init__(self, pattern, bpm=60):
        """
        Così si inizializza una pulsazione.

        Args:
          pattern: Stringa che rappresenta la suddivisione del metro (es. "332").
                NON è un numero "332" ma una stringa di tre caratteri.
          bpm: Battiti per minuto (float).
                Lo definiamo come float perché nessuna legge obbliga che siano interi.
                La definizione prevede un valore standard di 60 bpm,
                    ovviamente dipendente dalla geodetica che si sta percorrendo.
        """
        self.pattern = pattern
        self.bpm = bpm
        self.durata = self._duration_comp() # Defined below

    def _duration_comp(self):
        """
        Calcola la durata totale della pulsazione in unità.

        Nel subprocess 'nectar_space' si dimostra che l'insieme {3, 2}, ovvero una coppia di interi, è sufficiente per ogni costruzione.
        In particolare, bisogna mostrare che effettivamente ogni pattern sia una combinazione lineare di "3" e "2".
        'nectar_space' NON è uno spazio vettoriale:
            - 3 + 2 non corrisponde a 2 + 3
            
        """
        return self.pattern.count('3') * 3 + self.pattern.count('2') * 2
    
'''
Un monoide è un insieme con un'operazione associativa e un elemento neutro.
Potrebbe essere più adatto per rappresentare la concatenazione di durate, mantenendo l'ordine.
'''

try:
    # Execution of subprocess 'nectar_space' in current directory
    run(['./nectar_space'], check=True) # If exit code is not 0, an exception is raised -> above definitions are wrong. Program ends here.
except KILL:
    print('Error in the definition of the Pulse class. Please check get back to sleep.')
    exit(1)