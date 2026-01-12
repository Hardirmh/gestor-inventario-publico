from shiny import ui, module, render, reactive
import pandas as pd
import io
from typing import Callable

@module.ui
def data_ui():
    return ui.row(
        # --- COLUMNA IZQUIERDA: Formularios ---
        ui.column(
            3,
            # CARD: Edición
            ui.card(
                ui.card_header("🛠️ Editar Proyecto"),
                ui.input_select("select_id", "Seleccionar ID", choices=[]),
                ui.hr(),
                ui.input_select("input_status", "Nuevo Estado", 
                                choices=["En dependencia", "En Proceso", "finalizado", "Riesgo"]),
                ui.input_slider("input_progreso", "Nuevo Progreso (%)", min=0, max=100, value=0, step=5),
                ui.input_action_button("btn_save", "Actualizar", class_="btn-primary w-100"),
                ui.br(),
                ui.download_button("btn_download", "Descargar Vista Actual", class_="btn-secondary w-100")
            ),
            
            # CARD: Nuevo Proyecto
            ui.card(
                ui.card_header("➕ Nuevo Proyecto"),
                ui.input_text("input_new_name", "Nombre del Proyecto", placeholder="Ej: Migración Cloud"),
                ui.input_date("input_new_start", "Fecha Inicio"),
                ui.input_date("input_new_end", "Fecha Fin"),
                ui.br(),
                ui.input_action_button("btn_add", "Agregar Proyecto", class_="btn-success w-100")
            )
        ),
        
        # --- COLUMNA DERECHA: Tabla con Filtros ---
        ui.column(
            9,
            ui.card(
                ui.card_header("🔎 Filtros y Gestión"),
                ui.layout_column_wrap(
                    ui.input_text("search", "🔍 Buscar (Proyecto/Resp)", placeholder="Escribe para filtrar..."),
                    ui.input_select("filter_status", "Filtro Estado", choices=["Todos", "En dependencia", "En Proceso", "finalizado", "Riesgo"]),
                    ui.input_action_button("btn_delete", "🗑️ Borrar Seleccionados", class_="btn-danger"),
                    width=1/3
                )
            ),
            ui.card(
                ui.output_data_frame("grid_proyectos")
            )
        )
    )

@module.server
def data_server(input, output, session, df_reactive, update_callback: Callable, add_callback: Callable, delete_callback: Callable):
    """
    Retorna: Un objeto reactivo (filtered_data) para que App lo pase al Dashboard.
    """

    # --- 1. LÓGICA DE FILTRADO (Reactive Calc) ---
    @reactive.Calc
    def filtered_data():
        df = df_reactive()
        if df.empty: return df

        # Filtro de Texto (Búsqueda)
        term = input.search()
        if term:
            # Buscamos en Proyecto y Responsable
            mask = (
                df['Proyecto'].str.contains(term, case=False, na=False) | 
                df['Responsable'].str.contains(term, case=False, na=False)
            )
            df = df[mask]

        # Filtro de Estado
        status = input.filter_status()
        if status != "Todos":
            df = df[df['Status'] == status]
            
        return df

    # --- 2. SELECTOR DE ID (Sincronizado con data filtrada) ---
    @reactive.Effect
    def _():
        df = filtered_data()
        opciones = {}
        if not df.empty:
            opciones = {str(row['ID']): f"{row['ID']} - {row['Proyecto']}" for _, row in df.iterrows()}
        ui.update_select("select_id", choices=opciones)

    # --- 3. TABLA (Muestra data filtrada) ---
    @render.data_frame
    def grid_proyectos():
        return render.DataGrid(
            filtered_data(), 
            filters=False, # Ya tenemos filtros externos
            selection_mode="rows" # Permite seleccionar múltiples
        )

    # --- 4. ACCIONES (CRUD) ---
    
    # Update
    @reactive.Effect
    @reactive.event(input.btn_save)
    def _():
        update_callback(input.select_id(), input.input_status(), input.input_progreso())
        ui.notification_show("Registro actualizado.", type="message")

    # Create
    @reactive.Effect
    @reactive.event(input.btn_add)
    def _():
        name = input.input_new_name()
        start = input.input_new_start()
        end = input.input_new_end()

        if not name or not start or not end:
            ui.notification_show("Error: Faltan datos obligatorios.", type="error")
            return

        new_project = {
            "Proyecto": name,
            "Inicio": str(start),
            "Fin": str(end),
            "Status": "En Proceso",
            "Progreso": 0,
            "Descripcion": "Nuevo proyecto",
            "Dependencias": "N/A", "Acciones tomadas": "N/A", "Notas": "N/A", "Asignado": "Sin asignar", "Responsable": "TBD", "Dias_retraso": 0
        }
        add_callback(new_project)
        ui.notification_show(f"Proyecto '{name}' agregado.", type="message")

    # Delete (NUEVO)
    @reactive.Effect
    @reactive.event(input.btn_delete)
    def _():
        # Obtener índices seleccionados de la vista actual
        selected_indices = input.grid_proyectos_selected_rows()
        
        if not selected_indices:
            ui.notification_show("Selecciona filas en la tabla para borrar.", type="warning")
            return

        # Mapear índices visuales a IDs reales usando el DataFrame filtrado
        current_df = filtered_data()
        
        # Extraemos los IDs de las filas seleccionadas
        # iloc usa indices posicionales (0, 1, 2...) que coinciden con la selección visual
        ids_to_delete = current_df.iloc[list(selected_indices)]['ID'].tolist()
        
        # Llamamos al callback
        delete_callback(ids_to_delete)
        ui.notification_show(f"Se eliminaron {len(ids_to_delete)} proyectos.", type="message")

    # Descarga (Respeta el filtro actual)
    @render.download(filename="Vista_Filtrada.xlsx")
    def btn_download():
        df = filtered_data()
        buffer = io.BytesIO()
        with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
            df.to_excel(writer, index=False)
        yield buffer.getvalue()

    # --- RETORNO CRÍTICO ---
    # Devolvemos el cálculo reactivo para que App lo use
    return filtered_data
