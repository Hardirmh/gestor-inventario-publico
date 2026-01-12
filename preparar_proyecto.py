import os
import zipfile
import shutil

# Configuración
NOMBRE_ZIP = "mi_proyecto_limpio.zip"
# Archivos/Carpetas a IGNORAR
IGNORE_DIRS = {'venv', '.git', '__pycache__', '.idea', '.vscode'}
IGNORE_EXTS = {'.pyc', '.DS_Store'}
# Archivos específicos a excluir (como la base de datos con datos reales)
EXCLUDE_FILES = {'preparar_proyecto.py', 'mi_base_de_datos.db', 'database.db'} 

def limpiar_y_empaquetar():
    print("🧹 Iniciando limpieza y empaquetado...")
    
    # Crear el archivo ZIP
    with zipfile.ZipFile(NOMBRE_ZIP, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk('.'):
            # Filtrar directorios basura en el recorrido
            dirs[:] = [d for d in dirs if d not in IGNORE_DIRS]
            
            for file in files:
                if file in EXCLUDE_FILES or any(file.endswith(ext) for ext in IGNORE_EXTS) or file == NOMBRE_ZIP:
                    continue
                
                # Ruta relativa para el zip
                file_path = os.path.join(root, file)
                zipf.write(file_path, arcname=file_path)
                print(f"  ✅ Agregado: {file}")

    print("-" * 30)
    print(f"📦 ¡Listo! Archivo generado: {NOMBRE_ZIP}")
    print("Nota: La base de datos actual NO se incluyó (se creará una nueva vacía al ejecutar el programa).")

if __name__ == "__main__":
    limpiar_y_empaquetar()
