# 🏛️ Presupuesto Abierto — Consultor

App Streamlit para consultar la API de crédito presupuestario de Argentina.

## Instalación

```bash
pip install -r requirements.txt
```

## Uso

```bash
streamlit run app.py
```

## Funcionalidades

- **Selección de columnas** por categorías (institucional, programática, económica, geográfica, crédito)
- **Filtros dinámicos** con todos los operadores del schema: `equal`, `like`, `between`, `greater_than`, etc.
- **Rango de años** desde 1995 hasta 2026
- **Preview** del payload JSON antes de ejecutar
- **Vista previa** de datos (1 año) antes de descargar todo
- **Descarga** en Excel o CSV

## API Key

Podés configurar tu API Key en la barra lateral. Por defecto usa la clave de ejemplo.

## Notas

- Se agrega un delay configurable entre requests para no saturar la API
- Los errores por año se muestran al final sin interrumpir la descarga de los demás años
