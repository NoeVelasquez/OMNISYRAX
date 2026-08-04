# -*- coding: utf-8 -*-
import random
from src.core.base_generator import BaseGenerator
from src.domain.models import Package

class PackageGenerator(BaseGenerator):
    """Generador de paquetes (cajas) con dimensiones y pesos."""
    
    TYPES = ["Box", "Pallet", "Envelope", "Crate"]
    
    def generate_single(self) -> Package:
        pkg_type = random.choice(self.TYPES)
        l = round(random.uniform(10, 100), 2)
        w = round(random.uniform(10, 80), 2)
        h = round(random.uniform(5, 60), 2)
        
        return Package(
            name=f"PKG-{pkg_type.upper()}-{random.randint(100, 999)}",
            description=f"Standard {pkg_type} for shipping",
            type_pack=pkg_type,
            price=round(random.uniform(1.0, 20.0), 2),
            cost=round(random.uniform(0.5, 15.0), 2),
            length=l,
            width=w,
            height=h,
            inner_length=round(l * 0.95, 2),
            inner_width=round(w * 0.95, 2),
            inner_height=round(h * 0.95, 2),
            box_weight=round(random.uniform(0.1, 5.0), 2),
            max_weight=round(random.uniform(10.0, 50.0), 2),
            volume_capacity=round((l * w * h) / 1000, 2),
            stackeable=random.choice([True, False])
        )
