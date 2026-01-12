#!/bin/bash
# start.sh
# Inicializa el entorno y lanza la aplicación Shiny

echo "🚀 Iniciando PMO Dashboard..."

# 1. Verificar si existe el entorno virtual, si no, crearlo
if [ ! -d "env" ]; then
    echo "⚠️  No se detectó entorno virtual. Creando 'env'..."
    python3 -m venv env
fi

# 2. Activar entorno
source env/bin/activate

# 3. Verificar e instalar requerimientos
if [ -f "requirements.txt" ]; then
    echo "📦 Verificando dependencias..."
    pip install -q -r requirements.txt
fi

# 4. Lanzar la aplicación
echo "🟢 Servidor activo en: http://127.0.0.1:8000"
echo "💡 (Presiona CTRL+C para detener)"
echo "---------------------------------------------------"
shiny run app.py --reload
