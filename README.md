# 🏛️ Presupuesto Abierto — Presupuesto Express

App desarrollada en Streamlit para consultar la API de crédito presupuestario de Argentina, con descarga de datos y ajuste automático por inflación.

---

## ⚙️ Instalación

pip install -r requirements.txt

---

## ▶️ Uso

streamlit run app.py

---

## 🚀 Funcionalidades

- Selección de columnas por categorías:
  - institucional
  - programática
  - económica
  - geográfica
  - crédito
- Filtros dinámicos con operadores del schema:
  - equal, like, between, greater_than, etc.
- Rango de años desde 1995 hasta 2026
- Preview del payload JSON antes de ejecutar
- Vista previa de datos (1 año) antes de descargar todo
- Descarga en Excel o CSV

### 📊 Ajuste por inflación

- Integración con Google Sheets para coeficientes de inflación
- Dos modalidades automáticas:

**Ajuste anual**
- Se aplica cuando no se incluye impacto_presupuestario_mes
- Genera columnas ajustadas para todas las variables de crédito

**Ajuste mensual**
- Se activa cuando se incluye impacto_presupuestario_mes
- Construye una fecha (año + mes + día 1)
- Ajusta la columna credito_devengado usando IPC mensual

---

## 🔐 Seguridad

- La API key no se expone en el código
- Uso de st.secrets para:
  - PRESUPUESTO_API_KEY
  - APP_ACCESS_CODE
- Acceso protegido mediante código al ingresar a la app

---

## ☁️ Deploy

La app puede desplegarse en Streamlit Cloud:

https://streamlit.io/cloud

Requiere:
- Repositorio en GitHub
- Configuración de secrets

---

## 🔑 API Key

La app utiliza la API de Presupuesto Abierto.

La clave debe configurarse como variable secreta en el entorno de ejecución.

---

## 📝 Notas

- Se incluye delay configurable entre requests para evitar saturar la API
- Los errores por año no interrumpen la descarga total
- Compatible con consultas de gran volumen de datos

---

## 👤 Autor

Natán Spollansky  
Asociación Civil por la Igualdad y la Justicia (ACIJ)
