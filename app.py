import dash
from dash import dcc, html, Input, Output
import plotly.express as px
from data_loader import load_and_clean_data

# Load data
df_tidy, df_comp = load_and_clean_data()

# Initialize the Dash app
app = dash.Dash(__name__)
server = app.server
app.title = "Global Climate Anomalies"

CHART_TEMPLATE = "simple_white"

# Define Layout
app.layout = html.Div(className='notion-container', children=[
    
    # Header Section
    html.Div(className='notion-header', children=[
        html.H1("🌡️ Climate Change: Temperature Anomalies"),
        html.P("Analyzing Combined Land-Surface Air and Sea-Surface Water Temperature Anomalies in the Northern Hemisphere.", className='notion-text-gray'),
    ]),

    # Interactive Controls
    html.Div(className='notion-card', children=[
        html.H3("Filters & Controls"),
        html.Label("Select Year Range:"),
        dcc.RangeSlider(
            id='year-slider',
            min=int(df_tidy['Year'].min()),
            max=int(df_tidy['Year'].max()),
            step=1,
            value=[1880, int(df_tidy['Year'].max())],
            marks={year: str(year) for year in range(1880, 2030, 20)},
            className='notion-slider'
        ),
        html.Br(),
        html.Label("Select Months to Display:"),
        dcc.Dropdown(
            id='month-dropdown',
            options=[{'label': m, 'value': m} for m in df_tidy['month'].unique()],
            value=list(df_tidy['month'].unique()),
            multi=True,
            className='notion-dropdown'
        )
    ]),

    # Section 1: Time Series Trend
    html.Div(className='notion-card', children=[
        html.H2("1. Overall Temperature Trend"),
        dcc.Graph(id='timeseries-chart')
    ]),

    # Section 2: Faceted Monthly View
    html.Div(className='notion-card', children=[
        html.H2("2. Seasonal & Monthly Heat Profile"),
        dcc.Graph(id='faceted-chart')
    ]),

    # Section 3: Density Curves
    html.Div(className='notion-card', children=[
        html.H2("3. Distribution of Monthly Temperature Anomalies by Time Period"),
        html.P("Density curves showing the distribution shift of temperature anomalies across historical intervals."),
        dcc.Graph(id='density-chart')
    ]),

    # Section 4: Statistical Conclusion & Image
    html.Div(className='notion-card', children=[
        html.H2("4. Analytical Conclusion & Bootstrap Simulation"),
        
        # 确保你在 assets 文件夹下放了 bootstrap.png
        html.Img(src='/assets/bootstrap.png', style={'width': '100%', 'maxWidth': '800px', 'marginBottom': '20px', 'borderRadius': '6px'}),
        
        html.Div(className='notion-callout', children=[
            html.Div([
                html.P("To analyze the trajectory of global climate change, we first visualized historical temperature anomalies using monthly and annual time-series scatter plots, trend lines, and period-based density distributions. Both the annual and monthly anomalies graphs suggest a rising trend after 2011."),
                html.P("And then we use the bootstrap simulation and formula method for cross checking to further confirm this pattern, which finally shows we are 95% confident that the true average temperature anomaly for 2011-present is between 1.13°C and 1.22°C."),
                html.P(html.B("Hence our analysis suggests that there is a global warming trend in increasing temperature over the period."))
            ])
        ])
    ])
])

# Callbacks for Interactivity
@app.callback(
    [Output('timeseries-chart', 'figure'),
     Output('faceted-chart', 'figure'),
     Output('density-chart', 'figure')],
    [Input('year-slider', 'value'),
     Input('month-dropdown', 'value')]
)
def update_charts(year_range, selected_months):
    filtered_tidy = df_tidy[(df_tidy['Year'] >= year_range[0]) & 
                            (df_tidy['Year'] <= year_range[1]) &
                            (df_tidy['month'].isin(selected_months))]
    
    filtered_comp = df_comp[(df_comp['Year'] >= year_range[0]) & 
                            (df_comp['Year'] <= year_range[1]) &
                            (df_comp['month'].isin(selected_months))]

    # 1. Timeseries Plot (Safe version without lowess)
    fig_time = px.scatter(
        filtered_tidy, x='date', y='delta', 
        opacity=0.6, color_discrete_sequence=['#2E5C8A'],
        template=CHART_TEMPLATE,
        labels={'date': 'Date', 'delta': 'Temperature Anomaly (°C)'}
    )
    fig_time.update_layout(margin=dict(l=20, r=20, t=30, b=20))

    # 2. Faceted Plot (Safe version without lowess)
    fig_facet = px.scatter(
        filtered_tidy, x='date', y='delta', facet_col='month', facet_col_wrap=3,
        opacity=0.6, color_discrete_sequence=['#2E5C8A'],
        template=CHART_TEMPLATE, height=700,
        labels={'date': '', 'delta': 'Anomaly (°C)'}
    )
    fig_facet.for_each_annotation(lambda a: a.update(text=a.text.split("=")[-1]))
    
    # 3. Density Plot
    fig_density = px.violin(
        filtered_comp, x='delta', y='interval', color='interval',
        orientation='h', side='positive',
        template=CHART_TEMPLATE,
        labels={'interval': 'Historical Epoch', 'delta': 'Temperature Anomaly (°C)'},
        color_discrete_sequence=px.colors.qualitative.Pastel
    )
    fig_density.update_traces(meanline_visible=True, width=1.5)
    fig_density.update_layout(showlegend=False, margin=dict(l=20, r=20, t=30, b=20))

    return fig_time, fig_facet, fig_density

if __name__ == '__main__':
    app.run_server(debug=True)
