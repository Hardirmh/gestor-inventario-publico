import os
import zipfile

NOMBRE_ZIP = "mi_proyecto_limpio.zip"
IGNORE_DIRS = {'venv', '.git', '__pycache__', '.idea', '.vscode'}
IGNORE_EXTS = {'.pyc', '.DS_Store'}
EXCLUDE_FILES = {'preparar_proyecto.py', 'database.db', 'mi_base_de_datos.db'} 

def limpiar_y_empaquetar():
    print(f"Creando {NOMBRE_ZIP} limpio...")
    with zipfile.ZipFile(NOMBRE_ZIP, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk('.'):
            dirs[:] = [d for d in dirs if d not in IGNORE_DIRS]
            for file in files:
                if file in EXCLUDE_FILES or any(file.endswith(ext) for ext in IGNORE_EXTS) or file == NOMBRE_ZIP:
                    continue
                file_path = os.path.join(root, file)
                zipf.write(file_path, arcname=file_path)
    print("Listo.")

if __name__ == "__main__":
    limpiar_y_empaquetar()
