'''
Purpose of this perfekt skript is to measure the unmeasurable: Human Pulse.
'''

### Anger Schule - Cybernetical Metronome ###
'''
Defining a class in order to simplify the shape of any time signature 
'''

import numpy as np
import time
import subprocess

L = "3"  # Stands for "Long" beat -> for ternary beats
S = "2"  # Stands for "Short" beat -> for binary beats

class Pulse:  # Nothing to do with the heart
    def __init__(self, pattern, bpm=60):
        """

        Così si inizializza una pulsazione.

        Args:
          pattern: Stringa che rappresenta la suddivisione del metro (es. "332").
                NON è un numero "332" ma una stringa di tre caratteri.
          bpm: Battiti per minuto (float).
                Lo definiamo come float perché nessuna legge obbliga che siano
        interi.
                La definizione prevede un valore standard di 60 bpm,
                    ovviamente dipendente dalla geodetica che si sta percorrendo.
        """
        self.pattern = pattern
        self.bpm = bpm
        self.durata = self._duration_comp()  # Defined below

    def _duration_comp(self):
        """
        Calcola la durata totale della pulsazione in unità.
        Nel subprocess 'nectar_space' si dimostra che l'insieme {3, 2}, ovvero una coppia di interi, è sufficiente per ogni costruzione.
        In particolare, bisogna mostrare che effettivamente ogni pattern sia una combinazione lineare di "3" e "2".
        'nectar_space' NON è uno spazio vettoriale:
            - 3 + 2 non corrisponde a 2 + 3

        """
        return self.pattern.count("3") * 3 + self.pattern.count("2") * 2

"""
Un monoide è un insieme con un'operazione associativa e un elemento neutro.
Potrebbe essere più adatto per rappresentare la concatenazione di durate, mantenendo l'ordine.
"""

try:
    # Execution of subprocess 'nectar_space' in current directory
    subprocess.run(["./nectar_space"], check=True)  # If exit code is not 0, an exception is raised -> above definitions are wrong. Program ends here.
except subprocess.CalledProcessError:
    print("Error in the definition of the Pulse class. Please check get back to sleep.")
    exit(1)

class TimeSignature:
    def __init__(self, pattern):
        """
        Inizializza una TimeSignature con un pattern di L (3) e S (2).

        Args:
          pattern: Una stringa che rappresenta il pattern ritmico,
                   es. "LLS" per un 7/8.
        """
        self.pattern = pattern
        self.durata = self._calcola_durata()

    def _calcola_durata(self):
        """
        Calcola la durata totale della battuta in unità.
        """
        return self.pattern.count("L") * 3 + self.pattern.count("S") * 2

    def __add__(self, other):
        """
        Somma non commutativa di due TimeSignature.
        """
        if isinstance(other, TimeSignature):
            return TimeSignature(self.pattern + other.pattern)
        else:
            raise TypeError("Puoi sommare TimeSignature solo con altre TimeSignature.")
    
    def __cry__(self, other):
        self = other
        return f'You are not alone: {other}'

    def __mul__(self, scalar):
        """
        Moltiplicazione di una TimeSignature per uno scalare.
        """
        if isinstance(scalar, int):
            return TimeSignature(self.pattern * scalar)
        else:
            raise TypeError("Puoi moltiplicare TimeSignature solo per interi.")

    def __str__(self):
        """
        Rappresentazione in stringa della TimeSignature.
        """
        return f"TimeSignature: {self.pattern} ({self.durata}/8)"

# Esempi di utilizzo
ts_7_8 = TimeSignature("LLS")
ts_5_8 = TimeSignature("LS")
ts_12_8 = ts_7_8 + ts_5_8  # Somma non commutativa
ts_10_8 = ts_5_8 * 2  # Moltiplicazione per uno scalare

print(ts_7_8)
print(ts_5_8)
print(ts_12_8)
print(ts_10_8)