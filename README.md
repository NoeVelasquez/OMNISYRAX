# 🌌 OMNISYRAX: Plataforma Maestra de Generación de Datos Logísticos

**OMNISYRAX** es una plataforma de grado industrial diseñada para automatizar la creación de ecosistemas de datos masivos, precisos, multilingües y con productos **100% coherentes y reales**. Ideal para pruebas de estrés, demostraciones de software y validación de flujos logísticos complejos en CONDOR, OMNIO, Shipedge y Shopify.

---

## 🌟 Características Principales

- **🌐 Consultas en APIs Vivas de Internet**: Consulta APIs públicas reales en tiempo de ejecución (*DummyJSON, FakeStoreAPI, Platzi API, Makeup API, Gutendex, PokeAPI*) notificando explícitamente en consola.
- **🏷️ Catálogos Auténticos y Específicos por Marca**: Colecciones curadas para las marcas líderes de cada categoría (*Coca-Cola, Pepsi, Nestlé, Kellogg's, Kraft, Danone, Apple, Samsung, Sony, Nike, Adidas, Puma, Pandora, Casio, LEGO, Mattel, Penguin, HarperCollins, DeWalt, Makita*, etc.), eliminando cualquier mezcla o contaminación incongruente entre marcas.
- **🌍 Motor de Traducción y Localización en Tiempo Real (`TextTranslator`)**:
  - Traducción automática multinivel (Online vía API + Caché persistente en disco + Reglas heurísticas offline).
  - Títulos y descripciones 100% naturales en **Español (`es`)**, **Inglés (`en`)** o **Multilingüe (`all`)**.
  - Localización inteligente de prefijos editoriales (*"Libro: ... / Book: ..."*) y figuras (*"Figura Coleccionable ... / Collectible Figure ..."*).
- **⏱️ Nomenclatura Segura sin Sobrescritura**:
  - Timestamps de alta precisión con segundos (`%Y%m%d_%H%M%S`) y resolución de colisiones automáticas.
- **📷 Fotografías HD Reales**: Sin URLs rotas ni marcadores de posición genéricos (*sin placehold.co ni picsum*).
- **🛡️ Compatibilidad Estricta CONDOR / OMNIO (Límite 255 caracteres)**: Sanitización automática de descripciones para cumplir con el límite `VARCHAR(255)` de base de datos.
- **📄 Extracción Inteligente de SKUs desde CSV**: Autodetección de columnas de SKUs desde cualquier archivo CSV para encadenar la generación de órdenes o inventario.
- **⚡ Suite Completa de Pruebas y Carga API**: Carga directa de órdenes, simulación de webhooks, inyección de devoluciones (RMA) y pruebas de estrés masivas con métricas de latencia y RPS.

---

## 🚀 Guía de Inicio Rápido

### 1. Requisitos Previos
- **Python 3.9** o superior.
- Terminal (macOS, Linux o Windows).

### 2. Instalación
```bash
# Navega al directorio del proyecto
cd OMNISYRAX

# Instala las dependencias necesarias
pip install -r requirements.txt
```

### 3. Ejecución

#### A. El Oráculo (Modo Interactivo)
Simplemente ejecuta el oráculo interactivo por menús:
```bash
python3 omnisyrax.py
```
*Incluye selector dinámico de misiones (Archivos locales CSV/XML/PDF, Carga API en vivo, Suite de pruebas y simulaciones).*

#### B. Modo Línea de Comandos (CLI)
```bash
# Generar 50 productos de Electrónica marca Samsung en español
python3 omnisyrax.py products --count 50 --category Electronics --brand Samsung --lang es

# Generar 20 órdenes de venta usando SKUs extraídos de un archivo CSV previo
python3 omnisyrax.py orders --count 20 --skus-file data/products_20260907_163800.csv

# Generar productos para Shopify
python3 omnisyrax.py shopify --count 20 --category Clothing --brand Nike --lang es

# Generar archivos EDI XML
python3 omnisyrax.py edi --count 5

# Generar archivos Cargo Hub (.neworders)
python3 omnisyrax.py ch --count 5
```

---

## 🛠️ Catálogo de Comandos y Formatos

### 📦 Generación de Productos
| Comando | Parámetros Principales | Formato | Descripción |
| :--- | :--- | :--- | :--- |
| `products` | `--count`, `--category`, `--brand`, `--lang` | CSV (19 cols) | Formato estándar de 19 columnas optimizado para CONDOR/OMNIO. |
| `shopify` | `--count`, `--category`, `--brand`, `--lang` | CSV Shopify | Compatible con el importador de productos de Shopify. |
| `shipedge` | `--count`, `--category`, `--brand`, `--lang` | CSV Shipedge | Formato técnico para Shipedge (DC1, Serial Numbers, Harmonization HS). |

**Estructura del CSV Estándar (19 Columnas):**
```csv
product,description,images,type_product,category,brand,name,sku,supplier,upc,hs_code,country_origin,length,width,height,weight,price_buy,price_wholesale,price_retail
```

### 🛍️ Órdenes, Compras e Inventario
| Comando | Parámetros Principales | Formato | Descripción |
| :--- | :--- | :--- | :--- |
| `orders` | `--count`, `--multi-sku`, `--skus-file`, `--days-back`, `--profile` | CSV / API | Órdenes de venta con direcciones reales y clientes multirregionales. |
| `po` | `--count`, `--skus` | CSV | Órdenes de compra (Purchase Orders) asociadas a proveedores. |
| `inventory` | `--count`, `--skus` | CSV | Stock de almacén y existencias iniciales. |
| `transfers` | `--count` | CSV | Movimientos y transferencias de inventario entre almacenes. |
| `packages` | `--count` | CSV | Plantillas y dimensiones de cajas/paquetes. |

### 📠 Integraciones Especiales (XML / PDF)
| Comando | Parámetros | Formato | Descripción |
| :--- | :--- | :--- | :--- |
| `edi` | `--count`, `--items-mode`, `--sku-choice` | XML (.xml) | Archivos EDI estándar para transacciones electrónicas B2B. |
| `ch` | `--count` | Cargo Hub (.neworders) | Archivos `.neworders` para Cargo Hub (The Home Depot). |
| `pdf` | `--count`, `--size-mb` | PDF (.pdf) | Archivos PDF con peso específico en MB para pruebas de carga de adjuntos. |

---

## 🏷️ Marcas y Categorías Soportadas

OMNISYRAX cuenta con datasets oficiales y aislamiento garantizado para:

| Categoría | Marcas Destacadas |
| :--- | :--- |
| **Alimentos (Food)** | *Coca-Cola, Pepsi, Nestlé, Kellogg's, Kraft, Danone* |
| **Electrónica (Electronics)** | *Apple, Samsung, Sony, Bose, JBL, Logitech, Philips, Pioneer* |
| **Ropa y Calzado (Clothing)** | *Nike, Adidas, Puma, Under Armour, Levi's, Zara, Tommy Hilfiger* |
| **Libros (Books)** | *Penguin, HarperCollins, Random House, Simon & Schuster, O'Reilly* |
| **Joyería y Accesorios** | *Pandora, Swarovski, Ray-Ban, Casio, Fossil, Oakley* |
| **Juguetes (Toys)** | *LEGO, Hasbro, Mattel, Bandai, Funko, ToyCraft* |
| **Herramientas (Tools & Hardware)**| *DeWalt, Makita, Milwaukee, Bosch Tools, Stanley, Black & Decker* |
| **Belleza (Beauty)** | *L'Oréal, Maybelline, MAC, Clinique, Nivea, Estée Lauder* |
| **Salud (Health)** | *Optimum Nutrition, GNC, Centrum, Nature Made, Muscletech* |
| **Hogar y Jardín (Home & Garden)** | *IKEA, Ninja, Dyson, KitchenPro, DeLonghi, Philips* |
| **Automotriz (Automotive)** | *Bosch, Michelin, Mobil 1, Castrol, Pioneer Auto, 3M* |

---

## 🛡️ Estándar de SKUs y Códigos Aduaneros
- **Patrón de SKU:** `SKU-[CAT]-[MARCA]-[YYMMDD]-[RANDOM]`
  *(Ejemplo: `SKU-FOO-COCA-260907-9R5U`, `SKU-ELE-SAMS-260907-7K2X`)*
- **Códigos HS Aduaneros:** Mapeados por categoría según la clasificación arancelaria internacional oficial.
- **Códigos UPC:** Generación de códigos de barra numéricos válidos de 12 dígitos.

---

## 📁 Estructura del Proyecto

```text
OMNISYRAX/
├── omnisyrax.py               # Punto de entrada interactivo y CLI principal
├── requirements.txt           # Dependencias del proyecto
├── README.md                  # Documentación oficial
├── data/                      # Archivos CSV de salida y caché local
│   ├── ch_neworders/          # Archivos .neworders para Cargo Hub
│   ├── edi_xmls/              # Archivos XML de EDI
│   └── pdfs/                  # Archivos PDF generados
├── src/
│   ├── core/                  # Clases base de generadores y configuración
│   ├── domain/                # Modelos de datos Pydantic (Product, Order, etc.)
│   ├── exporters/             # Exportadores a CSV, XML, PDF y API Client
│   ├── generators/            # Generadores específicos de cada tipo de entidad
│   └── utils/
│       ├── api_product_fetcher.py # Cliente de APIs en vivo e integración de marcas
│       ├── data_pool.py           # Datasets estáticos, catálogos de marca e imágenes HD
│       └── translator.py          # Motor de traducción y localización multilingüe
```

---

## 🔐 Configuración de Credenciales API (`config/credentials.yaml`)

Para habilitar la carga directa a servidores CONDOR / OMNIO:
```yaml
credentials:
  qa_server:
    token: "tu_bearer_token"
    company_id: "id_empresa_o_tenant"
    api_url: "https://qa-api.omnio.com"
```

---

> [!TIP]
> Todos los archivos generados quedan almacenados en la carpeta `data/` listos para ser importados o consumidos por tus suites de pruebas.
