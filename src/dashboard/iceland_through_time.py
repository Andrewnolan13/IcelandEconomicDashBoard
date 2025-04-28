from ..constants import SOURCE

import sqlite3
import pandas as pd
import dash_bootstrap_components as dbc
from dash import dcc, html
from plotly import graph_objects as go
import warnings

warnings.filterwarnings("ignore")

pd.options.plotting.backend = "plotly"

div = html.Div([
            html.H3("Iceland Through Time"),
            dcc.Dropdown(
                id="variable-selector",
                options=[
                    {"label": "GDP", "value": "GDP"},
                    {"label": "Consumer Price Index", "value": "CPI"},
                    {"label": "Interest Rates", "value": "Interest"},
                    {"label": "Employment By Sector", "value": "Employment"},
                ],
                value='GDP',  
                multi=False,
            ),
            html.Div(id="secondary-dropdown"),
            dcc.Graph(id="time-series-graph"),
        ])

def update_time_series(selected:str,secondary:dict,n:int):
    # establish conn    
    conn = sqlite3.connect(SOURCE.DATA.DB.str)
    secondaryType = secondary['type']
    value = secondary['props']['value'] if secondaryType == 'Dropdown' else None
    try:
        df = pd.read_sql_query(f"SELECT * FROM {selected}", conn)
        match selected:
            case "GDP":
                return charts_grossDomesticProduct(df, value_unit='Current prices', variation=value or '1. Private final consumption')
            case "CPI":
                return charts_consumerPriceIndex(df,variation = value or 'Consumer price index Index')
            case "Interest":
                return charts_Interest(df,variation = value or 'General savings deposits Nominal interest, % per year')
            case "Employment":
                return charts_EmploymentBySector(df)
            case _:
                raise ValueError(f"Unknown variable: {selected}")
    except Exception:
        raise
    finally:
        conn.close()

def update_secondary_dropdown(selected:str)->dbc.Select:
    # establish conn
    conn = sqlite3.connect(SOURCE.DATA.DB.str)
    df = pd.read_sql_query(f"SELECT * FROM {selected}", conn)
    conn.close()
    match selected:
        case 'GDP':
            options = df['Category'].unique()
        case 'CPI':
            options = df.columns.drop(['Month'])
        case 'Interest':
            options = df.columns.drop(['Year'])
        case 'Employment':
            return html.Div()
        case _:
            raise ValueError(f"Unknown variable: {selected}")
    
    return dcc.Dropdown(
        id="secondary-dropdown-dropdown",
        options=[{"label": option, "value": option} for option in options],
        value=options[0],  # Default value
        multi=False,
    )


def charts_Interest(df:pd.DataFrame,variation:str)->go.Figure:
    return (
        df
        .replace(r'^\.+$','0.0', regex=True)
        .astype(float)
        .plot(x = 'Year', y = variation, title = variation, kind='line', markers=True, template='plotly_white')
        .update_layout(title_x = 0.5)
        .update_yaxes(title_text = '')
    )

def charts_grossDomesticProduct(df:pd.DataFrame,value_unit:str,variation)->go.Figure:
    return (
        df
        .set_index(['Value unit','Category'])
        .loc[pd.IndexSlice[value_unit, variation,:], :]#.T
        .reset_index().T
        .iloc[2:].reset_index(names = 'Quarter')
        .rename(columns = {0:variation})
        .assign(**{variation: lambda x: x[variation].astype(float)})
        .plot(x='Quarter', y=variation, title = f"{variation} in {value_unit}", kind='line', markers=True, template='plotly_white')
        .update_layout(title_x = 0.5)   
        .update_yaxes(title_text = '')
    )

def charts_consumerPriceIndex(df:pd.DataFrame,variation:str)->go.Figure:
    return (
        df
        .assign(**{variation: lambda x: x[variation].astype('str').str.replace(r'^\.$','0.0',regex = True).astype(float)})
        .plot(x = 'Month', y = variation, title = f"{variation} in Iceland", kind='line', markers=True, template='plotly_white')
        .update_layout(title_x = 0.5)
        .update_yaxes(title_text = '')
    )

def charts_EmploymentBySector(df:pd.DataFrame)->go.Figure:
    return (
        df
        .pipe(lambda s: s.set_index(s.columns[:3].tolist()))
        .loc[pd.IndexSlice['Jobs','Total employment'],]
        .drop('Total - All activities')
        .T
        .reset_index(names = 'time')
        .melt(id_vars=['time'], var_name ='sector', value_name='Number of Jobs')
        .plot(x = 'time', y = 'Number of Jobs', color = 'sector',kind = 'area')
        .update_layout(showlegend = False)
    )   


