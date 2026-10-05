# -*- coding: utf-8 -*-
import random
from datetime import datetime, timedelta
from src.core.base_generator import BaseGenerator
from src.domain.models import Order, Customer, Address, OrderItem
from src.utils import data_pool
from src.utils.address_fetcher import AddressFetcher

class OrderGenerator(BaseGenerator):
    """Generador especializado en la creación de órdenes con direcciones residenciales reales y únicas."""
    
    def __init__(self, lang: str = "en", country_mode: str = "US"):
        super().__init__(lang)
        self.available_skus = []
        self.country_mode = country_mode

    def generate_batch(self, count: int, multi_sku: bool = True, skus: list = None, days_back: int = 0, country_mode: str = "US") -> list[Order]:
        self.multi_sku = multi_sku
        self.available_skus = skus or []
        self.days_back = days_back
        self.country_mode = country_mode

        # Obtener direcciones residenciales reales y únicas para todo el lote
        shipping_addresses = AddressFetcher.get_unique_addresses(count, country_mode=self.country_mode)
        billing_addresses = AddressFetcher.get_unique_addresses(count, country_mode=self.country_mode)

        orders_list = []
        for i in range(count):
            ship_data = shipping_addresses[i] if i < len(shipping_addresses) else shipping_addresses[0]
            bill_data = billing_addresses[i] if i < len(billing_addresses) else billing_addresses[0]
            orders_list.append(self.generate_single(shipping_data=ship_data, billing_data=bill_data))
        
        return orders_list

    def _generate_item(self, sku: str = None) -> OrderItem:
        if sku:
            category = sku.split("-")[1] if "-" in sku else random.choice(data_pool.PRODUCT_CATEGORIES)
        elif self.available_skus:
            sku = random.choice(self.available_skus)
            category = sku.split("-")[1] if "-" in sku else random.choice(data_pool.PRODUCT_CATEGORIES)
        else:
            category = random.choice(data_pool.PRODUCT_CATEGORIES)
            product_id = random.randint(1000, 9999)
            sku = f"SKU-{category[:3].upper()}-{product_id}"
        
        # Obtener nombre según categoría
        lang_data = data_pool.MULTILANG_DATA.get(self.lang, data_pool.MULTILANG_DATA["en"])
        noun = random.choice(lang_data["categories"].get(category, lang_data["categories"]["Electronics"]))
        adj = random.choice(lang_data["adjectives"])
        
        return OrderItem(
            sku=sku,
            description=f"{adj} {noun}",
            quantity=random.randint(1, 5),
            sold_price=round(random.uniform(10.0, 500.0), 2)
        )

    def generate_single(self, shipping_data: dict = None, billing_data: dict = None) -> Order:
        num_items = random.randint(1, 5) if self.multi_sku else 1
        
        # Garantizar SKUs únicos
        items = []
        used_skus = set()
        
        # Si hay SKUs disponibles, intentar tomarlos de ahí sin repetir
        if self.available_skus:
            count_to_pick = min(num_items, len(self.available_skus))
            order_skus = random.sample(self.available_skus, count_to_pick)
            for sku in order_skus:
                items.append(self._generate_item(sku=sku))
        else:
            while len(items) < num_items:
                item = self._generate_item()
                if item.sku not in used_skus:
                    items.append(item)
                    used_skus.add(item.sku)
        
        total_price = sum(item.quantity * item.sold_price for item in items)
        
        # Generar direcciones residenciales reales
        if not shipping_data:
            shipping_data = AddressFetcher.get_unique_addresses(1, country_mode=self.country_mode)[0]
        if not billing_data:
            billing_data = AddressFetcher.get_unique_addresses(1, country_mode=self.country_mode)[0]
            
        shipping = Address(
            address1=shipping_data["address1"],
            city=shipping_data["city"],
            state=shipping_data["state"],
            postal_code=shipping_data["zip"],
            country=shipping_data["country"],
            currency=shipping_data["currency"]
        )
        billing = Address(
            address1=billing_data["address1"],
            city=billing_data["city"],
            state=billing_data["state"],
            postal_code=billing_data["zip"],
            country=billing_data["country"],
            currency=billing_data["currency"]
        )
        
        # Lógica de fecha (hoy o fechas pasadas)
        if hasattr(self, 'days_back') and self.days_back > 0:
            random_days = random.randint(0, self.days_back)
            order_date = datetime.now() - timedelta(days=random_days)
        else:
            order_date = datetime.now()
        
        # Formatear el número de orden como ORD-YYYYMMDD-HHMMSS
        order_prefix = order_date.strftime("%Y%m%d-%H%M%S")
        
        return Order(
            order_num=f"ORD-{order_prefix}-{random.randint(100, 999)}",
            order_date=order_date,
            customer=self._generate_customer(),
            shipping_address=shipping,
            billing_address=billing,
            items=items,
            total_price=round(total_price, 2),
            ship_method=random.choice(data_pool.SHIP_METHODS),
            ship_carrier=random.choice(data_pool.SHIP_CARRIERS)
        )
    
    def _generate_customer(self) -> Customer:
        first = random.choice(data_pool.FIRST_NAMES)
        last = random.choice(data_pool.LAST_NAMES)
        return Customer(
            firstname=first,
            lastname=last,
            email=f"{first.lower()}.{last.lower()}@example.com",
            phone=self.faker.phone_number()
        )
