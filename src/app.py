import dash
from dash import dcc, html, Output, Input
import dash_bootstrap_components as dbc

from .dashboard import iceland_through_time, state_of_the_economy

# Initialize app
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
app.title = "Iceland Economic Dashboard"
server = app.server

# Layout
app.layout = dbc.Container([
    dcc.Interval(
        id='interval-component',
        interval=1*1000,  # 1 second
        n_intervals=0
    ),
    dbc.Tabs([
        dbc.Tab(label="Iceland Through Time", tab_id="tab-time"),
        dbc.Tab(label="State of the Economy", tab_id="tab-now")
    ], id="tabs", active_tab="tab-time"),
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

# callback for the state of the economy tab
app.callback(
    Output("snapshot-graph", "figure"),
    Output("sector-breakdown-graph", "figure"),
    Input("interval-component", "n_intervals")
)(state_of_the_economy.update_snapshot_graphs)