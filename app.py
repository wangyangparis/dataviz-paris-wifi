import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_core_components as dcc
from dash.dependencies import Input, Output
import pandas as pd

import utils.figure as fig
import utils.wifi_data as wd

app = dash.Dash(__name__)

df_full = wd.get_df_full()

slider_marks = {str(d): str(d) for d in df_full.session_date.dt.day.unique()}
slider_marks[0] = 'March'
app.layout = html.Div([
    # Header
    html.H1("Time-varying Data Visualization"),
    html.H2("Paris WI-FI"),
    # Day Slider
    dcc.Slider(
        id='day-slider',
        min=0,
        max=df_full.session_date.max().day,
        value=0,
        marks=slider_marks,
        step=None,
        included=False
    ),
    # figures
    html.Div([
        # map
        html.Div(dcc.Graph(id='paris-wifi-map', config={'displayModeBar': False}), className='col-6'),
        # TODO heatmap
        html.Div(dcc.Graph(id='paris-wifi-heatmap', config={'displayModeBar': False}), className='col-6'),
    ], className='row'),
    
    html.Div([
        # polar bar daily
        html.Div(dcc.Graph(id='paris-wifi-polarBar', config={'displayModeBar': False}), className='col-6'),
        # TODO polar bar hourly
        html.Div(dcc.Graph(id='paris-wifi-polarBar-hourly', config={'displayModeBar': False}), className='col-6'),
    ], className='row'),
    # Device distribution dropdown
    dcc.Dropdown(
        id = 'dropdown_device',
        options=[
            {'label': 'Device type', 'value': 'TYP'},
            {'label': 'Device constructer', 'value': 'CON'},
        ],
        value='TYP'
    ),     
    html.Div([
        # distribution map
        html.Div(
            dcc.Graph(id='paris-wifi-device', config={'displayModeBar': False}),className='col-12'),
    ], className='row'),
], className='container')

# plot Map
@app.callback(
    Output('paris-wifi-map', 'figure'),
    [Input('day-slider', 'value')])
def update_graph(selected_day):
    if selected_day == 0:
        from_date = pd.datetime(2020, 3, 1, 0)
        to_date = pd.datetime(2020, 3, 31, 23)
    else:
        from_date = pd.datetime(2020, 3, selected_day, 0)
        to_date = pd.datetime(2020, 3, selected_day, 23)
    df = wd.get_df_period_nb_sess(df_full, from_date, to_date, with_info=True)
    return fig.get_fig_map(df)

# plot distribution bar chart
@app.callback(
    Output('paris-wifi-device', 'figure'),
    [Input('dropdown_device', 'value')])

def dist_graph(dropdown):
    if dropdown == 'TYP':
        selected = 1
    elif dropdown == 'CON':
        selected = 2
    df = wd.get_df_dist()[selected]['count']
    return fig.get_fig_dist(df)

# plot Polar Chart
@app.callback(
    [Output('paris-wifi-polarBar', 'figure'),Output('paris-wifi-polarBar-hourly', 'figure')],
    #Output('paris-wifi-polarBar', 'figure'),
    [Input('paris-wifi-map', 'clickData')])
def update_wifi_site_selected(clickData):
    # data of march
    from_date = pd.datetime(2020, 3, 1, 0)
    to_date = pd.datetime(2020, 3, 31, 23)
    site_code = None if clickData is None else clickData['points'][0]['customdata'][0]

    df_daily, df_hourly = wd.get_df_period_nb_sess(df_full, from_date, to_date, site_code=site_code)
    # TODO hourly
    return fig.get_fig_polar_bar(df_daily) , fig.get_fig_polar_bar_hourly(df_hourly)


if __name__ == '__main__':
    app.run_server(debug=True)

