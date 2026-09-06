import dash
from dash import dcc, html, Input, Output
import plotly.express as px
from data_loader import load_and_clean_data

# Load data using the exact logic from the Jupyter Notebook
df_tidy, df_comp = load_and_clean_data()

# Initialize the Dash app
app = dash.Dash(__name__)
server = app.server # Required for Render/Gunicorn deployment
app.title = "Global Climate Anomalies"

# Global Notion-style chart template
CHART_TEMPLATE = "simple_white"

# Define Layout
app.layout = html.Div(className='notion-container', children=[
    
    # Header Section
    html.Div(className='notion-header', children=[
        html.H1("🌡️ Climate Change: Temperature Anomalies"),
        html.P("Analyzing Combined Land-Surface Air and Sea-Surface Water Temperature Anomalies in the Northern Hemisphere.", className='notion-text-gray'),
        html.Div(className='notion-callout', children=[
            html.Span("💡 Reference Base Period: "),
            html.Span("1951-1980 (NASA Goddard Institute for Space Studies)")
        ])
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
        html.P("Time-series scatter plot showing temperature anomalies with a LOESS smoothing trendline."),
        dcc.Graph(id='timeseries-chart')
    ]),

    # Section 2: Faceted Monthly View
    html.Div(className='notion-card', children=[
        html.H2("2. Seasonal & Monthly Heat Profile"),
        html.P("Faceted view to determine if warming is more pronounced in specific months."),
        dcc.Graph(id='faceted-chart')
    ]),

    # Section 3: Epoch Comparison (Box Plot)
    html.Div(className='notion-card', children=[
        html.H2("3. Historical Climate Eras"),
        html.P("Comparing anomaly distributions across predefined historical intervals."),
        dcc.Graph(id='interval-chart')
    ])
])

# Callbacks for Interactivity
@app.callback(
    [Output('timeseries-chart', 'figure'),
     Output('faceted-chart', 'figure'),
     Output('interval-chart', 'figure')],
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

    # 1. Timeseries Plot
    fig_time = px.scatter(
        filtered_tidy, x='date', y='delta', 
        trendline='lowess', trendline_color_override='red',
        opacity=0.6, color_discrete_sequence=['#2E5C8A'],
        template=CHART_TEMPLATE,
        labels={'date': 'Date', 'delta': 'Temperature Anomaly (°C)'}
    )
    fig_time.update_layout(margin=dict(l=20, r=20, t=30, b=20))

    # 2. Faceted Plot
    fig_facet = px.scatter(
        filtered_tidy, x='date', y='delta', facet_col='month', facet_col_wrap=3,
        opacity=0.6, color_discrete_sequence=['#2E5C8A'],
        template=CHART_TEMPLATE, height=700,
        labels={'date': '', 'delta': 'Anomaly (°C)'}
    )
    fig_facet.for_each_annotation(lambda a: a.update(text=a.text.split("=")[-1]))
    
    # 3. Interval Box Plot
    fig_box = px.box(
        filtered_comp, x='interval', y='delta', color='interval',
        template=CHART_TEMPLATE,
        labels={'interval': 'Historical Epoch', 'delta': 'Temperature Anomaly (°C)'},
        color_discrete_sequence=px.colors.qualitative.Pastel
    )
    fig_box.update_layout(showlegend=False)

    return fig_time, fig_facet, fig_box

if __name__ == '__main__':
    app.run_server(debug=True)
