from shiny import ui, module, render
from plotnine import *
import pandas as pd
import numpy as np
from datetime import date

# Importación explícita segura
from plotnine import ggplot, aes, geom_col, geom_bar, geom_text, theme_minimal, labs, coord_flip, theme, element_text, element_blank, expand_limits, scale_fill_manual, geom_vline, annotate, geom_segment, scale_x_datetime, geom_point, scale_color_manual

@module.ui
def dashboard_ui():
    return ui.div(
        # --- 1. INYECCIÓN CSS (Compresión Vertical Extrema) ---
        ui.tags.style(
            """
            /* 1. Aplastar los KPIs (Value Boxes) */
            .compact-kpi {
                height: 110px !important; 
                min-height: 110px !important;
                max-height: 110px !important;
                overflow: hidden !important;
            }
            .compact-kpi .value-box-value {
                font-size: 1.5rem !important; /* Texto valor más pequeño */
                margin-top: 0px !important;
            }
            .compact-kpi .value-box-title {
                font-size: 0.85rem !important; /* Título pequeño */
                margin-bottom: 2px !important;
                opacity: 0.8;
            }
            .compact-kpi .value-box-area {
                padding: 10px !important; /* Menos relleno interno */
            }
            
            /* 2. Filas Apretadas (Tight Rows) */
            .tight-row {
                margin-bottom: 8px !important; /* Espacio mínimo entre filas */
            }
            
            /* 3. Ajustes de Cards para Analítica */
            .card {
                margin-bottom: 0px !important;
                box-shadow: none !important; /* Look más plano y limpio */
                border: 1px solid #e9ecef !important;
            }
            .card-header {
                padding: 4px 10px !important; /* Header muy delgado */
                font-size: 0.9rem !important;
                font-weight: bold;
            }
            .card-body {
                padding: 0px !important; /* Sin padding alrededor de gráficos */
            }

            /* 4. Gantt Card Específico */
            .gantt-card {
                margin-top: 0px !important;
                border: none !important;
            }
            """
        ),
        
        # --- FILA 1: KPIs (Compactos) ---
        ui.div(
            ui.layout_column_wrap(
                ui.value_box(
                    "Días Retraso Promedio",
                    ui.output_text("kpi_retraso"),
                    theme="warning",
                    class_="compact-kpi" # Clase forzada
                ),
                ui.value_box(
                    "Progreso General",
                    ui.output_text("kpi_progreso"),
                    theme="bg-gradient-blue-purple",
                    class_="compact-kpi"
                ),
                ui.value_box(
                    "Proyectos Visibles",
                    ui.output_text("kpi_total"),
                    theme="primary",
                    class_="compact-kpi"
                ),
                width=1/3, 
                fill=False
            ),
            class_="tight-row"
        ),
        
        # --- FILA 2: GRÁFICOS ANALÍTICOS ---
        ui.div(
            ui.layout_column_wrap(
                ui.card(
                    ui.card_header("Tiempo vs Avance"),
                    ui.output_plot("plot_time_vs_advance")
                ),
                ui.card(
                    ui.card_header("Días para Entrega"),
                    ui.output_plot("plot_delivery_radar")
                ),
                ui.card(
                    ui.card_header("Carga por Responsable"),
                    ui.output_plot("plot_responsables")
                ),
                width=1/3,
                fill=False
            ),
            class_="tight-row"
        ),

        # --- FILA 3: GANTT CHART (Base) ---
        ui.div(
            ui.card(
                ui.output_plot("plot_gantt"),
                full_screen=True,
                class_="gantt-card"
            ),
            class_="tight-row"
        )
    )

@module.server
def dashboard_server(input, output, session, df_reactive):
    
    # --- KPIs ---
    @render.text
    def kpi_retraso():
        df = df_reactive()
        if df.empty: return "0"
        return f"{df['Dias_retraso'].mean():.1f} d"

    @render.text
    def kpi_progreso():
        df = df_reactive()
        if df.empty: return "0%"
        return f"{df['Progreso'].mean():.1f}%"

    @render.text
    def kpi_total():
        df = df_reactive()
        return f"{len(df)}"

    # --- WIDGET 1: TIEMPO VS AVANCE ---
    @render.plot
    def plot_time_vs_advance():
        df = df_reactive()
        if df.empty: return _empty_message("-")

        plot_df = df.copy()
        today = pd.to_datetime(date.today())

        plot_df['Total_Days'] = (plot_df['Fin'] - plot_df['Inicio']).dt.days
        plot_df['Elapsed_Days'] = (today - plot_df['Inicio']).dt.days
        plot_df['Total_Days'] = plot_df['Total_Days'].replace(0, 1)
        plot_df['Pct_Time'] = (plot_df['Elapsed_Days'] / plot_df['Total_Days'] * 100).clip(0, 100)

        p = (
            ggplot(plot_df)
            + geom_col(aes(x='reorder(Proyecto, Pct_Time)', y='Pct_Time'), fill='#ecf0f1', width=0.8)
            + geom_col(aes(x='reorder(Proyecto, Pct_Time)', y='Progreso'), fill='#3498db', width=0.4)
            + coord_flip()
            + labs(x="", y="% Comparativo")
            + theme_minimal()
            + theme(
                panel_grid_major_y=element_blank(),
                axis_text_y=element_text(size=8),
                figure_size=(5, 2.5), # Altura reducida para ahorrar espacio
                plot_margin=0
            )
        )
        return p

    # --- WIDGET 2: DÍAS PARA ENTREGA ---
    @render.plot
    def plot_delivery_radar():
        df = df_reactive()
        if df.empty: return _empty_message("-")

        today = pd.to_datetime(date.today())
        plot_df = df[df['Progreso'] < 100].copy()
        
        if plot_df.empty: return _empty_message("Todo Entregado")

        plot_df['Dias_Restantes'] = (plot_df['Fin'] - today).dt.days
        
        conditions = [
            (plot_df['Dias_Restantes'] < 15),
            (plot_df['Dias_Restantes'] < 45)
        ]
        choices = ['Urgente', 'Atención']
        plot_df['Nivel'] = np.select(conditions, choices, default='Normal')

        colores = {'Urgente': '#e74c3c', 'Atención': '#f1c40f', 'Normal': '#2ecc71'}

        p = (
            ggplot(plot_df, aes(x='reorder(Proyecto, -Dias_Restantes)', y='Dias_Restantes', color='Nivel'))
            + geom_segment(aes(xend='Proyecto', yend=0), size=1.5)
            + geom_point(size=4)
            + coord_flip()
            + scale_color_manual(values=colores)
            + labs(x="", y="Días Restantes")
            + theme_minimal()
            + theme(
                legend_position="none",
                panel_grid_major_y=element_blank(),
                axis_text_y=element_text(size=8),
                figure_size=(5, 2.5),
                plot_margin=0
            )
        )
        return p

    # --- WIDGET 3: CARGA POR RESPONSABLE ---
    @render.plot
    def plot_responsables():
        df = df_reactive()
        if df.empty: return _empty_message("-")

        p = (
            ggplot(df, aes(x='Responsable'))
            + geom_bar(fill='#34495e', width=0.6)
            + labs(x="", y="Proyectos")
            + theme_minimal()
            + theme(
                panel_grid_major_x=element_blank(),
                axis_text_x=element_text(angle=45, ha='right', size=8),
                figure_size=(5, 2.5),
                plot_margin=0
            )
        )
        return p

    # --- GANTT CHART ---
    @render.plot
    def plot_gantt():
        df = df_reactive()
        if df.empty: return _empty_message("Sin datos")

        plot_df = df.copy()
        today = pd.to_datetime(date.today())
        today_str = today.strftime("%d-%b")

        orden = plot_df.sort_values('Inicio', ascending=False)['Proyecto'].unique()
        plot_df['Proyecto'] = pd.Categorical(plot_df['Proyecto'], categories=orden, ordered=True)
        max_y = len(orden)

        colores = {
            'finalizado': '#2ecc71', 'En Proceso': '#3498db', 
            'En dependencia': '#f1c40f', 'Riesgo': '#e74c3c'
        }
        
        p = (
            ggplot(plot_df, aes(x='Inicio', xend='Fin', y='Proyecto', yend='Proyecto', color='Status'))
            + geom_segment(size=8, alpha=0.9)
            
            # Marcador "T" Horizontal
            + geom_vline(xintercept=today, linetype="dashed", color="#7f8c8d", size=1)
            + annotate("text", x=today, y=max_y + 0.2, label=f"Hoy: {today_str}", 
                       color="#7f8c8d", size=9, angle=0, ha="center", va="bottom")
            + expand_limits(y=max_y + 0.5)
            
            + scale_color_manual(values=colores)
            + labs(x="", y="", color="", title="")
            + scale_x_datetime(date_labels="%d-%b")
            + theme_minimal()
            + theme(
                panel_grid_major_y=element_blank(),
                axis_text_y=element_text(size=9, color="#2c3e50", weight="bold"),
                axis_text_x=element_text(size=8),
                legend_position="bottom",
                figure_size=(12, 3), # Mantenemos altura baja
                plot_margin=0
            )
        )
        return p

def _empty_message(msg):
    return (ggplot() + annotate("text", x=0, y=0, label=msg, color="gray", size=10) + theme_void())
