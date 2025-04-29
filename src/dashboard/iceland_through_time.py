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
            html.H1("Economic Variables"),
            dcc.Graph(id="time-series-graph",config={'displayModeBar': False}),
            html.H1("Population"),
            html.Div([
                html.Div([
                    dcc.Graph(style={"width": "100%", "height": "100%"},id ='net_migration',config={'displayModeBar': False} )
                ], style={"width": "33%", "display": "inline-block", "padding": "10px"}),

                html.Div([
                    dcc.Graph(style={"width": "100%", "height": "100%"},id='births_and_deaths',config={'displayModeBar': False} )
                ], style={"width": "33%", "display": "inline-block", "padding": "10px"}),

                html.Div([
                    dcc.Graph(style={"width": "100%", "height": "100%"},id='native_non_native',config={'displayModeBar': False} )
                ], style={"width": "33%", "display": "inline-block", "padding": "10px"}),
            ]),
            html.Div([
                html.Div([
                    dcc.Graph(style={"width": "100%", "height": "100%"},id='population-line-chart',config={'displayModeBar': False} )
                ], style={"width": "66%", "display": "inline-block", "padding": "10px"}),
                html.Div([
                    dcc.Graph(style={"width": "100%", "height": "100%"},id='non-binary-chart',config={'displayModeBar': False} )
                ], style={"width": "33%", "display": "inline-block", "padding": "10px"}),
            ]),
            html.Div([
                html.Div([
                    html.Button("Play", id="play-button", n_clicks=0),
                ], style={"display": "inline-block", "paddingRight": "5%"}),
                html.Div([
                    dcc.Slider(
                        id='population-slider',
                        min=1850,
                        max=2025,
                        value=2024,
                        marks={i: str(i) for i in range(1850, 2026, 5)},
                        step=1
                    ),
                ], style={"display": "inline-block", "width": "95%"}),
            ]),
            dcc.Graph(id='population-pyramid-chart', style={"width": "100%", "height": "700px"},config={'displayModeBar': False} ),
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
        .update_layout(uirevision = 'None')
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
        .update_layout(uirevision = 'None')

    )

def charts_consumerPriceIndex(df:pd.DataFrame,variation:str)->go.Figure:
    return (
        df
        .assign(**{variation: lambda x: x[variation].astype('str').str.replace(r'^\.$','0.0',regex = True).astype(float)})
        .plot(x = 'Month', y = variation, title = f"{variation} in Iceland", kind='line', markers=True, template='plotly_white')
        .update_layout(title_x = 0.5)
        .update_yaxes(title_text = '')
        .update_layout(uirevision = 'None')

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
        .update_layout(uirevision = 'None')
    )   

# Population graphs
def fluxFigs(n:int)->tuple[go.Figure,go.Figure]:
    conn = sqlite3.connect(SOURCE.DATA.DB.str)
    df = pd.read_sql_query('''SELECT Quarter,"Total Total",Event FROM Flux
                           WHERE Event IN ('Net migration','Births','Deaths')
                           ''', conn)
    netMigration = (
            df.loc[lambda s: s.Event == 'Net migration',['Quarter','Total Total']]
                .plot(x='Quarter',y='Total Total',title='Net migration in Iceland 2011-2024')
                .update_layout(title_x = 0.5,uirevision = 'None',title_font=dict(size=9),showlegend = False)
                .update_yaxes(title_text = '')
                .update_xaxes(title_text = '')                
    )
    birthsAndDeaths = (
            df.loc[lambda s: (s.Event == 'Births')+(s.Event == 'Deaths'),['Quarter','Event','Total Total']]
                .plot(x='Quarter',y='Total Total',title='Births and Deaths in Iceland 2011-2024',color='Event')
                .update_layout(title_x = 0.5,uirevision = 'None',title_font=dict(size=9),showlegend = False)
                .update_yaxes(title_text = '')
                .update_xaxes(title_text = '')                
    )
    conn.close()
    return netMigration,birthsAndDeaths

def nativeNonNative(n:int)->tuple[go.Figure]:
    conn = sqlite3.connect(SOURCE.DATA.DB.str)
    # df = pd.read_sql_query("SELECT * FROM Population_by_municipality", conn) # write sql insead of filtering w pandas?
    query = """
    SELECT Quarter, Municipality, "Foreign citizens", "Icelandic citizens"
    FROM Population_by_municipality
    WHERE Municipality = 'Total' 
    """
    df = pd.read_sql_query(query, conn)
    fig = (
            df
            .loc[lambda s: s.Municipality == 'Total',['Quarter','Municipality','Foreign citizens','Icelandic citizens']]
            .melt(id_vars=['Quarter','Municipality'])
            .assign(value = lambda s: s.value.astype(float))
            .plot(x = 'Quarter', y = 'value', color = 'variable')
            .update_layout(title = 'Native and Non-native citizens in Iceland 2011-2024', title_x = 0.5, uirevision = 'None',title_font=dict(size=9),showlegend = False)
            .update_yaxes(title_text = '')
            .update_xaxes(title_text = '')
    )
    conn.close()
    return fig

def populationLineChart(n:int)->go.Figure:
    conn = sqlite3.connect(SOURCE.DATA.DB.str)
    query = """
    SELECT * From Population
    WHERE Age == 'Total'
    """

    line_chart = (
            pd.read_sql_query(query, conn)
            .melt(id_vars=['Sex','Age'],var_name='Year',value_name='Population')
            .assign(
                    Year=lambda s: s.Year.astype(int),
                    Population=lambda s: s.Population.replace('..','0').astype(int)
                    )
            .plot(x = 'Year',y='Population',color = 'Sex')
            .update_layout(title = 'Population in Iceland 1841-2025', title_x = 0.5, uirevision = 'None',title_font=dict(size=9),showlegend = False)
            .update_yaxes(title_text = '')
            .update_xaxes(title_text = '')            
    )
    conn.close()
    return line_chart

def nonBinaryChart(n:int)->go.Figure:
    conn = sqlite3.connect(SOURCE.DATA.DB.str)
    query = """
    SELECT "2022", "2023", "2024", "2025", Sex, Age From Population
    WHERE Age == 'Total' AND 
    Sex == 'Non-binary/Other'
    """

    non_binary_chart = (
            pd.read_sql_query(query, conn)
            .melt(id_vars=['Sex','Age'],var_name='Year',value_name='Population')
            .assign(Year=lambda s: s.Year.astype(int),
                    Population=lambda s: s.Population.replace('..','0').astype(int)
                    )
            .plot(x ='Year',y='Population',title = 'Non-binary/Other citizens in Iceland 1841-2025',kind = 'bar')
            .update_layout(title_x = 0.5, uirevision = 'None',showlegend = False)
            .update_layout(title_font=dict(size=9))
            .update_yaxes(title_text = '')
            .update_xaxes(title_text = '')
    )    
    conn.close()
    return non_binary_chart

def populationPyramidChart(year:int,n:int)->go.Figure:
    conn = sqlite3.connect(SOURCE.DATA.DB.str)
    query = """
    SELECT Sex, Age, "{year}" From Population
    WHERE Age != 'Total' AND
    Sex != 'Total' AND
    Sex != 'Non-binary/Other'
    """.format(year=year)

    frame = (
        pd.read_sql_query(query, conn)
        .melt(id_vars=['Sex','Age'],var_name='Year',value_name='Population')
        .assign(Age=lambda s: s.Age.str.replace(r'\syears?','',regex=True).replace('Under 1','0').astype(int),
                Population=lambda s: s.Population.replace('..','0').astype(int)
                )
    )

    df_male = frame[frame['Sex'] == 'Males'].copy()
    df_female = frame[frame['Sex'] == 'Females'].copy()
    df_male['Population'] *= -1  # Invert male values for pyramid shape

    pyramid_chart = go.Figure()

    pyramid_chart.add_trace(go.Bar(
        y=df_male['Age'],
        x=df_male['Population'],
        orientation='h',
        name='Male',
        marker_color='blue'
    ))

    pyramid_chart.add_trace(go.Bar(
        y=df_female['Age'],
        x=df_female['Population'],
        orientation='h',
        name='Female',
        marker_color='red'
    ))

    pyramid_chart.update_layout(
        title=f'Iceland Population Pyramid - {year}',
        xaxis=dict(title='Population',range = [-3500,3500]),
        yaxis=dict(title='Age', categoryorder='category ascending'),
        barmode='overlay',
        bargap=0.1,
        template='plotly_white',
        title_x=0.5,
        showlegend=False,
        uirevision='None',
    )   

    conn.close()
    return pyramid_chart


