# 🚀 GUÍA DEFINITIVA DE INSTALACIÓN Y CONFIGURACIÓN

Este manual detalla paso a paso cómo poner en marcha el proyecto desde cero para cualquier usuario o IA.

## 📥 1. DESCARGA DEL CÓDIGO
- **Desde la Web:** Ve a [este enlace](https://github.com/Hardirmh/gestor-inventario-publico) y pulsa el botón verde **Code** -> **Download ZIP**.
- **Enlace Directo:** [DESCARGAR ZIP AQUÍ](https://github.com/Hardirmh/gestor-inventario-publico/archive/refs/heads/main.zip)
- **Vía Terminal:** `git clone https://github.com/Hardirmh/gestor-inventario-publico.git`

## 📂 2. DESEMPAQUETADO
1. Busca el archivo `main.zip` en tu carpeta de Descargas.
2. Haz clic derecho y elige **Extraer en gestor-inventario-publico**.
3. Entra en la carpeta y haz clic derecho en un espacio blanco -> **Abrir Terminal aquí**.

## 🛠️ 3. INSTALACIÓN DE SCRIPTS (PASO A PASO)
Para que el programa funcione, debes instalar las librerías necesarias ejecutando estos comandos:

### A. Crear el Entorno Virtual (Aislamiento)
- **Windows:** `python -m venv venv`
- **Linux/Mac:** `python3 -m venv venv`

### B. Activar el Entorno (Crucial)
- **Windows:** `.\venv\Scripts\activate`
- **Linux/Mac:** `source venv/bin/activate`

### C. Instalar Dependencias
Una vez activado (verás un `(venv)` al inicio de tu línea de comandos), ejecuta:
```bash
pip install -r requirements.txt
```

## 🚀 4. INICIALIZACIÓN Y PRIMER USO
Para ejecutar el sistema principal:
```bash
python main.py
```
*Nota: El sistema detectará automáticamente si falta la base de datos y creará una nueva (`database.db`) totalmente limpia y lista para usar.*

## ☁️ 5. CÓMO ACTUALIZAR EN GITHUB
Si haces mejoras y quieres subirlas a la nube:
1. `git add .` (Prepara los archivos)
2. `git commit -m 'Mejoras en el código'` (Guarda la versión)
3. `git push origin main` (Sube a la nube)

## 🤖 6. RE-EMPAQUETADO PARA IA (CONTEXTO LIMPIO)
Si deseas que otra IA entienda tu proyecto sin enviarle archivos basura:
1. Ejecuta: `python preparar_proyecto.py`
2. Sube el archivo resultante `mi_proyecto_limpio.zip` al chat de la IA.
