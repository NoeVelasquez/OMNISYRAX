# -*- coding: utf-8 -*-
import random
from abc import ABC, abstractmethod
from typing import List, Any
from faker import Faker

class BaseGenerator(ABC):
    """
    Clase base abstracta para generadores de datos.
    Proporciona utilidades comunes y define el contrato para subclases.
    """
    
    def __init__(self, seed: int = None, lang: str = "es"):
        self.lang = lang
        # Faker no soporta 'all'. Usamos 'es' como fallback para la librería,
        # pero mantenemos self.lang = 'all' para nuestra lógica interna de OMNISYRAX.
        faker_lang = "es" if lang == "all" else lang
        self.faker = Faker(faker_lang)
        if seed is not None:
            random.seed(seed)
            Faker.seed(seed)
            
    @abstractmethod
    def generate_single(self) -> Any:
        """Genera un único objeto de dominio."""
        pass
    
    def generate_batch(self, count: int) -> List[Any]:
        """Genera una lista de objetos de dominio."""
        return [self.generate_single() for _ in range(count)]
        
    def get_random_item(self, items: List[Any]) -> Any:
        """Utility to get a random item from a list."""
        return random.choice(items) if items else None
