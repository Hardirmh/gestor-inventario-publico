import pandas as pd
import numpy as np
from datetime import datetime
import os

DB_FILE = "proyectos.csv"

class DataManager:
    def __init__(self):
        if os.path.exists(DB_FILE):
            self.df = pd.read_csv(DB_FILE)
            # Conversión robusta de fechas
            self.df['Inicio'] = pd.to_datetime(self.df['Inicio'], dayfirst=True, format='mixed', errors='coerce')
            self.df['Fin'] = pd.to_datetime(self.df['Fin'], dayfirst=True, format='mixed', errors='coerce')
            
            if 'Progreso' in self.df.columns:
                self.df['Progreso'] = self.df['Progreso'].fillna(0).astype(int)
            
            # Asegurar strings para evitar NaN en UI
            cols_str = ['Status', 'Proyecto', 'Acciones tomadas', 'Notas', 'Asignado', 'Responsable', 'Descripcion', 'Dependencias']
            for col in cols_str:
                if col not in self.df.columns: self.df[col] = "" # Crear si no existe
                self.df[col] = self.df[col].fillna("").astype(str)
        else:
            self.df = self._load_initial_data()
            self._save_to_csv()

    def _save_to_csv(self):
        self.df.to_csv(DB_FILE, index=False)

    def _load_initial_data(self) -> pd.DataFrame:
        # (Tu raw_data original aquí, omitido por brevedad pero MANTENLO en tu archivo)
        # ... se asume que carga el DataFrame inicial ...
        # Para el ejemplo, retornaré un DF vacío con estructura si no hay datos, 
        # pero tú mantén tu carga original.
        cols = ["ID", "Proyecto", "Descripcion", "Acciones tomadas", "Dependencias", 
                "Status", "Notas", "Asignado", "Responsable", "Progreso", "Inicio", "Fin", "Dias_retraso"]
        return pd.DataFrame(columns=cols)

    def update_project(self, project_id, data_dict: dict) -> pd.DataFrame:
        """
        Actualiza un proyecto existente con un diccionario completo de datos.
        """
        mask = self.df['ID'].astype(str) == str(project_id)
        
        if not mask.any():
            return self.df # No encontrado

        # 1. Actualizar columnas recibidas
        for key, val in data_dict.items():
            if key in self.df.columns and key != 'ID':
                # Manejo especial de Fechas
                if key in ['Inicio', 'Fin']:
                    self.df.loc[mask, key] = pd.to_datetime(val)
                else:
                    self.df.loc[mask, key] = val
        
        # 2. Recalcular Dias_retraso para esta fila
        # Formula: (Hoy - Fin) si no ha terminado.
        # Ojo: Pandas maneja esto vectorizado, pero para una fila usamos .loc
        fin_date = self.df.loc[mask, 'Fin'].iloc[0]
        today = pd.to_datetime("today")
        
        # Calculamos retraso: Días que han pasado desde la fecha fin (positivo = retraso)
        retraso = (today - fin_date).days
        self.df.loc[mask, 'Dias_retraso'] = int(retraso)

        self._save_to_csv()
        return self.df.copy()

    def add_project(self, new_data_dict: dict) -> pd.DataFrame:
        new_id = self.df['ID'].max() + 1 if not self.df.empty else 1
        new_data_dict['ID'] = new_id

        # Convertir fechas
        if 'Inicio' in new_data_dict: new_data_dict['Inicio'] = pd.to_datetime(new_data_dict['Inicio'])
        if 'Fin' in new_data_dict: new_data_dict['Fin'] = pd.to_datetime(new_data_dict['Fin'])
        
        # Calcular retraso inicial
        fin_date = new_data_dict.get('Fin', pd.to_datetime("today"))
        new_data_dict['Dias_retraso'] = (pd.to_datetime("today") - fin_date).days

        new_row = pd.DataFrame([new_data_dict])
        self.df = pd.concat([self.df, new_row], ignore_index=True)
        self._save_to_csv()
        return self.df.copy()

    def delete_projects(self, ids_to_delete: list) -> pd.DataFrame:
        if not ids_to_delete: return self.df
        ids_str = [str(x) for x in ids_to_delete]
        self.df = self.df[~self.df['ID'].astype(str).isin(ids_str)].copy()
        self._save_to_csv()
        return self.df.copy()
