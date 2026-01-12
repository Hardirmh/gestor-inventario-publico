from shiny import App, ui, reactive, render
from pathlib import Path
from logic.data_manager import DataManager
from modules import mod_dashboard, mod_data

# 1. Instanciamos la Lógica
dm = DataManager()

# --- DEFINICIÓN DE TEMAS ---
THEME_CONFIG = [
    {"name": "Flatly (Claro)", "type": "bootswatch", "value": "flatly"},
    {"name": "Midnight (Imagen)", "type": "custom", "value": "midnight"}, 
    {"name": "Vapor (Neon)", "type": "bootswatch", "value": "vapor"},
    {"name": "Darkly (Oscuro)", "type": "bootswatch", "value": "darkly"},
    {"name": "Zephyr (Moderno)", "type": "bootswatch", "value": "zephyr"},
    {"name": "Solar (Azul)", "type": "bootswatch", "value": "solar"},
]

# --- CSS PERSONALIZADO (MIDNIGHT) ---
MIDNIGHT_CSS = """
    body { background-color: #131525 !important; color: #e0e6ed !important; font-family: 'Segoe UI', sans-serif; }
    .navbar { background-color: #131525 !important; border-bottom: 1px solid #2b2d42 !important; }
    .navbar-brand, .nav-link { color: #ffffff !important; }
    .card { background-color: #1E2235 !important; border: none !important; border-radius: 20px !important; box-shadow: 0 4px 15px rgba(0,0,0,0.3) !important; }
    .card-header { background-color: transparent !important; border-bottom: 1px solid #2b2d42 !important; color: #8c90b0 !important; font-weight: 600; text-transform: uppercase; font-size: 0.8rem; letter-spacing: 1px; }
    .compact-kpi { background: linear-gradient(145deg, #23273a, #1E2235) !important; border-left: 4px solid #4d79ff !important; }
    .value-box-value { color: #ffffff !important; }
    .value-box-title { color: #8c90b0 !important; }
    .btn-primary { background-color: #4d79ff !important; border: none; }
    .btn-success { background-color: #00d2d3 !important; border: none; color: #000; }
    .btn-danger  { background-color: #ff6b6b !important; border: none; }
    text { fill: #e0e6ed !important; } 
    .nav-tabs .nav-link.active { background-color: #1E2235 !important; border-color: #2b2d42 !important; color: #4d79ff !important; }
"""

# --- SCRIPT JAVASCRIPT BLINDADO ---
theme_js = f"""
$(document).on('shiny:connected', function() {{
    Shiny.addCustomMessageHandler('switch_theme', function(message) {{
        var link = document.getElementById('theme-link');
        var customStyle = document.getElementById('custom-theme-style');
        if (customStyle) customStyle.remove();
        
        if (message.type === 'bootswatch') {{
            link.href = 'https://cdn.jsdelivr.net/npm/bootswatch@5.3.2/dist/' + message.value + '/bootstrap.min.css';
        }} else if (message.type === 'custom') {{
            link.href = 'https://cdn.jsdelivr.net/npm/bootswatch@5.3.2/dist/darkly/bootstrap.min.css';
            var style = document.createElement('style');
            style.id = 'custom-theme-style';
            style.innerHTML = `{MIDNIGHT_CSS}`;
            document.head.appendChild(style);
        }}
    }});
}});
"""

# 2. UI Global
app_ui = ui.page_navbar(
    ui.nav_panel("Tablero Ejecutivo", mod_dashboard.dashboard_ui("dash1")),
    ui.nav_panel("Gestión de Datos", mod_data.data_ui("data1")),
    
    ui.nav_control(
        ui.div(
            ui.output_text("txt_current_theme", inline=True), 
            ui.input_action_button("btn_theme", "🎨 Tema", class_="btn-secondary btn-sm ms-2"),
            class_="d-flex align-items-center my-2"
        )
    ),
    
    title="PMO Dashboard",
    id="main_navbar",
    header=ui.TagList(
        ui.tags.script(theme_js),
        ui.tags.link(id="theme-link", rel="stylesheet", href="https://cdn.jsdelivr.net/npm/bootswatch@5.3.2/dist/flatly/bootstrap.min.css"),
        ui.include_css(Path(__file__).parent / "styles.css")
    )
)

# 3. Server
def server(input, output, session):
    val_df_global = reactive.Value(dm.df)
    current_theme_idx = reactive.Value(0)

    # Callback Tema
    @reactive.Effect
    @reactive.event(input.btn_theme)
    async def _():
        new_idx = (current_theme_idx() + 1) % len(THEME_CONFIG)
        current_theme_idx.set(new_idx)
        await session.send_custom_message("switch_theme", THEME_CONFIG[new_idx])
    
    @render.text
    def txt_current_theme():
        return f"{THEME_CONFIG[current_theme_idx()]['name']}"

    # --- CALLBACKS DE DATOS ACTUALIZADOS ---
    
    # NUEVA FIRMA: Recibe ID y Diccionario completo
    def update_callback(p_id, data_dict):
        new_df = dm.update_project(p_id, data_dict)
        val_df_global.set(new_df)

    def add_data_callback(new_project_dict):
        new_df = dm.add_project(new_project_dict)
        val_df_global.set(new_df)
        
    def delete_data_callback(ids_list):
        new_df = dm.delete_projects(ids_list)
        val_df_global.set(new_df)

    # Conexión Módulos
    filtered_view = mod_data.data_server("data1", val_df_global, update_callback, add_data_callback, delete_data_callback)
    mod_dashboard.dashboard_server("dash1", filtered_view)

app = App(app_ui, server)
