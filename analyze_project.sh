#!/bin/bash
# analyze_project.sh
# Escanea el proyecto y genera un prompt de contexto para la IA

OUTPUT_FILE="contexto_proyecto.txt"

echo "Generando análisis del proyecto..." > "$OUTPUT_FILE"
echo "--- ESTRUCTURA DE ARCHIVOS ---" >> "$OUTPUT_FILE"
tree -I 'env|__pycache__|.git|.pytest_cache' >> "$OUTPUT_FILE"

echo -e "\n\n--- CONTENIDO DE LOS ARCHIVOS ---" >> "$OUTPUT_FILE"

# Busca archivos Python, CSS y Requirements (ignora entorno virtual)
find . -type f \( -name "*.py" -o -name "*.css" -o -name "requirements.txt" \) -not -path "./env/*" | while read file; do
    echo -e "\n=========================================" >> "$OUTPUT_FILE"
    echo "ARCHIVO: $file" >> "$OUTPUT_FILE"
    echo "=========================================" >> "$OUTPUT_FILE"
    cat "$file" >> "$OUTPUT_FILE"
done

echo -e "\n\n--- FIN DEL ANÁLISIS ---" >> "$OUTPUT_FILE"

echo "✅ Análisis completado. El archivo '$OUTPUT_FILE' ha sido creado."
echo "📋 Copia el contenido de ese archivo y pégalo en el chat con Gemini."
