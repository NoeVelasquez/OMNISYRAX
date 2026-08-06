# 🌌 OMNISYRAX: Plataforma Maestra de Generación de Datos Logísticos

**OMNISYRAX** es una solución de grado industrial diseñada para automatizar la creación de ecosistemas de datos masivos, precisos, multilingües y con productos **100% reales**. Ideal para pruebas de estrés, demostraciones de software y validación de flujos logísticos complejos en CONDOR, OMNIO, Shipedge y Shopify.

---

## 🌟 ¿Por qué OMNISYRAX?

En el mundo de la logística, los datos de prueba suelen ser aburridos y repetitivos. OMNISYRAX rompe esa barrera ofreciendo:
- **🌐 Búsqueda en APIs Vivas de Internet**: Consulta APIs externas reales en tiempo real (*DummyJSON, FakeStoreAPI, Makeup API, Gutendex, PokeAPI*) notificando explícitamente en pantalla durante la generación.
- **🎧 Catálogo Oficial de Productos Reales (JBL, Sony, Nike, etc.)**: Productos auténticos con precios MSRP oficiales, dimensiones reales, pesos y códigos aduaneros HS oficializados.
- **📷 Fotografías HD 100% Reales**: Eliminación total de imágenes de relleno (sin *Picsum* ni *placehold.co*). Todas las URLs apuntan a fotografías reales de alta resolución.
- **🛡️ Compatibilidad Estricta CONDOR / OMNIO (Límite 255 caracteres)**: Sanitización automática de descripciones para ajustarse estrictamente al límite `VARCHAR(255)` de las tablas de CONDOR, evitando fallos de base de datos.
- **📄 Extracción Automática de SKUs desde CSV**: Autodetecta columnas de SKUs desde cualquier archivo CSV cargado para reutilizarlos en nuevas órdenes o inventario.
- **Multilenguaje Real**: Generación en 15+ idiomas con coherencia cultural.
- **Unicidad Garantizada**: Algoritmos basados en timestamps y sufijos aleatorios que eliminan el error de "ID duplicado".

---

## 🚀 Guía de Inicio Rápido

### 1. Requisitos Previos
- **Python 3.9** o superior.
- Una terminal (CMD, PowerShell o Terminal de macOS/Linux).

### 2. Instalación
```bash
# Navega a la carpeta del proyecto
cd OMNISYRAX

# Instala las dependencias necesarias
pip install -r requirements.txt
```

### 3. Ejecución
Tienes dos caminos para dominar OMNISYRAX:

#### A. El Oráculo (Modo Interactivo)
Simplemente escribe el nombre del programa y déjate guiar por el menú visual:
```bash
python3 omnisyrax.py
```
*Incluye selección de marcas por teclado/lista destacada, extracción de SKUs desde CSV y aviso visual de consulta vía Internet.*

#### B. La Forja (Modo Comandos Directos)
Usa comandos con opciones avanzadas de categoría y marca:
```bash
python3 omnisyrax.py products --count 10 --category Electronics --brand JBL
python3 omnisyrax.py orders --count 10 --skus-file data/orders_20260806_1452.csv
```

---

## 🛠️ Comandos y Generadores en Detalle

### 📦 Catálogo de Productos (Estructura Estándar de 19 Columnas)
| Comando | Opciones | Formato | Uso Principal |
| :--- | :--- | :--- | :--- |
| `products` | `--count`, `--category`, `--brand`, `--lang` | CSV (19 cols) | Productos estándar ajustados a 255 caracteres para CONDOR/OMNIO. |
| `shipedge` | `--count`, `--category`, `--brand`, `--lang` | CSV | Importación técnica para Shipedge (DC1, Serial Numbers, Customs). |
| `shopify` | `--count`, `--category`, `--brand`, `--lang` | CSV | Archivo listo para importar en el administrador de Shopify. |

**Estructura del CSV Estándar:**
`product,description,images,type_product,category,brand,name,sku,supplier,upc,hs_code,country_origin,length,width,height,weight,price_buy,price_wholesale,price_retail`

### 🛍️ Flujo de Órdenes y Compras
| Comando | Opciones | Formato | Uso Principal |
| :--- | :--- | :--- | :--- |
| `orders` | `--count`, `--multi-sku`, `--skus-file`, `--days-back` | CSV/API | Órdenes de venta con clientes, direcciones reales y extracción de SKUs. |
| `po` | `--count`, `--skus` | CSV | Órdenes de compra vinculadas a proveedores específicos. |
| `transfers` | `--count` | CSV | Movimientos de stock entre almacenes (A -> B). |

**Ejemplo:** `python3 omnisyrax.py orders --count 10 --skus-file data/orders_20260806_1452.csv`

### 📠 Integraciones EDI y Cargo Hub
| Comando | Formato | Uso Principal |
| :--- | :--- | :--- |
| `ch` | .neworders | Formato exacto para Commerce Hub (The Home Depot). |
| `edi` | .xml | Estándar EDI para transacciones B2B. |

### 🛠️ Utilidades Especiales
| Comando | Formato | Uso Principal |
| :--- | :--- | :--- |
| `packages` | CSV | Configuración de Cajas y Paquetes (Templates). |
| `pdf` | PDF | Archivos de gran tamaño (MB) para pruebas de carga. |
| `inventory` | CSV | Ajustes de stock masivos con imanes HD reales. |

---

## 🎧 Catálogo Auténtico de Marcas (JBL, Sony, Nike, etc.)

OMNISYRAX incluye datasets oficiales de productos reales de mercado:
- **JBL**: *Flip 6, Charge 5, Boombox 3, Tune 510BT, PartyBox 110, Quantum 800, Live 660NC, Endurance Peak 3, Cinema SB170*.
- **Precios e Información Oficial**: Incluye precios retail MSRP reales, precios mayoreo/costo, pesos exactos, dimensiones de caja y códigos aduaneros HS (`8518.22.00` / `8518.30.20`).
- **Filtrado Inteligente**: Submenú de selección de marca interactivo (Aleatorio, Lista Destacada por Categoría o Ingreso Manual).

---

## 🌍 El Motor Multilingüe (Data Pool)

Soporta múltiples idiomas y categorías:
- **Idiomas**: Inglés, Español, Árabe, Japonés, Coreano, Chino, Ruso, Hindi, Hebreo, Tailandés, Vietnamita, Griego, Amhárico, Georgiano y Armenio.
- **Categorías**: Electrónica, Ropa, Comida (Food), Libros, Hogar, Deportes, Juguetes, Salud, Belleza y Automotriz.

---

## 🛡️ Sistema de Unicidad y Compatibilidad

- **Patrón SKU**: `SKU-[CAT]-[MARCA]-[YYMMDD]-[RANDOM]`
- **Compatibilidad CONDOR/OMNIO**: Descripciones sanitizadas sin HTML roto ni saltos de línea, limitadas estrictamente a 250 caracteres para encajar sin errores en columnas `VARCHAR(255)`.

---

## 📁 Mapa de Carpetas
- `data/` -> Archivos generales (Productos, Órdenes).
- `data/ch_neworders/` -> Salida específica para Cargo Hub.
- `data/edi_xmls/` -> Salida específica para EDI.
- `data/po_csvs/` -> Salida específica para Purchase Orders.
- `data/pdfs/` -> Archivos PDF generados.

---

## 🔐 Configuración Avanzada (`config/credentials.yaml`)

Para usar la carga directa vía API, configura tus credenciales:
```yaml
profiles:
  test_server:
    token: "tu_token_aqui"
    company_id: "id_compañia"
```

---
> [!IMPORTANT]
> **OMNISYRAX** es una herramienta de generación de datos. Siempre verifica los archivos en la carpeta `./data` antes de importarlos a entornos de producción.

**Desarrollado con ❤️ para la eficiencia logística.**
