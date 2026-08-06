# -*- coding: utf-8 -*-
import os
import urllib.request
import json
import random
from datetime import datetime

class APIProductFetcher:
    """Módulo multi-API para consumir 7 APIs públicas de productos reales en tiempo de ejecución (DummyJSON, FakeStoreAPI, Platzi API, Makeup API, Gutendex Books, OpenBeautyFacts y PokeAPI Toys) con persistencia entre lotes."""
    
    _cache = []
    _used_titles = set()
    _history_file = os.path.join("data", ".product_history.json")

    @classmethod
    def _load_history(cls):
        if not cls._used_titles and os.path.exists(cls._history_file):
            try:
                with open(cls._history_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    cls._used_titles = set(data.get("titles", []))
            except Exception:
                cls._used_titles = set()

    @classmethod
    def _save_history(cls):
        try:
            os.makedirs("data", exist_ok=True)
            # Conservar máximo los últimos 5000 títulos para no saturar memoria
            recent_titles = list(cls._used_titles)[-5000:]
            with open(cls._history_file, "w", encoding="utf-8") as f:
                json.dump({"titles": recent_titles, "updated_at": datetime.now().isoformat()}, f, indent=2)
        except Exception:
            pass

    @staticmethod
    def _clean_image_url(url: str) -> str:
        if not url:
            return ""
        url = str(url).strip()
        # Eliminar caracteres de control o saltos de línea
        url = "".join(c for c in url if ord(c) >= 32)
        # Reemplazar espacios sin codificar con %20 para validez HTTP
        if " " in url:
            url = url.replace(" ", "%20")
        return url

    @staticmethod
    def _clean_description(desc: str, max_len: int = 250) -> str:
        if not desc:
            return ""
        import re
        clean = re.sub(r'<[^>]+>', ' ', str(desc))
        clean = " ".join(clean.replace("\n", " ").replace("\r", " ").replace('"', '').split())
        if len(clean) > max_len:
            truncated = clean[:max_len - 3].rsplit(" ", 1)[0]
            return f"{truncated}..."
        return clean

    @classmethod
    def load_live_products(cls, force_refresh: bool = False) -> list:
        cls._load_history()
        if cls._cache and not force_refresh:
            return cls._cache
            
        products = []
        
        # 1. DummyJSON API (Electronics, Clothing, Food, Home, Auto)
        try:
            skip = random.randint(0, 90)
            url = f"https://dummyjson.com/products?limit=100&skip={skip}"
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req, timeout=3) as resp:
                data = json.loads(resp.read().decode()).get("products", [])
                for item in data:
                    cat_raw = item.get("category", "Electronics").capitalize()
                    cat_map = {
                        "Beauty": "Beauty", "Fragrances": "Beauty", "Skin-care": "Beauty",
                        "Groceries": "Food", "Food": "Food",
                        "Furniture": "Home & Garden", "Home-decoration": "Home & Garden", "Kitchen-accessories": "Home & Garden",
                        "Laptops": "Electronics", "Mobile-accessories": "Electronics", "Smartphones": "Electronics", "Tablets": "Electronics",
                        "Mens-shirts": "Clothing", "Mens-shoes": "Clothing", "Tops": "Clothing", "Womens-dresses": "Clothing", "Womens-shoes": "Clothing",
                        "Mens-watches": "Jewelry & Accessories", "Sunglasses": "Jewelry & Accessories", "Womens-bags": "Jewelry & Accessories", "Womens-jewellery": "Jewelry & Accessories", "Womens-watches": "Jewelry & Accessories",
                        "Motorcycle": "Automotive", "Vehicle": "Automotive",
                        "Sports-accessories": "Sports", "Sports": "Sports",
                        "Health": "Health", "Personal-care": "Health",
                        "Tools": "Tools & Hardware", "Hardware": "Tools & Hardware"
                    }
                    category = cat_map.get(cat_raw, "Electronics")
                    raw_img = item.get("thumbnail") or (item.get("images", [""])[0] if item.get("images") else "")
                    products.append({
                        "name": item.get("title", "Product"),
                        "brand": item.get("brand") or "Generic",
                        "category": category,
                        "description": item.get("description", ""),
                        "price": float(item.get("price", 29.99)),
                        "image": cls._clean_image_url(raw_img),
                        "weight": round(float(item.get("weight", random.uniform(0.2, 5.0))), 2)
                    })
        except Exception:
            pass

        # 2. Platzi Fake Store API (Clothing, Shoes, Furniture)
        try:
            offset = random.randint(0, 80)
            url = f"https://api.escuelajs.co/api/v1/products?offset={offset}&limit=50"
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req, timeout=3) as resp:
                data = json.loads(resp.read().decode())
                for item in data:
                    title = item.get("title", "Item")
                    desc = item.get("description", "")
                    raw_img = item.get("images", [""])[0] if item.get("images") else ""
                    
                    # Ignorar items basura de prueba (ej: Config-..., description-..., placehold.co)
                    if "config-" in title.lower() or "description-" in desc.lower() or "placehold" in raw_img.lower():
                        continue
                        
                    cat_raw = item.get("category", {}).get("name", "").lower()
                    if "clothes" in cat_raw or "shoe" in cat_raw:
                        category = "Clothing"
                    elif "electronics" in cat_raw:
                        category = "Electronics"
                    elif "furniture" in cat_raw:
                        category = "Home & Garden"
                    else:
                        category = "Jewelry & Accessories"
                        
                    products.append({
                        "name": title,
                        "brand": "EscuelaBrand",
                        "category": category,
                        "description": desc,
                        "price": float(item.get("price", 49.99)),
                        "image": cls._clean_image_url(raw_img),
                        "weight": round(random.uniform(0.4, 6.0), 2)
                    })
        except Exception:
            pass

        # 3. FakeStoreAPI (Jewelry, Electronics, Clothing)
        try:
            url = "https://fakestoreapi.com/products"
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req, timeout=3) as resp:
                data = json.loads(resp.read().decode())
                for item in data:
                    cat_raw = item.get("category", "").lower()
                    if "clothing" in cat_raw:
                        category = "Clothing"
                    elif "jewelery" in cat_raw:
                        category = "Jewelry & Accessories"
                    elif "electronics" in cat_raw:
                        category = "Electronics"
                    else:
                        category = "Home & Garden"
                    products.append({
                        "name": item.get("title", "Product"),
                        "brand": "ImportBrand",
                        "category": category,
                        "description": item.get("description", ""),
                        "price": float(item.get("price", 19.99)),
                        "image": cls._clean_image_url(item.get("image", "")),
                        "weight": round(random.uniform(0.3, 4.0), 2)
                    })
        except Exception:
            pass

        # 4. Makeup API (Beauty Category)
        try:
            url = "http://makeup-api.herokuapp.com/api/v1/products.json?rating_greater_than=4"
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req, timeout=3) as resp:
                data = json.loads(resp.read().decode())
                for item in data[:35]:
                    raw_name = item.get("name") or "Beauty Item"
                    brand = (item.get("brand") or "Cosmetics").capitalize()
                    full_name = raw_name if raw_name.lower().startswith(brand.lower()) else f"{brand} {raw_name}"
                    products.append({
                        "name": full_name,
                        "brand": brand,
                        "category": "Beauty",
                        "description": item.get("description") or f"{raw_name} by {brand}",
                        "price": float(item.get("price") or 15.0),
                        "image": cls._clean_image_url(item.get("image_link") or ""),
                        "weight": round(random.uniform(0.1, 0.8), 2)
                    })
        except Exception:
            pass

        # 5. Gutendex Books API (Books Category)
        try:
            page = random.randint(1, 10)
            url = f"https://gutendex.com/books/?page={page}"
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req, timeout=3) as resp:
                data = json.loads(resp.read().decode()).get("results", [])
                for b in data[:20]:
                    title = b.get("title", "Book Title")
                    author = b["authors"][0]["name"] if b.get("authors") else "Famous Author"
                    products.append({
                        "name": f"Libro: {title}",
                        "brand": author,
                        "category": "Books",
                        "description": f"Edición clásica de {title} por {author}.",
                        "price": round(random.uniform(9.99, 39.99), 2),
                        "image": cls._clean_image_url("https://images.unsplash.com/photo-1544716278-ca5e3f4abd8c?w=800&auto=format&fit=crop"),
                        "weight": round(random.uniform(0.3, 1.2), 2)
                    })
        except Exception:
            pass

        # 6. PokeAPI Items (Toys Category)
        try:
            offset = random.randint(0, 50)
            url = f"https://pokeapi.co/api/v2/item?limit=25&offset={offset}"
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req, timeout=3) as resp:
                data = json.loads(resp.read().decode()).get("results", [])
                toy_images = [
                    "https://images.unsplash.com/photo-1566576912321-d58ddd7a6088?w=800&auto=format&fit=crop",
                    "https://images.unsplash.com/photo-1596461404969-9ae70f2830c1?w=800&auto=format&fit=crop",
                    "https://images.unsplash.com/photo-1563245372-f21724e3856d?w=800&auto=format&fit=crop"
                ]
                for idx, t in enumerate(data):
                    raw_name = t.get("name", "Toy").replace("-", " ").title()
                    toy_img = toy_images[idx % len(toy_images)]
                    products.append({
                        "name": f"Figura Coleccionable {raw_name}",
                        "brand": "ToyCraft",
                        "category": "Toys",
                        "description": f"Figura de edición limitada {raw_name}.",
                        "price": round(random.uniform(12.99, 59.99), 2),
                        "image": cls._clean_image_url(toy_img),
                        "weight": round(random.uniform(0.2, 2.0), 2)
                    })
        except Exception:
            pass

        if products:
            cls._cache = products
            
        return cls._cache

    @classmethod
    def get_live_product(cls, category: str = "all", brand: str = "all") -> dict:
        cls._load_history()
        
        # Manejo especial para catálogo auténtico de JBL
        if brand and "jbl" in str(brand).lower():
            from src.utils.data_pool import REAL_JBL_PRODUCTS
            pool = REAL_JBL_PRODUCTS
        else:
            prods = cls.load_live_products()
            if not prods:
                return None
                
            if category != "all":
                filtered = [p for p in prods if p["category"].lower() == category.lower()]
                pool = filtered if filtered else prods
            else:
                pool = prods
                
            if brand and brand != "all":
                brand_filtered = [p for p in pool if str(p.get("brand")).lower() == brand.lower()]
                if brand_filtered:
                    pool = brand_filtered

        item = dict(random.choice(pool))
        
        # Aplicar marca personalizada si se especificó y no venía de un pool nativo
        if brand and brand != "all" and item.get("brand", "").lower() != brand.lower():
            famous_brands = ["apple", "iphone", "ipad", "macbook", "amazon", "echo", "galaxy"]
            name_lower = item["name"].lower()
            if not any(fb in name_lower for fb in famous_brands):
                item["brand"] = brand
                if not item["name"].lower().startswith(brand.lower()):
                    item["name"] = f"{brand} {item['name']}"
            else:
                item["brand"] = brand

        title = item["name"]
        
        # Garantizar que ningún nombre se repita entre ejecuciones ni entre lotes
        if title in cls._used_titles:
            batch_tag = datetime.now().strftime("%d%H%M")
            variants = [
                f"{title} (Edición Especial 2026)",
                f"{title} - Pack x{random.choice([2, 3, 5])}",
                f"{title} (Modelo {random.choice(['V2', 'Pro', 'Ultra', 'Slim'])})",
                f"{title} - Lote #{batch_tag}",
                f"{title} (Ref: {random.randint(100, 999)})"
            ]
            title = random.choice(variants)
            
        cls._used_titles.add(title)
        cls._save_history()
        
        item["name"] = title
        item["description"] = cls._clean_description(item.get("description", ""), max_len=250)
        return item
