import sqlite3
import plotly.express as px
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from dash import dcc, html
import dash_bootstrap_components as dbc
import datetime as dt

from ..constants import SOURCE

div = html.Div([
        html.H2("Overview of the Icelandic Economy", style={"textAlign": "center"}),
        html.Div([
            html.Div([
                html.H4("Consumer Price Index"),
                html.P(id = 'consumer-price-index-text', style={"fontSize": "24px", "fontWeight": "bold"})
            ], style={
                    "background": "#f9f9f9",
                    "borderRadius": "10px",
                    "boxShadow": "0 2px 6px rgba(0,0,0,0.1)",
                    "padding": "15px",
                    "textAlign": "center",
                    "transition": "0.3s ease"
                }),

            html.Div([
                html.H4("Population"),
                html.P(id = 'population-text', style={"fontSize": "24px", "fontWeight": "bold"})
            ], style={
                    "background": "#f9f9f9",
                    "borderRadius": "10px",
                    "boxShadow": "0 2px 6px rgba(0,0,0,0.1)",
                    "padding": "15px",
                    "textAlign": "center",
                    "transition": "0.3s ease"
                }),

            html.Div([
                html.H4("Net Migration"),
                html.P(id = 'net-migration-text', style={"fontSize": "24px", "fontWeight": "bold"})
            ], style={
                    "background": "#f9f9f9",
                    "borderRadius": "10px",
                    "boxShadow": "0 2px 6px rgba(0,0,0,0.1)",
                    "padding": "15px",
                    "textAlign": "center",
                    "transition": "0.3s ease"
                }),

            html.Div([
                html.H4("Gross Domestic Product"),
                html.P(id = 'gross-domestic-product-text', style={"fontSize": "24px", "fontWeight": "bold"})
            ], style={
                    "background": "#f9f9f9",
                    "borderRadius": "10px",
                    "boxShadow": "0 2px 6px rgba(0,0,0,0.1)",
                    "padding": "15px",
                    "textAlign": "center",
                    "transition": "0.3s ease"
                }),
        ], style={
            "display": "grid",
            "gridTemplateColumns": "repeat(auto-fit, minmax(200px, 1fr))",
            "gap": "20px",
            "padding": "20px"
        }),
        html.Div([
            html.Div([
                dcc.Graph(id='population-stacked-pie', style={"height": "650px", "width": "100%"},config={"displayModeBar": False}),
            ], style={"width": "25%", "display": "inline-block", "verticalAlign": "top"}),

            html.Div([
                dcc.Graph(id='employment-by-economic-activity', style={"height": "650px", "width": "100%"},config={"displayModeBar": False}),
            ], style={"width": "75%", "display": "inline-block", "verticalAlign": "top"}),
        ],
        style={"width": "100%", 'height':'650px'})
    ],
    style={"fontFamily": "Arial, sans-serif"}
)


def getCPI()->str:
    query = """
    SELECT "Consumer price index Index" FROM CPI
    WHERE "Month" = (SELECT MAX("Month") FROM CPI)
    """
    conn = sqlite3.connect(SOURCE.DATA.DB.str)
    cursor = conn.cursor()
    cursor.execute(query)
    CPI = cursor.fetchone()[0]
    conn.close()
    return str(CPI)    

def getPopulation()->str:
    query = """
    SELECT "{}" FROM Population
    WHERE SEX == "Total" AND AGE == "Total"
    """.format(dt.datetime.now().year)
    conn = sqlite3.connect(SOURCE.DATA.DB.str)
    cursor = conn.cursor()
    cursor.execute(query)
    population = cursor.fetchone()[0]
    conn.close()
    return "{:,.0f}".format(float(population))


def getNetMigration()->str:
    query = """
    SELECT "TOTAL TOTAL" FROM Flux
    WHERE QUARTER = (SELECT MAX(QUARTER) FROM Flux)
    AND EVENT == "Net migration"
    """
    conn = sqlite3.connect(SOURCE.DATA.DB.str)
    cursor = conn.cursor()
    cursor.execute(query)
    net_migration = cursor.fetchone()[0]
    conn.close()
    return str(net_migration)

def getGDP()->str:
    qry = """
    SELECT "2024Q4"
    FROM GDP
    WHERE "Value unit" == "Current prices" AND
    Category == "8. Gross Domestic Product"
    """
    conn = sqlite3.connect(SOURCE.DATA.DB.str)
    cursor = conn.cursor()
    cursor.execute(qry)
    GDP = cursor.fetchone()[0]
    conn.close()
    return "{:,.0f}".format(float(GDP)) + " ISK" 

def makeEmploymentPieChart(n:int)->go.Figure:
    query = """
    SELECT "Economic Activity", "2024Q4" From Employment
    WHERE "Value unit" == 'Persons'
    AND "Employment" == "Total employment"
    AND "Economic Activity" != "Total - All activities"
    """
    conn = sqlite3.connect(SOURCE.DATA.DB.str)
    pieFrame = pd.read_sql_query(query, conn)

    #make pie chart with plotly
    fig = px.pie(pieFrame, values='2024Q4', names='Economic activity')
    fig.update_traces(showlegend=False)
    fig.update_layout(title_font_size=20, title_x=0.5, title_y=0.95, title_text="Total Employment by Economic Activity in 2024Q4")
    
    conn.close()
    return fig.update_layout(uirevision='None')
    
def makeIcelandicPopulationBreakDown(n:int)->go.Figure:
    query = """
    SELECT TOTAL, MALES, FEMALES, "Non-Binary/Other", "Icelandic citizens", "Foreign citizens"
    FROM Population_by_municipality
    WHERE Quarter == '2024Q4' AND Municipality == 'Total'
    """
    conn = sqlite3.connect(SOURCE.DATA.DB.str)

    dictionary = pd.read_sql_query(query, conn)
    data = dictionary.to_dict(orient='records')[0]

    fig = make_subplots(rows=3, cols=2,
                        specs=[[{'type':'domain'},{'type':'domain'}], 
                            [{'type':'domain'},{'type':'domain'}],
                            [{'type':'domain'},{'type':'domain'}]],
                        column_widths=[0.5,0.5])

    fig.add_trace(go.Pie(
        labels=['Males', 'Females', 'Non-binary/Other'],
        values=[data['Males'], data['Females'], int(data['Non-binary/Other'])],
        name='Sex',
        hole=0.4
    ), row=1, col=1)

    fig.add_trace(go.Pie(
        labels=['Total'],
        values=[data['Total']],
        name='Total',
        hole=0.6,
        marker_colors=['lightgrey'],
        textinfo='label+value'
    ), row=2, col=2)

    fig.add_trace(go.Pie(
        labels=['Icelandic citizens', 'Foreign citizens'],
        values=[data['Icelandic citizens'], int(data['Foreign citizens'])],
        name='Citizenship',
        hole=0.4
    ), row=3, col=1)

    fig.update_layout(
        title_text="Iceland Population Breakdown (2025)",
        title_x=0.5,
        width = 450,
        height = 800,
        showlegend=False,
        uirevision='None',
    )

    return fig
