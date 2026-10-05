# -*- coding: utf-8 -*-
"""
Pool de datos estáticos y curados para la generación de pruebas.
Incluye nombres, ciudades, categorías, marcas y datos multilingües.
"""
import random

FIRST_NAMES = [
    "Sofia", "John", "Mary", "Lucas", "Ana", "Carlos", "Sophie", "David",
    "Linda", "Tom", "Maria", "Veronica", "Noah", "Emma", "Oliver", "Mia",
    "James", "Isabella", "William", "Ava", "Benjamin", "Charlotte", "Lucas", "Amelia"
]

LAST_NAMES = [
    "Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller", "Davis",
    "Rodriguez", "Martinez", "Hernandez", "Lopez", "Gonzalez", "Wilson", "Anderson", "Thomas"
]

CITIES = {
    "US": ["Miami", "Chicago", "Los Angeles", "New York", "Houston", "Phoenix", "Philadelphia"],
    "MX": ["CDMX", "Guadalajara", "Monterrey", "Puebla", "Tijuana", "León"],
    "ES": ["Madrid", "Barcelona", "Valencia", "Sevilla", "Bilbao", "Málaga"],
    "PT": ["Lisbon", "Porto", "Braga", "Faro", "Coimbra"],
    "GB": ["London", "Manchester", "Birmingham", "Leeds", "Glasgow"],
    "FR": ["Paris", "Lyon", "Marseille", "Toulouse", "Nice"],
    "DE": ["Berlin", "Munich", "Hamburg", "Frankfurt", "Cologne"],
    "CA": ["Toronto", "Vancouver", "Montreal", "Calgary", "Ottawa"],
    "IT": ["Rome", "Milan", "Naples", "Turin", "Palermo"],
    "BR": ["São Paulo", "Rio de Janeiro", "Brasília", "Salvador", "Fortaleza"]
}

CURRENCIES = {
    "US": "USD", "MX": "MXN", "ES": "EUR", "PT": "EUR", "GB": "GBP", 
    "FR": "EUR", "DE": "EUR", "CA": "CAD", "IT": "EUR", "BR": "BRL"
}

REAL_MATCHING_LOCATIONS = {
    "US": [
        {"city": "Beverly Hills", "state": "CA", "zip": "90210", "currency": "USD", "country": "US"},
        {"city": "New York", "state": "NY", "zip": "10001", "currency": "USD", "country": "US"},
        {"city": "Miami", "state": "FL", "zip": "33101", "currency": "USD", "country": "US"},
        {"city": "Chicago", "state": "IL", "zip": "60601", "currency": "USD", "country": "US"},
        {"city": "Houston", "state": "TX", "zip": "77001", "currency": "USD", "country": "US"},
        {"city": "Seattle", "state": "WA", "zip": "98101", "currency": "USD", "country": "US"},
        {"city": "Los Angeles", "state": "CA", "zip": "90001", "currency": "USD", "country": "US"}
    ],
    "MX": [
        {"city": "Ciudad de México", "state": "CDMX", "zip": "06000", "currency": "MXN", "country": "MX"},
        {"city": "Guadalajara", "state": "JAL", "zip": "44100", "currency": "MXN", "country": "MX"},
        {"city": "Monterrey", "state": "NL", "zip": "64000", "currency": "MXN", "country": "MX"},
        {"city": "Puebla", "state": "PUE", "zip": "72000", "currency": "MXN", "country": "MX"},
        {"city": "León", "state": "GTO", "zip": "37000", "currency": "MXN", "country": "MX"}
    ],
    "ES": [
        {"city": "Madrid", "state": "MD", "zip": "28001", "currency": "EUR", "country": "ES"},
        {"city": "Barcelona", "state": "CT", "zip": "08001", "currency": "EUR", "country": "ES"},
        {"city": "Valencia", "state": "VC", "zip": "46001", "currency": "EUR", "country": "ES"},
        {"city": "Sevilla", "state": "AN", "zip": "41001", "currency": "EUR", "country": "ES"}
    ],
    "CA": [
        {"city": "Toronto", "state": "ON", "zip": "M5V 2T6", "currency": "CAD", "country": "CA"},
        {"city": "Vancouver", "state": "BC", "zip": "V6B 1A1", "currency": "CAD", "country": "CA"},
        {"city": "Montreal", "state": "QC", "zip": "H2X 1Y4", "currency": "CAD", "country": "CA"}
    ],
    "GB": [
        {"city": "London", "state": "ENG", "zip": "EC1A 1BB", "currency": "GBP", "country": "GB"},
        {"city": "Manchester", "state": "ENG", "zip": "M1 1AG", "currency": "GBP", "country": "GB"}
    ],
    "DE": [
        {"city": "Berlin", "state": "BE", "zip": "10115", "currency": "EUR", "country": "DE"},
        {"city": "Munich", "state": "BY", "zip": "80331", "currency": "EUR", "country": "DE"}
    ]
}

def get_random_location(country_code: str = None) -> dict:
    import random
    if country_code and country_code in REAL_MATCHING_LOCATIONS:
        return random.choice(REAL_MATCHING_LOCATIONS[country_code])
    cc = random.choice(list(REAL_MATCHING_LOCATIONS.keys()))
    return random.choice(REAL_MATCHING_LOCATIONS[cc])

SKU_CATEGORIES = [
    "BEEF", "CHKN", "PORK", "VEG", "FRUIT",
    "DAIRY", "GRAIN", "SNACK", "DRINK", "SEAFOOD",
    "SPICE", "COND", "PASTA", "CLEAN", "FROZEN",
    "ELEC", "HOME", "FASH", "AUTO", "SPORT"
]

PRODUCT_CATEGORIES = [
    "Electronics",
    "Clothing",
    "Food",
    "Books",
    "Home & Garden",
    "Sports",
    "Toys",
    "Health",
    "Beauty",
    "Automotive",
    "Jewelry & Accessories",
    "Tools & Hardware"
]

BRANDS = [
    "TechCorp",
    "FashionBrand",
    "FoodCo",
    "HomeMaker",
    "SportPro",
    "BeautyPlus",
    "AutoMax",
    "BookWorld",
    "HealthFirst",
    "ToyLand",
    "Apple",
    "Huawei",
    "Samsung",
    "Sony",
    "Dell",
    "Lenovo",
    "Logitech",
    "Olay",
    "Chic Cosmetics",
    "ProVision",
    "Off White",
    "Nike",
    "Adidas",
    "Puma",
    "Ray-Ban",
    "Casio",
    "Seiko",
    "Bosch",
    "DeWalt",
    "Makita",
    "Nestle",
    "Artisan Kitchen",
    "EcoHome",
    "GreenHarvest",
    "NordicDecor"
]

SUPPLIERS_DATA = [
    {
        "code": "SUP-SOUNDWAVE", 
        "name": "SoundWave Supplies",
        "first_name": "James", "last_name": "Wilson", "phone": "555-0101",
        "email": "contact@soundwave.com", "address": "123 Audio Ave",
        "country": "USA", "state": "CA", "city": "Los Angeles"
    },
    {
        "code": "SUP-KITCHENPRO", 
        "name": "KitchenPro Corp",
        "first_name": "Maria", "last_name": "Garcia", "phone": "555-0202",
        "email": "info@kitchenpro.com", "address": "456 Cooking Blvd",
        "country": "USA", "state": "TX", "city": "Houston"
    },
    {
        "code": "SUP-URBANSTYLE", 
        "name": "UrbanStyle Imports",
        "first_name": "Sophie", "last_name": "Chen", "phone": "555-0303",
        "email": "sales@urbanstyle.com", "address": "789 Fashion St",
        "country": "USA", "state": "NY", "city": "New York"
    }
]

COUNTRIES = ["China", "USA", "Vietnam", "Mexico", "India", "Germany", "Japan", "Brazil", "Italy", "Canada"]

HS_CODES = {
    "Electronics": ["851821", "851671", "851712", "852851", "847130"],
    "Clothing": ["620342", "620462", "610510", "620212", "611020"],
    "Food": ["020230", "020130", "071190", "080550", "090111"],
    "Home": ["732393", "732181", "841582", "851679", "732490"],
    "Sports": ["950662", "950300", "950691", "950659", "950640"]
}

SHIP_METHODS = ["UPSND2DAY", "UPSND8AM", "UPSSTD", "FEDX2DAY", "DHLINT", "DHLSTD", "FEDXINT"]
SHIP_CARRIERS = ["UPS", "FedEx", "DHL"]

# Datos especializados para alimentos (Restaurado de Backup)
FOOD_PRODUCTS = {
    "en": [
        "Classic Cheeseburger", "Chicken Teriyaki Bowl", "Vegetarian Pizza",
        "Caesar Salad", "Beef Tacos", "Salmon Teriyaki", "Pasta Carbonara",
        "Greek Yogurt", "Avocado Toast", "Chicken Wings", "Fish Tacos",
        "Veggie Burger", "BBQ Ribs", "Sushi Roll", "Pad Thai",
        "Margherita Pizza", "Chicken Sandwich", "Beef Burrito", "Shrimp Fried Rice"
    ],
    "es": [
        "Hamburguesa con Queso Clásica", "Tazón de Pollo Teriyaki", "Pizza Vegetariana",
        "Ensalada César", "Tacos de Res", "Salmón Teriyaki", "Pasta Carbonara",
        "Yogur Griego", "Tostada de Aguacate", "Alitas de Pollo", "Tacos de Pescado",
        "Hamburguesa Vegetal", "Costillas BBQ", "Roll de Sushi", "Pad Thai"
    ]
}

FOOD_BRANDS = [
    "TechCorp",
    "FashionBrand",
    "FoodCo",
    "HomeMaker",
    "SportPro",
    "BeautyPlus",
    "AutoMax",
    "BookWorld",
    "HealthFirst",
    "ToyLand",
    "Apple",
    "Huawei",
    "Samsung",
    "Sony",
    "Dell",
    "Lenovo",
    "Logitech",
    "Olay",
    "Chic Cosmetics",
    "ProVision",
    "Off White",
    "Nike",
    "Adidas",
    "Puma",
    "Ray-Ban",
    "Casio",
    "Seiko",
    "Bosch",
    "DeWalt",
    "Makita",
    "Nestle",
    "Artisan Kitchen",
    "EcoHome",
    "GreenHarvest",
    "NordicDecor"
]
FOOD_CATEGORIES = ["Fast Food", "Healthy Food", "Desserts", "Beverages", "Snacks", "Organic", "Seafood", "Meat", "Dairy"]
NUTRITION_INFO = ["High in protein", "Low calorie", "Rich in vitamins", "Good source of fiber", "Organic", "Gluten-free"]

# Mapeo de idiomas soportados ampliado
SUPPORTED_LANGS = ["en", "es", "ar", "ja", "ko", "zh", "ru", "hi", "he", "th", "vi", "el", "am", "ka", "hy"]

# Aquí iría el MULTILANG_DATA completo (Restaurado de Backup con 15 idiomas)
MULTILANG_DATA = {
    "en": {
        "categories": {
            "Electronics": ["Wireless Earbuds", "Smartwatch", "Bluetooth Speaker", "Charging Dock", "USB-C Cable"],
            "Clothing": ["Classic T-Shirt", "Leather Jacket", "Travel Backpack", "Minimalist Wallet", "Sport Socks"],
            "Food": FOOD_PRODUCTS["en"],
            "Books": ["Science Fiction Novel", "Cooking Recipes Book", "History Biography", "Self-Help Guide"],
            "Home & Garden": ["Ceramic Planter Pot", "LED Table Lamp", "Soy Wax Candle", "Ergonomic Cushion"],
            "Sports": ["Non-Slip Yoga Mat", "Insulated Water Bottle", "Speed Jump Rope", "Resistance Bands Set"],
            "Toys": ["Handcrafted Wooden Blocks", "3D Wooden Puzzle", "Family Board Game", "Card Game Deck"],
            "Health": ["Multivitamin Supplements", "Organic Whey Protein", "First Aid Kit", "Digital Thermometer"],
            "Beauty": ["Hydrating Face Serum", "Organic Lip Balm Set", "Clay Face Mask", "Revitalizing Body Lotion"],
            "Automotive": ["Digital Tire Pressure Gauge", "Car Phone Mount", "Microfiber Cleaning Cloths", "Jumper Cables"]
        },
        "adjectives": ["Premium", "Eco-Friendly", "Ergonomic", "Ultra-Soft", "Durable", "Luxury", "Compact", "Modern"],
        "food_adjectives": NUTRITION_INFO,
        "brands": BRANDS,
        "food_brands": FOOD_BRANDS,
        "descriptions": ["This exceptional high-end product is meticulously designed to meet the most demanding needs."]
    },
    "es": {
        "categories": {
            "Electronics": ["Auriculares Inalámbricos", "Reloj Inteligente", "Altavoz Bluetooth", "Base de Carga Rápida"],
            "Clothing": ["Camiseta Clásica", "Chaqueta de Cuero", "Mochila de Viaje", "Cartera Mínima"],
            "Food": FOOD_PRODUCTS["es"],
            "Books": ["Novela de Ciencia Ficción", "Libro de Recetas de Cocina", "Biografía Histórica", "Guía de Autoayuda"],
            "Home & Garden": ["Maceta de Cerámica Decorativa", "Lámpara de Mesa LED", "Vela de Cera de Soja"],
            "Sports": ["Esterilla de Yoga Antideslizante", "Botella de Agua Aislada", "Cuerda de Salto Rápido"],
            "Toys": ["Bloques de Madera Artesanales", "Rompecabezas de Madera 3D", "Juego de Mesa Familiar"],
            "Health": ["Suplemento Multivitamínico", "Proteína de Suero Orgánica", "Botiquín de Primeros Auxilios"],
            "Beauty": ["Suero Facial Hidratante", "Juego de Bálsamos Labiales Orgánicos", "Mascarilla de Arcilla Facial"],
            "Automotive": ["Manómetro Digital de Neumáticos", "Soporte de Teléfono para Coche", "Paños de Limpieza"]
        },
        "adjectives": ["Premium", "Ecológico", "Ergonómico", "Ultra-Suave", "Durable", "De Lujo", "Compacto", "Moderno"],
        "food_adjectives": ["Rico en Proteínas", "Bajo en Calorías", "Orgánico", "Sin Gluten", "Artesanal"],
        "brands": ["TecnoCorp", "MarcaModa", "AlimentosCo", "HogarCreador", "DeportePro"],
        "food_brands": ["GourmetSano", "DeliciasCampo", "NutriVida", "SaborNatural"],
        "descriptions": ["Este excelente producto de alta gama está diseñado meticulosamente para satisfacer las necesidades exigentes."]
    },
    "ar": {
        "categories": {
            "Electronics": ["سماعات أذن لاسلكية", "ساعة ذكية", "مكبر صوت بلوتوث", "قاعدة شحن سريعة"],
            "Clothing": ["قميص كلاسيكي", "سترة جلدية", "حقيبة ظهر للسفر"],
            "Food": ["حبوب البن المختصة", "شاي أخضر عضوي", "جبن شيدر معتق"],
            "Books": ["رواية خيال علمي", "كتاب وصفات الطبخ", "سيرة تاريخية"],
            "Home & Garden": ["وعاء نباتات سيراميك", "مصباح طاولة إل إي دي"],
            "Sports": ["سجادة يوغا مانعة للانزلاق", "زجاجة مياه معزولة"],
            "Toys": ["مكعبات خشبية مصنوعة يدويًا", "أحجية خشبية ثلاثية الأبعاد"],
            "Health": ["مكملات الفيتامينات المتعددة", "بروتين مصل اللبن العضوي"],
            "Beauty": ["سيروم مرطب للوجه", "مجموعة مرطب شفاه عضوي"],
            "Automotive": ["مقياس ضغط الإطارات الرقمي", "حامل هاتف للسيارة"]
        },
        "adjectives": ["فاخر", "صديق للبيئة", "مريح", "ناعم للغاية", "متين"],
        "food_adjectives": ["عضوي", "طبيعي", "صحي"],
        "brands": ["تيك كورب", "فاشن براند"],
        "food_brands": ["فود كو"],
        "descriptions": ["تم تصميم هذا المنتج الاستثنائي عالي الجودة بدقة وعناية فائقة."]
    },
    "ja": {
        "categories": {
            "Electronics": ["ワイヤレスイヤホン", "スマートウォッチ", "Bluetoothスピーカー"],
            "Clothing": ["クラシックTシャツ", "レザージャケット"],
            "Food": ["スペシャル티コーヒー豆", "有機緑茶"],
            "Books": ["SF小説", "料理レシピ本"],
            "Home & Garden": ["陶器製植木鉢", "LEDテーブルランプ"],
            "Sports": ["滑り止めヨガマット", "真空断熱水筒"],
            "Toys": ["手作り木製積み木", "3D木製パズル"],
            "Health": ["マルチビタミンサプリメント", "有機ホエイプロテイン"],
            "Beauty": ["高保湿フェイスセラム", "オーガニックリップバーム"],
            "Automotive": ["デジタルタイヤ気圧計", "車載スマホホルダー"]
        },
        "adjectives": ["プレミアム", "エコフレンドリー", "人間工学デザイン", "モダン"],
        "food_adjectives": ["オーガニック", "新鮮", "高品質"],
        "brands": ["テックコープ", "ファッションブランド"],
        "food_brands": ["フードコー"],
        "descriptions": ["この優れたハイエンド製品は、細部までこだわり抜いて設計されています。"]
    },
    "ko": {
        "categories": {
            "Electronics": ["무선 이어폰", "스마트 워치", "블루투스 스피커"],
            "Clothing": ["클래식 티셔츠", "가죽 자켓"],
            "Food": ["스페셜티 원두 커피", "유기농 녹차"],
            "Books": ["공상과학 소설", "요리 레시피 북"],
            "Home & Garden": ["세라믹 화분", "LED 테이블 스탠드"],
            "Sports": ["미끄럼 방지 요가 매트", "진공 보온 보냉병"],
            "Toys": ["수공예 나무 블록", "3D 나무 퍼즐"],
            "Health": ["종합 비타민 영양제", "유기농 유청 단백질"],
            "Beauty": ["수분 공급 페이셜 세럼", "유기농 립밤"],
            "Automotive": ["디지털 타이어 공기압 측정기", "차량용 핸드폰 거치대"]
        },
        "adjectives": ["프리미엄", "친환경적", "인체공학적", "모던한"],
        "food_adjectives": ["유기농", "신선한", "최고급"],
        "brands": ["테크코프", "패션브랜드"],
        "food_brands": ["푸드코"],
        "descriptions": ["이 특별한 고급 제품은 세심하게 설계되었습니다."]
    },
    "zh": {
        "categories": {
            "Electronics": ["无线耳机", "智能手表", "蓝牙扬声器"],
            "Clothing": ["经典T恤", "皮夹克"],
            "Food": ["精品咖啡豆", "有机绿茶"],
            "Books": ["科幻小说", "烹饪食谱书"],
            "Home & Garden": ["装饰陶瓷花盆", "LED台灯"],
            "Sports": ["防滑瑜伽垫", "真空保温水杯"],
            "Toys": ["手工木制积木", "3D木制拼图"],
            "Health": ["复合维生素营养品", "有机乳清蛋白粉"],
            "Beauty": ["高保湿面部精华", "有机润唇膏"],
            "Automotive": ["数字轮胎气压表", "车载手机支架"]
        },
        "adjectives": ["优质", "环保", "符合人体工程学", "现代"],
        "food_adjectives": ["有机", "天然", "高品质"],
        "brands": ["科技谷", "时尚风暴"],
        "food_brands": ["食品优选"],
        "descriptions": ["这款出色的高端产品经过精心设计。"]
    },
    "ru": {
        "categories": {
            "Electronics": ["Беспроводные наушники", "Умные часы", "Bluetooth-колонка"],
            "Clothing": ["Классическая футболка", "Кожаная куртка"],
            "Food": ["Кофе в зернах", "Зеленый чай"],
            "Books": ["Научно-фантастический роман", "Кулинарная книга"],
            "Home & Garden": ["Керамический горшок", "Светодиодная лампа"],
            "Sports": ["Коврик для йоги", "Термобутылка"],
            "Toys": ["Деревянные кубики", "3D-пазл"],
            "Health": ["Мультивитамины", "Сывороточный протеин"],
            "Beauty": ["Сыворотка для лица", "Бальзам для гуב"],
            "Automotive": ["Манометр для шин", "Держатель для телефона"]
        },
        "adjectives": ["Премиум", "Экологичный", "Эргономичный", "Современный"],
        "food_adjectives": ["Органический", "Натуральный", "Свежий"],
        "brands": ["ТехКорп", "Бреนด์Моды"],
        "food_brands": ["ФудКо"],
        "descriptions": ["Этот исключительный высококлассный продукт разработан для удовлетворения самых требовательных потребностей."]
    }
}

# (Se pueden expandir el resto de idiomas hi, he, th, vi, el, am, ka, hy de la misma forma si es necesario)
# Para ahorrar espacio y evitar errores de tamaño de archivo, incluimos los principales.

HS_CODES = {
    "Electronics": ["8517.13.00", "8518.30.00", "8518.21.00", "8504.40.95"],
    "Clothing": ["6109.10.00", "6203.31.00", "4202.92.00", "4202.31.00"],
    "Food": ["0901.21.00", "0902.10.00", "0406.90.01", "1806.32.01"],
    "Books": ["4901.99.00", "4901.91.00", "4901.10.00"],
    "Home & Garden": ["6914.90.00", "9405.21.00", "3406.00.00", "9404.90.00"],
    "Sports": ["9506.91.00", "3924.10.00", "9506.99.00"],
    "Toys": ["9503.00.00", "9504.40.00", "9504.90.00"],
    "Health": ["2106.90.99", "3006.50.00", "9025.19.00"],
    "Beauty": ["3304.99.00", "3304.10.00", "3307.30.00"],
    "Automotive": ["9026.20.00", "3926.30.00", "6307.10.00", "8544.30.00"]
}

REAL_JBL_PRODUCTS = [
    {
        "name": "JBL Flip 6 Portable Waterproof Speaker",
        "brand": "JBL",
        "category": "Electronics",
        "description": "Bold sound for every adventure. The JBL Flip 6 delivers powerful JBL Original Pro Sound with exceptional clarity thanks to its 2-way speaker system.",
        "price": 129.95,
        "price_buy": 65.00,
        "price_wholesale": 85.00,
        "weight": 0.55,
        "length": 17.8,
        "width": 6.8,
        "height": 7.2,
        "hs_code": "8518.22.00",
        "image": "https://images.unsplash.com/photo-1545454675-3531b543be5d?w=800&auto=format&fit=crop"
    },
    {
        "name": "JBL Charge 5 Portable Wi-Fi & Bluetooth Speaker",
        "brand": "JBL",
        "category": "Electronics",
        "description": "Take the party with you no matter what the weather. The JBL Charge 5 speaker delivers bold JBL Original Pro Sound with an optimized long excursion driver.",
        "price": 179.95,
        "price_buy": 90.00,
        "price_wholesale": 120.00,
        "weight": 0.96,
        "length": 22.3,
        "width": 9.7,
        "height": 9.4,
        "hs_code": "8518.22.00",
        "image": "https://images.unsplash.com/photo-1608043152269-423dbba4e7e1?w=800&auto=format&fit=crop"
    },
    {
        "name": "JBL Boombox 3 Wi-Fi Portable Speaker with Dolby Atmos",
        "brand": "JBL",
        "category": "Electronics",
        "description": "Massive sound and deepest bass. The JBL Boombox 3 Wi-Fi speaker brings massive JBL Original Pro Sound with the deepest bass from a portable speaker.",
        "price": 499.95,
        "price_buy": 250.00,
        "price_wholesale": 340.00,
        "weight": 6.7,
        "length": 48.2,
        "width": 25.7,
        "height": 20.0,
        "hs_code": "8518.22.00",
        "image": "https://images.unsplash.com/photo-1545454675-3531b543be5d?w=800&auto=format&fit=crop"
    },
    {
        "name": "JBL Tune 510BT Wireless On-Ear Headphones",
        "brand": "JBL",
        "category": "Electronics",
        "description": "Stream powerful JBL Pure Bass sound with no strings attached. Easy to use, these headphones provide up to 40 hours of pure pleasure and an extra 2 hours of battery with just 5 minutes of power.",
        "price": 49.95,
        "price_buy": 24.00,
        "price_wholesale": 35.00,
        "weight": 0.16,
        "length": 18.5,
        "width": 15.0,
        "height": 7.5,
        "hs_code": "8518.30.20",
        "image": "https://images.unsplash.com/photo-1505740420928-5e560c06d30e?w=800&auto=format&fit=crop"
    },
    {
        "name": "JBL Go 3 Ultra-Portable Waterproof Speaker",
        "brand": "JBL",
        "category": "Electronics",
        "description": "Grab and go. JBL Go 3 features bold styling and rich JBL Pro Sound. With its new eye-catching edgy design, colorful fabrics and expressive details this a must-have accessory for your next outing.",
        "price": 39.95,
        "price_buy": 18.00,
        "price_wholesale": 27.00,
        "weight": 0.21,
        "length": 8.7,
        "width": 7.5,
        "height": 4.1,
        "hs_code": "8518.22.00",
        "image": "https://images.unsplash.com/photo-1608043152269-423dbba4e7e1?w=800&auto=format&fit=crop"
    },
    {
        "name": "JBL PartyBox 110 Portable Party Speaker with Built-in Lights",
        "brand": "JBL",
        "category": "Electronics",
        "description": "Bring a whole new dimension to any party with the unique dynamic LED lightrings, synced to the powerful sound and deep bass of the PartyBox 110.",
        "price": 399.95,
        "price_buy": 195.00,
        "price_wholesale": 270.00,
        "weight": 10.8,
        "length": 29.5,
        "width": 56.8,
        "height": 30.0,
        "hs_code": "8518.22.00",
        "image": "https://images.unsplash.com/photo-1545454675-3531b543be5d?w=800&auto=format&fit=crop"
    },
    {
        "name": "JBL Live 660NC Wireless Over-Ear NC Headphones",
        "brand": "JBL",
        "category": "Electronics",
        "description": "In your world, music is essential, so slip on a pair of JBL Live 660NC and elevate your day. Delivering signature sound punctuated with enhanced bass.",
        "price": 199.95,
        "price_buy": 95.00,
        "price_wholesale": 135.00,
        "weight": 0.25,
        "length": 20.0,
        "width": 16.0,
        "height": 8.0,
        "hs_code": "8518.30.20",
        "image": "https://images.unsplash.com/photo-1546435770-a3e426bf472b?w=800&auto=format&fit=crop"
    },
    {
        "name": "JBL Quantum 800 Wireless Gaming Headset with ANC",
        "brand": "JBL",
        "category": "Electronics",
        "description": "Level up your audio experience with JBL QuantumSOUND Signature and active noise cancelling engineered for immersive spatial positioning.",
        "price": 229.95,
        "price_buy": 110.00,
        "price_wholesale": 150.00,
        "weight": 0.41,
        "length": 21.0,
        "width": 19.0,
        "height": 9.5,
        "hs_code": "8518.30.20",
        "image": "https://images.unsplash.com/photo-1590658268037-6bf12165a8df?w=800&auto=format&fit=crop"
    },
    {
        "name": "JBL Endurance Peak 3 Waterproof True Wireless Earbuds",
        "brand": "JBL",
        "category": "Electronics",
        "description": "Power your workout with JBL Pure Bass sound and 50 hours of total playback time with IP68 dustproof and waterproof design.",
        "price": 99.95,
        "price_buy": 48.00,
        "price_wholesale": 68.00,
        "weight": 0.08,
        "length": 10.0,
        "width": 6.0,
        "height": 4.0,
        "hs_code": "8518.30.20",
        "image": "https://images.unsplash.com/photo-1590658268037-6bf12165a8df?w=800&auto=format&fit=crop"
    },
    {
        "name": "JBL Cinema SB170 2.1 Channel Soundbar with Subwoofer",
        "brand": "JBL",
        "category": "Electronics",
        "description": "220W power output, Dolby Digital, optical and HDMI ARC, four powerful full-range drivers with a wireless subwoofer for extra deep bass.",
        "price": 249.95,
        "price_buy": 120.00,
        "price_wholesale": 165.00,
        "weight": 5.2,
        "length": 90.0,
        "width": 15.0,
        "height": 20.0,
        "hs_code": "8518.22.00",
        "image": "https://images.unsplash.com/photo-1545454675-3531b543be5d?w=800&auto=format&fit=crop"
    }
]

CATEGORY_BRAND_SUGGESTIONS = {
    "Electronics": ["JBL", "Sony", "Apple", "Samsung", "Bose", "Logitech", "Philips", "Pioneer"],
    "Clothing": ["Nike", "Adidas", "Puma", "Under Armour", "Levi's", "Zara", "Tommy Hilfiger"],
    "Food": ["Nestlé", "Coca-Cola", "Kellogg's", "Pepsi", "Kraft", "Danone"],
    "Books": ["Penguin", "HarperCollins", "Random House", "Simon & Schuster", "O'Reilly"],
    "Home & Garden": ["IKEA", "Ninja", "Dyson", "KitchenPro", "DeLonghi", "Philips"],
    "Sports": ["Nike", "Adidas", "Under Armour", "Puma", "Reebok", "Wilson"],
    "Toys": ["LEGO", "Hasbro", "Mattel", "Bandai", "Funko", "ToyCraft"],
    "Health": ["Optimum Nutrition", "GNC", "Centrum", "Nature Made", "Muscletech"],
    "Beauty": ["L'Oréal", "Maybelline", "MAC", "Clinique", "Nivea", "Estée Lauder"],
    "Automotive": ["Bosch", "Michelin", "Mobil 1", "Castrol", "Pioneer Auto", "3M"],
    "Jewelry & Accessories": ["Pandora", "Swarovski", "Ray-Ban", "Casio", "Fossil", "Oakley"],
    "Tools & Hardware": ["DeWalt", "Makita", "Milwaukee", "Bosch Tools", "Stanley", "Black & Decker"]
}

BRAND_SPECIFIC_CATALOGS = {
    # Alimentos / Bebidas
    "coca-cola": [
        {"name": "Coca-Cola Original 500ml", "brand": "Coca-Cola", "category": "Food", "description": "Bebida refrescante clásica con el inconfundible y delicioso sabor de Coca-Cola original.", "price": 1.75, "weight": 0.52, "image": "https://images.unsplash.com/photo-1554866585-cd94860890b7?w=800&auto=format&fit=crop"},
        {"name": "Coca-Cola Zero Azúcar 600ml", "brand": "Coca-Cola", "category": "Food", "description": "Refresco Coca-Cola sin azúcar con todo el gran sabor y cero calorías.", "price": 1.85, "weight": 0.62, "image": "https://images.unsplash.com/photo-1622483767028-3f66f32aef97?w=800&auto=format&fit=crop"},
        {"name": "Coca-Cola Light 355ml (Lata)", "brand": "Coca-Cola", "category": "Food", "description": "Lata de Coca-Cola Light refrescante, ligera y baja en calorías.", "price": 1.25, "weight": 0.38, "image": "https://images.unsplash.com/photo-1554866585-cd94860890b7?w=800&auto=format&fit=crop"},
        {"name": "Coca-Cola Pack 12 x 355ml", "brand": "Coca-Cola", "category": "Food", "description": "Pack familiar de 12 latas de Coca-Cola Original para compartir en cualquier ocasión.", "price": 11.99, "weight": 4.5, "image": "https://images.unsplash.com/photo-1622483767028-3f66f32aef97?w=800&auto=format&fit=crop"},
        {"name": "Coca-Cola Cherry 355ml", "brand": "Coca-Cola", "category": "Food", "description": "Deliciosa variante de Coca-Cola con un toque irresistible de sabor a cereza.", "price": 1.95, "weight": 0.38, "image": "https://images.unsplash.com/photo-1554866585-cd94860890b7?w=800&auto=format&fit=crop"}
    ],
    "pepsi": [
        {"name": "Pepsi Cola Clásica 500ml", "brand": "Pepsi", "category": "Food", "description": "Bebida carbonatada refrescante y burbujeante con el auténtico sabor de Pepsi.", "price": 1.65, "weight": 0.52, "image": "https://images.unsplash.com/photo-1629203851122-3726ecdf080e?w=800&auto=format&fit=crop"},
        {"name": "Pepsi Black Sin Azúcar 600ml", "brand": "Pepsi", "category": "Food", "description": "Máximo sabor refrescante sin azúcar, ideal para disfrutar bien fría.", "price": 1.75, "weight": 0.62, "image": "https://images.unsplash.com/photo-1629203851122-3726ecdf080e?w=800&auto=format&fit=crop"},
        {"name": "Pepsi Pack 6 x 355ml", "brand": "Pepsi", "category": "Food", "description": "Pack de 6 latas de refresco Pepsi con intenso sabor carbonatado.", "price": 6.49, "weight": 2.3, "image": "https://images.unsplash.com/photo-1629203851122-3726ecdf080e?w=800&auto=format&fit=crop"}
    ],
    "nestlé": [
        {"name": "Chocolate KitKat 4 Barras", "brand": "Nestlé", "category": "Food", "description": "Crujiente galleta cubierta con suave chocolate con leche Nestlé.", "price": 1.49, "weight": 0.05, "image": "https://images.unsplash.com/photo-1541781774459-bb2af2f05b55?w=800&auto=format&fit=crop"},
        {"name": "Nescafé Clásico Café Soluble 200g", "brand": "Nestlé", "category": "Food", "description": "Café soluble puro 100% con aroma rico y sabor tostado inconfundible.", "price": 6.99, "weight": 0.35, "image": "https://images.unsplash.com/photo-1514432324607-a09d9b4aefdd?w=800&auto=format&fit=crop"},
        {"name": "Cereal Nesquik Chocolate 375g", "brand": "Nestlé", "category": "Food", "description": "Cereal integral de desayuno con irresistible sabor a chocolate enriquecido con vitaminas.", "price": 4.29, "weight": 0.42, "image": "https://images.unsplash.com/photo-1521483451569-e33803c0330c?w=800&auto=format&fit=crop"},
        {"name": "Leche Condensada La Lechera 397g", "brand": "Nestlé", "category": "Food", "description": "Leche condensada azucarada ideal para postres y repostería de alta calidad.", "price": 2.99, "weight": 0.45, "image": "https://images.unsplash.com/photo-1550583724-b2692b85b150?w=800&auto=format&fit=crop"}
    ],
    "kellogg's": [
        {"name": "Cereal Zucaritas Frosted Flakes 500g", "brand": "Kellogg's", "category": "Food", "description": "Hojuelas de maíz escarchadas con azúcar para un desayuno lleno de energía.", "price": 4.99, "weight": 0.55, "image": "https://images.unsplash.com/photo-1521483451569-e33803c0330c?w=800&auto=format&fit=crop"},
        {"name": "Cereal Corn Flakes Clásico 450g", "brand": "Kellogg's", "category": "Food", "description": "El cereal tradicional de hojuelas de maíz tostadas de Kellogg's.", "price": 4.29, "weight": 0.50, "image": "https://images.unsplash.com/photo-1521483451569-e33803c0330c?w=800&auto=format&fit=crop"},
        {"name": "Cereal Froot Loops 400g", "brand": "Kellogg's", "category": "Food", "description": "Aros de cereal con sabores frutales naturales y divertidos colores.", "price": 4.79, "weight": 0.45, "image": "https://images.unsplash.com/photo-1521483451569-e33803c0330c?w=800&auto=format&fit=crop"}
    ],
    "kraft": [
        {"name": "Kraft Macaroni & Cheese Original 206g", "brand": "Kraft", "category": "Food", "description": "La clásica pasta de macarrones con auténtica salsa cremosa de queso cheddar.", "price": 1.99, "weight": 0.22, "image": "https://images.unsplash.com/photo-1621996346565-e3d5d628151c?w=800&auto=format&fit=crop"},
        {"name": "Kraft Real Mayo Mayonesa 443ml", "brand": "Kraft", "category": "Food", "description": "Mayonesa cremosa elaborada con huevos de granja y aceite de primera calidad.", "price": 3.89, "weight": 0.48, "image": "https://images.unsplash.com/photo-1589301760014-d929f3979dbc?w=800&auto=format&fit=crop"},
        {"name": "Kraft Singles Queso Americano 16 Rebanadas", "brand": "Kraft", "category": "Food", "description": "Rebanadas individuales de queso pasteurizado americano, ideales para sándwiches y hamburguesas.", "price": 3.99, "weight": 0.34, "image": "https://images.unsplash.com/photo-1621996346565-e3d5d628151c?w=800&auto=format&fit=crop"}
    ],
    "danone": [
        {"name": "Yogur Danone Natural 4 x 125g", "brand": "Danone", "category": "Food", "description": "Pack de 4 yogures naturales cremosos elaborados con leche fresca seleccionada.", "price": 2.49, "weight": 0.55, "image": "https://images.unsplash.com/photo-1488477181946-6428a0291777?w=800&auto=format&fit=crop"},
        {"name": "Yogur Griego Oikos Vainilla 150g", "brand": "Danone", "category": "Food", "description": "Yogur estilo griego extra cremoso con un delicado toque de vainilla natural.", "price": 1.79, "weight": 0.16, "image": "https://images.unsplash.com/photo-1488477181946-6428a0291777?w=800&auto=format&fit=crop"},
        {"name": "Activia Fibra y Frutas 4 x 120g", "brand": "Danone", "category": "Food", "description": "Yogur probiótico con trozos de frutas y fibra para ayudar a la digestión diaria.", "price": 2.99, "weight": 0.52, "image": "https://images.unsplash.com/photo-1488477181946-6428a0291777?w=800&auto=format&fit=crop"}
    ],

    # Libros / Editoriales
    "penguin": [
        {"name": "Libro: 1984", "brand": "Penguin", "category": "Books", "description": "Edición clásica de la obra maestra distópica 1984 por George Orwell.", "price": 14.99, "weight": 0.35, "image": "https://images.unsplash.com/photo-1544716278-ca5e3f4abd8c?w=800&auto=format&fit=crop"},
        {"name": "Libro: Orgullo y Prejuicio", "brand": "Penguin", "category": "Books", "description": "Edición especial de Penguin Classics de Orgullo y Prejuicio por Jane Austen.", "price": 12.99, "weight": 0.40, "image": "https://images.unsplash.com/photo-1544716278-ca5e3f4abd8c?w=800&auto=format&fit=crop"},
        {"name": "Libro: El Gran Gatsby", "brand": "Penguin", "category": "Books", "description": "Edición de lujo de El Gran Gatsby por F. Scott Fitzgerald.", "price": 13.50, "weight": 0.32, "image": "https://images.unsplash.com/photo-1544716278-ca5e3f4abd8c?w=800&auto=format&fit=crop"},
        {"name": "Libro: Cien Años de Soledad", "brand": "Penguin", "category": "Books", "description": "La emblemática novela cumbre del realismo mágico por Gabriel García Márquez.", "price": 18.90, "weight": 0.50, "image": "https://images.unsplash.com/photo-1544716278-ca5e3f4abd8c?w=800&auto=format&fit=crop"}
    ],
    "harpercollins": [
        {"name": "Libro: El Hobbit", "brand": "HarperCollins", "category": "Books", "description": "La aventura épica inolvidable de Bilbo Bolsón por J.R.R. Tolkien.", "price": 16.99, "weight": 0.42, "image": "https://images.unsplash.com/photo-1544716278-ca5e3f4abd8c?w=800&auto=format&fit=crop"},
        {"name": "Libro: El Señor de los Anillos", "brand": "HarperCollins", "category": "Books", "description": "Edición completa de la trilogía fundamental de fantasía por J.R.R. Tolkien.", "price": 29.99, "weight": 1.10, "image": "https://images.unsplash.com/photo-1544716278-ca5e3f4abd8c?w=800&auto=format&fit=crop"},
        {"name": "Libro: Las Crónicas de Narnia", "brand": "HarperCollins", "category": "Books", "description": "Colección completa del mágico mundo de Narnia por C.S. Lewis.", "price": 24.50, "weight": 0.85, "image": "https://images.unsplash.com/photo-1544716278-ca5e3f4abd8c?w=800&auto=format&fit=crop"}
    ],
    "random house": [
        {"name": "Libro: Matar a un Ruiseñor", "brand": "Random House", "category": "Books", "description": "Edición clásica de Matar a un Ruiseñor por Harper Lee.", "price": 15.20, "weight": 0.38, "image": "https://images.unsplash.com/photo-1544716278-ca5e3f4abd8c?w=800&auto=format&fit=crop"},
        {"name": "Libro: Sapiens: De animales a dioses", "brand": "Random House", "category": "Books", "description": "Breve historia de la humanidad por Yuval Noah Harari.", "price": 21.90, "weight": 0.55, "image": "https://images.unsplash.com/photo-1544716278-ca5e3f4abd8c?w=800&auto=format&fit=crop"}
    ],

    # Ropa y Calzado / Ropa Deportiva
    "nike": [
        {"name": "Zapatillas Nike Air Max SC", "brand": "Nike", "category": "Clothing", "description": "Zapatillas deportivas con amortiguación Air visible para comodidad todo el día.", "price": 89.99, "weight": 0.85, "image": "https://images.unsplash.com/photo-1542291026-7eec264c27ff?w=800&auto=format&fit=crop"},
        {"name": "Camiseta Deportiva Nike Dri-FIT", "brand": "Nike", "category": "Clothing", "description": "Camiseta ligera y transpirable con tecnología absorbente de sudor Dri-FIT.", "price": 34.99, "weight": 0.20, "image": "https://images.unsplash.com/photo-1521572267360-ee0c2909d518?w=800&auto=format&fit=crop"},
        {"name": "Sudadera Nike Club Fleece con Capucha", "brand": "Nike", "category": "Clothing", "description": "Sudadera clásica con forro polar cepillado para una calidez suave y cómoda.", "price": 64.99, "weight": 0.60, "image": "https://images.unsplash.com/photo-1556905055-8f358a7a47b2?w=800&auto=format&fit=crop"},
        {"name": "Mochila Nike Elemental 21L", "brand": "Nike", "category": "Clothing", "description": "Mochila espaciosa con múltiples compartimentos para entrenamiento y uso diario.", "price": 39.99, "weight": 0.45, "image": "https://images.unsplash.com/photo-1553062407-98eeb64c6a62?w=800&auto=format&fit=crop"}
    ],
    "adidas": [
        {"name": "Zapatillas Adidas Ultraboost Light", "brand": "Adidas", "category": "Clothing", "description": "Calzado de running de alto rendimiento con amortiguación Boost ultrasensible.", "price": 149.99, "weight": 0.80, "image": "https://images.unsplash.com/photo-1584735935682-2f2b69dff9d2?w=800&auto=format&fit=crop"},
        {"name": "Zapatillas Adidas Superstar Clásicas", "brand": "Adidas", "category": "Clothing", "description": "El icónico diseño de puntera de concha que definió el estilo urbano contemporáneo.", "price": 99.99, "weight": 0.85, "image": "https://images.unsplash.com/photo-1584735935682-2f2b69dff9d2?w=800&auto=format&fit=crop"},
        {"name": "Chaqueta Adidas Essentials 3 Franjas", "brand": "Adidas", "category": "Clothing", "description": "Chaqueta deportiva de corte clásico confeccionada en tejido suave y duradero.", "price": 59.99, "weight": 0.50, "image": "https://images.unsplash.com/photo-1521572267360-ee0c2909d518?w=800&auto=format&fit=crop"}
    ],
    "puma": [
        {"name": "Zapatillas Puma Suede Classic XXI", "brand": "Puma", "category": "Clothing", "description": "Zapatillas legendarias de ante suave con el diseño atemporal y deportivo de Puma.", "price": 74.99, "weight": 0.75, "image": "https://images.unsplash.com/photo-1608231387042-66d1773070a5?w=800&auto=format&fit=crop"},
        {"name": "Sudadera Puma ESS Logo Hoodie", "brand": "Puma", "category": "Clothing", "description": "Sudadera de corte regular con el llamativo logotipo de Puma estampado en el pecho.", "price": 49.99, "weight": 0.55, "image": "https://images.unsplash.com/photo-1556905055-8f358a7a47b2?w=800&auto=format&fit=crop"}
    ],

    # Electrónica
    "apple": [
        {"name": "Apple iPhone 15 Pro 128GB", "brand": "Apple", "category": "Electronics", "description": "Smartphone de titanio de grado aeroespacial con chip A17 Pro y cámara de 48 MP.", "price": 999.00, "weight": 0.18, "image": "https://images.unsplash.com/photo-1510557880182-3d4d3cba35a5?w=800&auto=format&fit=crop"},
        {"name": "Apple AirPods Pro (2.ª generación)", "brand": "Apple", "category": "Electronics", "description": "Auriculares inalámbricos con cancelación activa de ruido 2x y audio espacial.", "price": 249.00, "weight": 0.05, "image": "https://images.unsplash.com/photo-1600294037681-c80b4cb5b434?w=800&auto=format&fit=crop"},
        {"name": "Apple Watch Series 9 GPS 45mm", "brand": "Apple", "category": "Electronics", "description": "Reloj inteligente avanzado con pantalla Retina brillante y sensor de salud potente.", "price": 429.00, "weight": 0.04, "image": "https://images.unsplash.com/photo-1508685096489-7aacd43bd3b1?w=800&auto=format&fit=crop"},
        {"name": "Apple MacBook Air 13\" Chip M2", "brand": "Apple", "category": "Electronics", "description": "Portátil ultraligero y silencioso con pantalla Liquid Retina y batería de 18 horas.", "price": 1099.00, "weight": 1.24, "image": "https://images.unsplash.com/photo-1517336714731-489689fd1ca8?w=800&auto=format&fit=crop"}
    ],
    "samsung": [
        {"name": "Samsung Galaxy S24 Ultra 256GB", "brand": "Samsung", "category": "Electronics", "description": "Smartphone insignia con Galaxy AI, marco de titanio y cámara de 200 MP.", "price": 1199.99, "weight": 0.23, "image": "https://images.unsplash.com/photo-1610945265064-0e34e5519bbf?w=800&auto=format&fit=crop"},
        {"name": "Samsung Galaxy Buds2 Pro", "brand": "Samsung", "category": "Electronics", "description": "Auriculares inalámbricos de alta fidelidad de 24 bits con cancelación activa de ruido.", "price": 189.99, "weight": 0.05, "image": "https://images.unsplash.com/photo-1590658268037-6bf12165a8df?w=800&auto=format&fit=crop"},
        {"name": "Samsung Smart TV 55\" Crystal UHD 4K", "brand": "Samsung", "category": "Electronics", "description": "Televisor inteligente 4K con procesador Crystal, HDR y diseño sin bordes.", "price": 449.99, "weight": 14.2, "image": "https://images.unsplash.com/photo-1593359677879-a4bb92f829d1?w=800&auto=format&fit=crop"}
    ],
    "sony": [
        {"name": "Sony WH-1000XM5 Auriculares Inalámbricos", "brand": "Sony", "category": "Electronics", "description": "Líderes en cancelación de ruido con audio de alta resolución y llamadas nítidas.", "price": 399.99, "weight": 0.25, "image": "https://images.unsplash.com/photo-1505740420928-5e560c06d30e?w=800&auto=format&fit=crop"},
        {"name": "Sony PlayStation 5 Consola", "brand": "Sony", "category": "Electronics", "description": "Consola de videojuegos de última generación con gráficos 4K y SSD ultrarrápido.", "price": 499.99, "weight": 4.5, "image": "https://images.unsplash.com/photo-1606813907291-d86efa9b94db?w=800&auto=format&fit=crop"}
    ],

    # Joyería y Accesorios
    "pandora": [
        {"name": "Pulsera Moments de Cadena de Serpiente Pandora", "brand": "Pandora", "category": "Jewelry & Accessories", "description": "Elegante pulsera icónica acabada a mano en plata de primera ley.", "price": 75.00, "weight": 0.03, "image": "https://images.unsplash.com/photo-1611591475155-4286fb7c2e74?w=800&auto=format&fit=crop"},
        {"name": "Charm Colgante Corazón Brillante Pandora", "brand": "Pandora", "category": "Jewelry & Accessories", "description": "Charm en forma de corazón con circonitas cúbicas transparentes engastadas.", "price": 45.00, "weight": 0.01, "image": "https://images.unsplash.com/photo-1599643478518-a784e5dc4c8f?w=800&auto=format&fit=crop"},
        {"name": "Anillo Tiara Real de Plata Pandora", "brand": "Pandora", "category": "Jewelry & Accessories", "description": "Anillo decorado con motivos de tiara y detalles brillantes en plata de ley.", "price": 55.00, "weight": 0.01, "image": "https://images.unsplash.com/photo-1605100804763-247f67b3557e?w=800&auto=format&fit=crop"}
    ],
    "casio": [
        {"name": "Reloj Digital Casio Vintage A168WA", "brand": "Casio", "category": "Jewelry & Accessories", "description": "Reloj unisex de estilo retro con pulsera de acero inoxidable y luz Illuminator.", "price": 32.00, "weight": 0.08, "image": "https://images.unsplash.com/photo-1524805444758-089113d48a6d?w=800&auto=format&fit=crop"},
        {"name": "Reloj Casio G-Shock GA-2100", "brand": "Casio", "category": "Jewelry & Accessories", "description": "Estructura de carbono resistente a impactos, sumergible a 200 metros.", "price": 99.00, "weight": 0.12, "image": "https://images.unsplash.com/photo-1524805444758-089113d48a6d?w=800&auto=format&fit=crop"}
    ],

    # Juguetes
    "lego": [
        {"name": "LEGO Star Wars Halcón Milenario", "brand": "LEGO", "category": "Toys", "description": "Set de construcción detallado de la nave espacial más famosa de la galaxia.", "price": 169.99, "weight": 1.95, "image": "https://images.unsplash.com/photo-1585366119957-e9730b6d0f60?w=800&auto=format&fit=crop"},
        {"name": "LEGO Icons Ramo de Flores", "brand": "LEGO", "category": "Toys", "description": "Hermoso set botánico decorativo con rosas, margaritas y amapolas para armar.", "price": 59.99, "weight": 0.75, "image": "https://images.unsplash.com/photo-1585366119957-e9730b6d0f60?w=800&auto=format&fit=crop"},
        {"name": "LEGO City Estación de Policía", "brand": "LEGO", "category": "Toys", "description": "Set de acción con patrulla policial, helicóptero y figuras de oficiales.", "price": 69.99, "weight": 1.20, "image": "https://images.unsplash.com/photo-1566576912321-d58ddd7a6088?w=800&auto=format&fit=crop"}
    ],
    "mattel": [
        {"name": "Barbie Muñeca Fashionista Vestido Floral", "brand": "Mattel", "category": "Toys", "description": "Muñeca Barbie con atuendo moderno y accesorios a la moda.", "price": 14.99, "weight": 0.25, "image": "https://images.unsplash.com/photo-1566576912321-d58ddd7a6088?w=800&auto=format&fit=crop"},
        {"name": "Hot Wheels Pack 5 Coches de Carreras", "brand": "Mattel", "category": "Toys", "description": "Colección de 5 vehículos a escala 1:64 con diseños de alta velocidad.", "price": 8.99, "weight": 0.30, "image": "https://images.unsplash.com/photo-1596461404969-9ae70f2830c1?w=800&auto=format&fit=crop"}
    ]
}

REAL_CATEGORY_IMAGES = {
    "Electronics": [
        "https://images.unsplash.com/photo-1505740420928-5e560c06d30e?w=800&auto=format&fit=crop",
        "https://images.unsplash.com/photo-1545454675-3531b543be5d?w=800&auto=format&fit=crop",
        "https://images.unsplash.com/photo-1608043152269-423dbba4e7e1?w=800&auto=format&fit=crop",
        "https://images.unsplash.com/photo-1546435770-a3e426bf472b?w=800&auto=format&fit=crop"
    ],
    "Toys": [
        "https://images.unsplash.com/photo-1566576912321-d58ddd7a6088?w=800&auto=format&fit=crop",
        "https://images.unsplash.com/photo-1596461404969-9ae70f2830c1?w=800&auto=format&fit=crop",
        "https://images.unsplash.com/photo-1563245372-f21724e3856d?w=800&auto=format&fit=crop"
    ],
    "Clothing": [
        "https://images.unsplash.com/photo-1521572267360-ee0c2909d518?w=800&auto=format&fit=crop",
        "https://images.unsplash.com/photo-1542291026-7eec264c27ff?w=800&auto=format&fit=crop"
    ],
    "Beauty": [
        "https://images.unsplash.com/photo-1596462502278-27bfdc403348?w=800&auto=format&fit=crop"
    ],
    "Books": [
        "https://images.unsplash.com/photo-1544716278-ca5e3f4abd8c?w=800&auto=format&fit=crop"
    ],
    "Food": [
        "https://images.unsplash.com/photo-1514432324607-a09d9b4aefdd?w=800&auto=format&fit=crop"
    ],
    "Home & Garden": [
        "https://images.unsplash.com/photo-1513694203232-719a280e022f?w=800&auto=format&fit=crop"
    ]
}

def get_real_category_image(category: str) -> str:
    images = REAL_CATEGORY_IMAGES.get(category, REAL_CATEGORY_IMAGES["Electronics"])
    return random.choice(images)
