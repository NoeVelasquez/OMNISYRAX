# 🌌 OMNISYRAX: Plataforma Maestra de Generación de Datos Logísticos

**OMNISYRAX** es una solución de grado industrial diseñada para automatizar la creación de ecosistemas de datos masivos, precisos y multilingües. Ideal para pruebas de estrés, demostraciones de software y validación de flujos logísticos complejos.

---

## 🌟 ¿Por qué OMNISYRAX?

En el mundo de la logística, los datos de prueba suelen ser aburridos y repetitivos. OMNISYRAX rompe esa barrera ofreciendo:
- **Multilenguaje Real**: Generación en 15+ idiomas (Chino, Árabe, Ruso, etc.) con coherencia cultural.
- **Unicidad Garantizada**: Algoritmos basados en timestamps que eliminan el error de "ID duplicado".
- **Estructuras Especializadas**: Soporte nativo para Commerce Hub, EDI, Shipedge y Shopify.
- **Flujos Sincronizados**: Crea un producto y úsalo automáticamente en órdenes y compras.

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

#### B. La Forja (Modo Comandos Directos)
Usa comandos para generar datos específicos de forma inmediata:
```bash
python3 omnisyrax.py [COMANDO] --count [CANTIDAD]
```

---

## 🛠️ Comandos y Generadores en Detalle

### 📦 Catálogo de Productos
| Comando | Formato | Uso Principal |
| :--- | :--- | :--- |
| `products` | CSV | Productos estándar con 26 columnas (peso, volumen, HS Codes). |
| `shipedge` | CSV | Importación técnica para Shipedge (DC1, Serial Numbers). |
| `shopify` | CSV | Archivo listo para importar en el administrador de Shopify. |

**Ejemplo:** `python3 omnisyrax.py shipedge --count 100`

### 🛍️ Flujo de Órdenes y Compras
| Comando | Formato | Uso Principal |
| :--- | :--- | :--- |
| `orders` | CSV/API | Órdenes de venta con clientes y direcciones reales. |
| `po` | CSV | Órdenes de compra vinculadas a proveedores específicos. |
| `transfers` | CSV | Movimientos de stock entre almacenes (A -> B). |

**Ejemplo:** `python3 omnisyrax.py po --count 10`

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
| `inventory` | CSV | Ajustes de stock masivos. |

---

## 🌍 El Motor Multilingüe (Data Pool)

OMNISYRAX no solo traduce, sino que entiende categorías. Soporta:
- **Idiomas**: Inglés, Español, Árabe, Japonés, Coreano, Chino, Ruso, Hindi, Hebreo, Tailandés, Vietnamita, Griego, Amhárico, Georgiano y Armenio.
- **Categorías**: Electrónica, Ropa, Comida (Food), Libros, Hogar, Deportes, Juguetes, Salud, Belleza y Automotriz.

---

## 🛡️ Sistema de Unicidad (Anti-Duplicidad)

Para garantizar que tus datos siempre sean aceptados por sistemas externos, OMNISYRAX genera IDs únicos:
- **Patrón**: `[PREFIJO]-[YYMMDDHHMMSS]-[RANDOM]`
- **Resultado**: Números de PO y Órdenes que nunca se repiten, sin importar cuántas veces ejecutes el programa.

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
