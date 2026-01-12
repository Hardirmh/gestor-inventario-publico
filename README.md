# 🚀 GUÍA RÁPIDA DE INICIO

Siga estos pasos para descargar, ejecutar y actualizar el proyecto con Gemini.

## 1. 📥 DESCARGA Y DESEMPAQUETADO
- **Enlace de descarga:** [DESCARGAR AQUÍ (.ZIP)](https://github.com/Hardirmh/gestor-inventario-publico/archive/refs/heads/main.zip)
- **Instrucción:** Una vez descargado, descomprima el archivo y abra una terminal dentro de la carpeta resultante.

## 2. ⚡ EJECUCIÓN (INICIALIZACIÓN)
Para arrancar la aplicación, simplemente ejecute en su terminal:
```bash
bash start.sh
```
*Este comando configurará el entorno e iniciará el sistema automáticamente.*

## 3. 🤖 ACTUALIZAR O CONSULTAR CON GEMINI (IA)
Si desea que Gemini analice el código actual o lo actualice sin enviar archivos basura:

1. **Limpiar el proyecto:** En la misma carpeta, ejecute:
   ```bash
   python3 preparar_proyecto.py
   ```
2. **Subir a la IA:** Tome el archivo generado `mi_proyecto_limpio.zip` y súbalo al chat de Gemini.

## 4. ☁️ SUBIR CAMBIOS A GITHUB
Para guardar sus avances en la nube:
```bash
git add . && git commit -m 'Actualización de código' && git push origin main
```
