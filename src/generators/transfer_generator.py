# -*- coding: utf-8 -*-
import random
from datetime import datetime, timedelta
from src.core.base_generator import BaseGenerator
from src.domain.models import Transfer, Address, OrderItem
from src.utils import data_pool

class TransferGenerator(BaseGenerator):
    """Generador de transferencias entre almacenes o locaciones."""
    
    def generate_single(self) -> Transfer:
        # Generar datos de origen y destino
        country_from = random.choice(list(data_pool.CITIES.keys()))
        country_to = random.choice(list(data_pool.CITIES.keys()))
        
        num_items = random.randint(1, 8)
        items = []
        total_price = 0.0
        used_skus = set()
        
        while len(items) < num_items:
            sku = f"SKU-TR-{random.randint(1000, 9999)}"
            if sku not in used_skus:
                qty = random.randint(10, 100)
                price = round(random.uniform(5.0, 50.0), 2)
                items.append(OrderItem(
                    sku=sku,
                    description="Transfer Item",
                    quantity=qty,
                    sold_price=price
                ))
                total_price += (qty * price)
                used_skus.add(sku)
        
        timestamp = datetime.now().strftime("%m%d%H%M%S")
        transfer_num = f"TR-{timestamp}-{random.randint(1000, 9999)}"
        
        return Transfer(
            transfer_number=transfer_num,
            ship_method=random.choice(data_pool.SHIP_METHODS),
            ship_carrier=random.choice(data_pool.SHIP_CARRIERS),
            instruction=self.faker.sentence(),
            comments=self.faker.sentence(),
            date=datetime.now().date(),
            total_price=round(total_price, 2),
            
            from_email=self.faker.email(),
            from_phone=self.faker.phone_number(),
            from_first_name=self.faker.first_name(),
            from_last_name=self.faker.last_name(),
            from_address1=self.faker.street_address(),
            from_city=random.choice(data_pool.CITIES[country_from]),
            from_state=self.faker.state_abbr() if country_from == "USA" else country_from,
            from_country=country_from,
            from_zip=self.faker.postcode(),
            
            to_email=self.faker.email(),
            to_phone=self.faker.phone_number(),
            to_first_name=self.faker.first_name(),
            to_last_name=self.faker.last_name(),
            to_address1=self.faker.street_address(),
            to_city=random.choice(data_pool.CITIES[country_to]),
            to_state=self.faker.state_abbr() if country_to == "USA" else country_to,
            to_country=country_to,
            to_zip=self.faker.postcode(),
            
            items=items
        )
