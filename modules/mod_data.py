from shiny import ui, module, render, reactive
import pandas as pd
import io
from datetime import date
from typing import Callable

@module.ui
def data_ui():
    return ui.row(
        ui.column(
            12,
            ui.card(
                ui.card_header("🗂️ Gestión de Base de Datos"),
                
                # Barra de Herramientas
                ui.layout_column_wrap(
                    ui.input_text("search", "🔍 Buscar", placeholder="Proyecto o Responsable..."),
                    ui.input_select("filter_status", "Filtro Estado", 
                                    choices=["Todos", "En Proceso", "En dependencia", "Riesgo", "finalizado"]),
                    
                    ui.div(
                        ui.input_action_button("btn_add_modal", "➕ Nuevo", class_="btn-primary"),
                        ui.input_action_button("btn_edit_modal", "✏️ Editar", class_="btn-warning"),
                        ui.input_action_button("btn_delete", "🗑️ Borrar", class_="btn-danger"),
                        class_="d-flex gap-2 align-items-end h-100 pb-3"
                    ),
                    width=1/3,
                    fill=False
                ),
                ui.hr(),
                
                # Tabla
                ui.output_data_frame("grid_proyectos"),
                
                ui.div(
                    ui.download_button("btn_download", "Descargar Excel", class_="btn-secondary btn-sm"),
                    class_="mt-3 text-end"
                )
            )
        )
    )

@module.server
def data_server(input, output, session, df_reactive, update_callback: Callable, add_callback: Callable, delete_callback: Callable):
    
    current_edit_id = reactive.Value(None)

    # --- 1. FILTRADO ---
    @reactive.Calc
    def filtered_data():
        df = df_reactive()
        if df.empty: return df

        term = input.search()
        if term:
            mask = (
                df['Proyecto'].str.contains(term, case=False, na=False) | 
                df['Responsable'].str.contains(term, case=False, na=False)
            )
            df = df[mask]

        status = input.filter_status()
        if status != "Todos":
            df = df[df['Status'] == status]
            
        return df

    # --- 2. TABLA ---
    @render.data_frame
    def grid_proyectos():
        return render.DataGrid(filtered_data(), filters=False, selection_mode="row")

    # --- 3. MODAL (EDICIÓN COMPLETA) ---
    def show_project_modal(is_edit=False, data=None):
        # Valores por defecto (Nuevo)
        vals = {
            "Proyecto": "", "Responsable": "", 
            "Inicio": date.today(), "Fin": date.today(), 
            "Status": "En Proceso", "Progreso": 0,
            "Descripcion": "", "Acciones tomadas": "", 
            "Dependencias": "", "Notas": ""
        }
        
        title = "➕ Nuevo Proyecto"
        btn_label = "Crear Proyecto"

        # Precarga (Editar)
        if is_edit and data is not None:
            title = "✏️ Editar Proyecto Completo"
            btn_label = "Guardar Cambios"
            vals["Proyecto"] = str(data['Proyecto'])
            vals["Responsable"] = str(data['Responsable'])
            vals["Inicio"] = pd.to_datetime(data['Inicio']).date()
            vals["Fin"] = pd.to_datetime(data['Fin']).date()
            vals["Status"] = str(data['Status'])
            vals["Progreso"] = int(data['Progreso'])
            # Campos de texto largo (manejo seguro de nulos)
            vals["Descripcion"] = str(data['Descripcion']) if pd.notna(data['Descripcion']) else ""
            vals["Acciones tomadas"] = str(data['Acciones tomadas']) if pd.notna(data['Acciones tomadas']) else ""
            vals["Dependencias"] = str(data['Dependencias']) if pd.notna(data['Dependencias']) else ""
            vals["Notas"] = str(data['Notas']) if pd.notna(data['Notas']) else ""

        m = ui.modal(
            # Fila 1: Datos Core
            ui.row(
                ui.column(6, ui.input_text("m_proyecto", "Proyecto", value=vals["Proyecto"])),
                ui.column(6, ui.input_text("m_responsable", "Responsable", value=vals["Responsable"])),
            ),
            # Fila 2: Fechas y Estado
            ui.row(
                ui.column(3, ui.input_date("m_inicio", "Inicio", value=vals["Inicio"])),
                ui.column(3, ui.input_date("m_fin", "Fin", value=vals["Fin"])),
                ui.column(3, ui.input_select("m_status", "Status", choices=["En Proceso", "En dependencia", "Riesgo", "finalizado"], selected=vals["Status"])),
                ui.column(3, ui.input_slider("m_progreso", "Avance %", 0, 100, vals["Progreso"])),
            ),
            ui.hr(),
            # Fila 3: Textos Largos (Areas)
            ui.layout_column_wrap(
                ui.input_text_area("m_descripcion", "Descripción", value=vals["Descripcion"], rows=3),
                ui.input_text_area("m_acciones", "Acciones Tomadas", value=vals["Acciones tomadas"], rows=3),
                width=1/2
            ),
            ui.layout_column_wrap(
                ui.input_text_area("m_dependencias", "Dependencias", value=vals["Dependencias"], rows=2),
                ui.input_text_area("m_notas", "Notas Adicionales", value=vals["Notas"], rows=2),
                width=1/2
            ),
            title=title,
            footer=ui.div(ui.modal_button("Cancelar"), ui.input_action_button("btn_save_modal", btn_label, class_="btn-primary")),
            easy_close=False, size="xl" # Modal Extra Grande
        )
        ui.modal_show(m)

    # --- EVENTOS ---
    @reactive.Effect
    @reactive.event(input.btn_add_modal)
    def _():
        current_edit_id.set(None)
        show_project_modal(is_edit=False)

    @reactive.Effect
    @reactive.event(input.btn_edit_modal)
    def _():
        sel = input.grid_proyectos_selected_rows()
        if not sel:
            ui.notification_show("Selecciona una fila para editar", type="warning")
            return
        
        idx = list(sel)[0]
        row_data = filtered_data().iloc[idx]
        current_edit_id.set(row_data['ID'])
        show_project_modal(is_edit=True, data=row_data)

    @reactive.Effect
    @reactive.event(input.btn_save_modal)
    def _():
        # Recolectar TODO el formulario
        new_data = {
            "Proyecto": input.m_proyecto(),
            "Responsable": input.m_responsable(),
            "Inicio": str(input.m_inicio()),
            "Fin": str(input.m_fin()),
            "Status": input.m_status(),
            "Progreso": input.m_progreso(),
            "Descripcion": input.m_descripcion(),
            "Acciones tomadas": input.m_acciones(),
            "Dependencias": input.m_dependencias(),
            "Notas": input.m_notas(),
            "Asignado": input.m_responsable() # Sincronizar Asignado/Responsable
        }

        if not new_data["Proyecto"]:
            ui.notification_show("Nombre requerido", type="error")
            return

        edit_id = current_edit_id()

        if edit_id is None:
            # NUEVO
            add_callback(new_data)
            ui.notification_show("Proyecto Creado", type="message")
        else:
            # EDITAR (Pasamos el dict completo)
            new_data['ID'] = edit_id
            update_callback(edit_id, new_data) 
            ui.notification_show("Proyecto Actualizado Completamente", type="message")

        ui.modal_remove()

    @reactive.Effect
    @reactive.event(input.btn_delete)
    def _():
        sel = input.grid_proyectos_selected_rows()
        if not sel: return
        ids = filtered_data().iloc[list(sel)]['ID'].tolist()
        delete_callback(ids)
        ui.notification_show(f"Eliminados: {len(ids)}", type="message")

    @render.download(filename="Data.xlsx")
    def btn_download():
        buffer = io.BytesIO()
        with pd.ExcelWriter(buffer) as writer: filtered_data().to_excel(writer, index=False)
        yield buffer.getvalue()

    return filtered_data
