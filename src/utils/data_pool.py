# -*- coding: utf-8 -*-
"""
Pool de datos estáticos y curados para la generación de pruebas.
Incluye nombres, ciudades, categorías, marcas y datos multilingües.
"""

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
