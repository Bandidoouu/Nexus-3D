# Nexus 3D — Pro System

Sistema de gestión de inventario y cotizaciones para impresión 3D. Permite controlar materiales, calcular costos de piezas, generar cotizaciones para clientes y mantener un catálogo de productos con sus costos de producción.

---

## Características

| Módulo | Descripción |
|---|---|
| **Dashboard** | Resumen en tiempo real: materiales totales, stock bajo, cotizaciones activas |
| **Stock** | Vista por categoría con alertas de stock mínimo |
| **Catálogo Maestro** | CRUD de materiales con búsqueda y filtros por categoría |
| **Entradas / Salidas** | Registro de movimientos con validación de stock |
| **Cotización** | Calculadora de costos: filamento + electricidad + máquina × overhead × margen |
| **Mis Cotizaciones** | Gestión de estados: Borrador → Guardada → Completada / Cancelada |
| **Productos Stock** | Catálogo de diseños con costo de producción calculado |
| **Historial** | Auditoría completa de todos los movimientos, filtrable por tipo |
| **Exportar Excel** | Exporta catálogo, cotizaciones e historial a `.xlsx` |

---

## Requisitos

- Python **3.10 o superior**
- `tkinter` (incluido en la instalación estándar de Python en Windows y macOS)
- `openpyxl` (opcional, solo para exportar a Excel)

---

## Instalación y uso

### 1. Clonar el repositorio

```bash
git clone https://github.com/Bandidoouu/Nexus-3D.git
cd Nexus-3D
```

### 2. (Opcional) Crear un entorno virtual

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# macOS / Linux
source venv/bin/activate
```

### 3. Instalar dependencias opcionales

```bash
python -m pip install openpyxl
```

> Sin `openpyxl` la app funciona normalmente; los botones de exportar Excel mostrarán un aviso.

### 4. Ejecutar la aplicación

```bash
python main.py
```

La primera vez se crea automáticamente el archivo `inventario_materiales.db` en la misma carpeta. No hace falta configurar nada más.

---

## Estructura del proyecto

```
Nexus-3D/
├── main.py                          ← Punto de entrada
├── nexus3d/
│   ├── db/
│   │   └── database.py              ← DatabaseManager (SQLite)
│   ├── logic/
│   │   └── calculadora.py           ← Fórmulas de costo (filamento, electricidad, máquina)
│   └── ui/
│       ├── app.py                   ← Ventana principal, navegación, layout
│       ├── widgets.py               ← HoverButton, ScrollableFrame, logo, tarjetas
│       └── pages/                   ← Una clase por página
│           ├── dashboard.py
│           ├── stock.py
│           ├── materiales.py
│           ├── perfil.py
│           ├── entradas.py
│           ├── salidas.py
│           ├── productos_stock.py
│           ├── nuevo_producto_stock.py
│           ├── cotizacion.py
│           ├── cotizaciones_lista.py
│           └── historial.py
```

---

## Fórmula de costo

El calculador usa los siguientes parámetros (editables en `nexus3d/logic/calculadora.py`):

```
Costo pieza = ((costo_filamento + costo_luz + costo_máquina) × 1.3 × ganancia) + materiales_extra

costo_luz     = (350W / 1000) × horas × $1.05/kWh
costo_máquina = horas × $1.12/hora
overhead      = 1.3 (30% gastos fijos)
```

---

## Primer uso recomendado

1. Ir a **Nuevo Perfil** → crear una categoría `Filamento` y registrar tus filamentos con precio por kg
2. Registrar otros materiales (tornillos, insertos, etc.) con sus categorías
3. Usar **Entradas** para cargar el stock inicial
4. Abrir **Cotización** para calcular el costo de una pieza e ingresarla en un presupuesto
5. Ver el resumen en **Dashboard**

---

## Notas

- La base de datos `inventario_materiales.db` se genera localmente y **no se sube al repositorio** (ver `.gitignore`)
- Compatible con Windows, macOS y Linux siempre que Python tenga `tkinter` instalado
- En algunas distribuciones Linux hay que instalar tkinter manualmente: `sudo apt install python3-tk`
