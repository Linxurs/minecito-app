"""
Generador de nombres de usuario aleatorios
"""
import random
import re
from typing import List

_ADJECTIVES = sorted([
    "Bill", "Cal", "Dar", "Fun", "Gen", "Gol", "Happy", "Hol", "Krit",
    "Mig", "Nus", "Sad", "Ser", "Shy", "Sil", "Smad", "Swy", "Thom",
])

_NOUNS = sorted([
    "Bird", "Blast", "Cat", "Dog", "Dolly", "Don", "Elephy", "Fish",
    "Gra", "Lio", "Moo", "Nick", "Nill", "Phel", "Star", "Story",
    "Turly", "Vey", "White", "Win", "Znack",
])

# Patrón compilado para detectar nombres generados aleatoriamente
_RANDOM_USERNAME_PATTERN_COMPILED = re.compile(
    "|".join(
        f"{adjective}as{noun}[0-9]{{2}}"
        for adjective in _ADJECTIVES
        for noun in _NOUNS
    )
)


class UsernameGenerator:
    """Generador de nombres de usuario aleatorios"""
    
    @staticmethod
    def generate_random_username() -> str:
        """Genera un nombre de usuario aleatorio"""
        random_number = random.randint(10, 99)
        adj = random.choice(_ADJECTIVES)
        noun = random.choice(_NOUNS)
        generated_name = f"{adj}as{noun}{random_number}"
        max_length = 16
        truncated_name = generated_name[:max_length]
        return truncated_name
    
    @staticmethod
    def is_randomly_generated(username: str) -> bool:
        """Verifica si un nombre de usuario fue generado aleatoriamente"""
        return _RANDOM_USERNAME_PATTERN_COMPILED.match(username) is not None
    
    @staticmethod
    def validate_username_length(username: str) -> tuple[bool, str]:
        """
        Valida la longitud del nombre de usuario
        Retorna (es_válido, mensaje_advertencia)
        """
        if len(username) <= 2:
            return False, "No podrás jugar en modo online con un nombre tan corto."
        elif len(username) > 15:
            return False, "No podrás jugar en modo online con un nombre mayor a 15 caracteres."
        return True, ""