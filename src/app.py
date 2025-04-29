import sqlite3
import dash
from dash import dcc, html, Output, Input
import dash_bootstrap_components as dbc

from .dashboard import iceland_through_time, state_of_the_economy, utils
from .constants import SOURCE


description_of_dashboard = """
This dashboard pulls real data from the statice.is API every minute... Although the data is mostly static, so it doesn't appear to be "real-time" - it actually is. 
The graphs update every 10 seconds as they read from a local database.

This dashboard aims to show economic data about iceland, both past and present. 
"""
# Initialize app
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
app.title = "Iceland Economic Dashboard"
server = app.server

# Layout
app.layout = dbc.Container([
    dcc.Interval(
        id='interval-component',
        interval=10*1000,  # 5 seconds
        n_intervals=0,
        disabled=False
    ),
    dcc.Interval(
        id='population-slider-interval',
        interval=250,  # 0.25 seconds
        n_intervals=0,
        disabled=True       
    ),
    html.H1("Real Time Iceland Economic Dashboard", className="text-center", title = description_of_dashboard),
    dbc.Tabs([
        dbc.Tab(label="Overview", tab_id="tab-now"),
        dbc.Tab(label="Iceland Through Time", tab_id="tab-time"),
    ], id="tabs", active_tab="tab-now"),
    html.Div(id="tab-content")
], fluid=True)

# Callback to switch between tabs
@app.callback(
    Output("tab-content", "children"),
    Input("tabs", "active_tab")
)
def render_tab_content(active_tab):
    if active_tab == "tab-time":
        return iceland_through_time.div  
    elif active_tab == "tab-now":
        return state_of_the_economy.div

# callbacks for Iceland Through Time tab

"""
 CALLBACKS FOR ICELAND THROUGH TIME TAB
"""
app.callback(
    Output("time-series-graph", "figure"),
    Input("variable-selector", "value"),
    Input("secondary-dropdown", "children"),
    Input("interval-component", "n_intervals")
)(iceland_through_time.update_time_series)

app.callback(
    Output("secondary-dropdown", "children"),
    Input("variable-selector", "value")
)(iceland_through_time.update_secondary_dropdown)


app.callback(
    Output("net_migration", "figure"),
    Output("births_and_deaths", "figure"),
    Input("interval-component", "n_intervals")
)(iceland_through_time.fluxFigs)

app.callback(
    Output("native_non_native", "figure"),
    Input("interval-component", "n_intervals")
)(iceland_through_time.nativeNonNative)

app.callback(
    Output("population-line-chart", "figure"),
    Input("interval-component", "n_intervals")
)(iceland_through_time.populationLineChart)

app.callback(
    Output("non-binary-chart", "figure"),
    Input("interval-component", "n_intervals")
)(iceland_through_time.nonBinaryChart)

app.callback(
    Output("population-pyramid-chart", "figure"),
    Input("population-slider", "value"),
    Input("interval-component", "n_intervals"),
)(iceland_through_time.populationPyramidChart)

app.callback(
    Output("play-button", "children"),
    Output("population-slider-interval", "disabled"),
    Output("interval-component", "disabled"),
    Input("play-button", "n_clicks"),
)(utils.toggle_play_button)

app.callback(
    Output("population-slider", "value"),
    Input("play-button", "children"),
    Input("population-slider", "value"),
    Input("population-slider-interval", "n_intervals"),
)(utils.play_slider)
        

"""
 CALLBACKS FOR THE STATE OF THE ECONOMY TAB
"""

@app.callback(
    Output("consumer-price-index-text", "children"),
    Output("population-text", "children"),
    Output("net-migration-text", "children"),
    Output("gross-domestic-product-text", "children"),
    Input("interval-component", "n_intervals")
)
def update_state_of_economy(n_intervals)->tuple[str,str,str,str]:
    results = (
        state_of_the_economy.getCPI(),
        state_of_the_economy.getPopulation(),
        state_of_the_economy.getNetMigration(),
        state_of_the_economy.getGDP()
    )
    return results

app.callback(
    Output("population-stacked-pie", "figure"),
    Input("interval-component", "n_intervals")
)(state_of_the_economy.makeIcelandicPopulationBreakDown)

app.callback(
    Output("employment-by-economic-activity", "figure"),
    Input("interval-component", "n_intervals")
)(state_of_the_economy.makeEmploymentPieChart)


