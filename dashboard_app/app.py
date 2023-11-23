import dash
from dash import dcc, html
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output
import plotly.graph_objs as go
import plotly.express as px
import pymysql
from sqlalchemy import create_engine
import pandas as pd
from django_plotly_dash import DjangoDash


# Establish a connection to the MariaDB database
def create_db_engine():
    user = 'seif'  # replace with your MariaDB username
    password = 'ahlawy99'  # replace with your MariaDB password
    host = 'localhost'  # replace with your MariaDB host, usually localhost
    database = 'cashier'  # replace with your database name
    engine = create_engine(f'mysql+pymysql://{user}:{password}@{host}/{database}')
    return engine


# Query MariaDB and return dataframe
def query_data(sql, columns=None):
    engine = create_db_engine()
    with engine.connect() as conn:
        df = pd.read_sql(sql, conn, columns=columns)
        return df


# Define a function to create a graph from a dataframe
def create_graph(df, x, y, title, graph_type='line'):
    if graph_type == 'line':
        fig = go.Figure([go.Scatter(x=df[x], y=df[y], mode='lines+markers')])
    elif graph_type == 'bar':
        fig = go.Figure([go.Bar(x=df[x], y=df[y])])
    # Add more graph types as needed
    fig.update_layout(title=title)
    fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
    fig.update_xaxes(visible=False)
    fig.update_yaxes(visible=False)
    return fig


def create_card(header, value, comparison_value=None):
    # Calculate the percentage difference if a comparison value is provided
    percentage_diff = ((value - comparison_value) / comparison_value) * 100 if comparison_value else ''

    # Construct the card with Bootstrap components
    card_content = [
        dbc.CardHeader(html.H6(header, className='text-primary fw-bold m-0')),
        dbc.CardBody(html.P(f'{value:,.2f}', className='m-0')),
        dbc.CardFooter(
            html.P(f'{percentage_diff:+.2f}%' if comparison_value else '', className='text-primary m-0 small'))
    ]

    return dbc.Card(card_content, className='card shadow border-start-primary py-2')


def card_column(header, current_value_query, comparison_value_query):
    # Fetch current and comparison values from the database
    current_value = query_data(current_value_query).iloc[0]['total_sales']
    comparison_value = query_data(comparison_value_query).iloc[0]['total_sales'] if comparison_value_query else None

    # Create the card
    try:
        card_component = create_card(header, current_value, comparison_value)
    except TypeError:
        card_component = create_card(header, 0, 0)

    # Return the column component
    return dbc.Col(card_component, width=4)


# Initialize the Dash app with Bootstrap components
app = DjangoDash('DashboardApp', external_stylesheets=[
    # dbc.themes.BOOTSTRAP,
    'https://cdn.jsdelivr.net/npm/tw-elements/dist/css/tw-elements.min.css'
])

app.layout = html.Div([
    html.Div([
        html.H2('GroceryTracker Overview', className='text-xl'),
        # Other sidebar components here
    ], className='sidebar bg-gray-200 p-4'),

    html.Div([
        html.Div([
            # Overview cards
            html.Div('Total Sales', className='card'),
            # Other cards
        ], className='flex flex-wrap gap-4'),

        dcc.Graph(
            id='sales-overview',
            figure={
                # Define your figure here
            }
        )
        # Other main content components here
    ], className='content flex-1 p-4')
], className='main-container flex')

## best Layout
# Define the layout of the app using Bootstrap components
# app.layout = html.Div([
#     dbc.Row(
#         [
#             card_column('Daily Sales', "SELECT SUM(total) as total_sales FROM Cashier_invoice WHERE date = CURDATE();",
#                         "SELECT SUM(total) as total_sales FROM Cashier_invoice WHERE date = CURDATE() - INTERVAL 1 DAY;"),
#             card_column('Weekly Sales',
#                         "SELECT SUM(total) as total_sales FROM Cashier_invoice WHERE WEEK(date) = WEEK(CURDATE());"
#                         ,
#                         "SELECT SUM(total) as total_sales FROM Cashier_invoice WHERE WEEK(date) = WEEK(CURDATE()) - 1;"),
#             card_column('Monthly Sales',
#                         "SELECT SUM(total) as total_sales FROM Cashier_invoice WHERE MONTH(date) = MONTH(CURDATE());",
#                         "SELECT SUM(total) as total_sales FROM Cashier_invoice WHERE MONTH(date) = MONTH(CURDATE()) - 1;"),
#         ]),
#     dbc.Container(fluid=True, children=[
#         dbc.Row([
#             dbc.Col(dcc.Graph(id='sales-graph'), width=12, lg=6),
#             dbc.Col(dcc.Graph(id='stock-graph'), width=12, lg=6),
#             # Add additional tiles (graphs) here
#         ]),
#         dbc.Row([
#             dcc.DatePickerRange(
#                 id='date-range',
#                 start_date_placeholder_text="Start Period",
#                 end_date_placeholder_text="End Period",
#                 calendar_orientation='horizontal',
#                 start_date='2023-10-22',
#                 end_date='2023-11-15',
#             ),
#             dcc.Graph(id='pie-chart')
#         ]),
#         dcc.Interval(id='update-interval', interval=30 * 1000, n_intervals=0)  # Update every minute
#     ], className='my-4'),
#     html.Footer(html.P('Copyright Information, Privacy Policy, and Terms of Service links'))
# ])


@app.callback(
    Output('pie-chart', 'figure'),
    [Input('date-range', 'start_date'),
     Input('date-range', 'end_date')]
)
def update_chart(start_date, end_date):
    if start_date is not None and end_date is not None:
        df = query_data("""
        SELECT p.name, SUM(i.quantity) as total_quantity
        FROM Cashier_product AS p
        JOIN Cashier_invoiceitem AS i ON p.ean = i.product_id
        JOIN Cashier_invoice AS inv ON i.invoice_id = inv.id
        WHERE inv.date BETWEEN "{}" AND "{}"
        GROUP BY p.name
        ORDER BY total_quantity DESC
        LIMIT 4
        """.format(start_date, end_date))
        fig = px.pie(df, values='total_quantity', names='name', title='Top Sales')
        return fig
    return {}

# Callbacks to update each graph
@app.callback(
    Output('sales-graph', 'figure'),
    [Input('update-interval', 'n_intervals')]
)
def update_sales_graph(n_intervals):
    sql_query = "SELECT date, SUM(total) as total_sales FROM Cashier_invoice GROUP BY date;"
    df = query_data(sql_query)
    return create_graph(df, 'date', 'total_sales', 'Total Sales Over Time')


@app.callback(
    Output('stock-graph', 'figure'),
    [Input('update-interval', 'n_intervals')]
)
def update_stock_graph(n_intervals):
    sql_query = "SELECT name, stock FROM Cashier_product;"
    df = query_data(sql_query)
    return create_graph(df, 'name', 'stock', 'Current Stock Levels', graph_type='bar')

# # Add additional callbacks for other graphs as needed
#
#
# # import dash
# # from dash import dcc, html
# # import dash_bootstrap_components as dbc
# # from django_plotly_dash import DjangoDash
# # import plotly.express as px
# # from dash.dependencies import Input, Output
# # import pandas as pd
# # import pymysql
# # from sqlalchemy import create_engine
# # import pandas.io.sql as psql
# # import os
# #
# #
# # # Initialize Dash app with Bootstrap
# # app = DjangoDash('DashboardApp', external_stylesheets=[dbc.themes.BOOTSTRAP])
# #
# # # Establishing a connection to the MySQL database
# # def db_connection():
# #     return pymysql.connect(
# #         host='localhost',
# #         user='seif', # Replace with your MySQL username
# #         password='ahlawy99', # Replace with your MySQL password
# #         database='cashier' # Replace with your database name
# #     )
# #
# # # Function to fetch data from MySQL database
# # def fetch_data(query):
# #     conn = db_connection()
# #     return psql.read_sql_query(query, conn)
# #
# # # Function to generate a plotly express figure
# # def generate_figure(data, chart_type, x_axis, y_axis, title):
# #     fig = getattr(px, chart_type)(data, x=x_axis, y=y_axis, title=title)
# #     fig.update_layout(transition_duration=500)
# #     return fig
# #
# #
# # # Define the layout of the app
# # app.layout = html.Div([
# #     dbc.NavbarSimple(
# #         brand='Store Name or Logo',
# #         brand_href='#',
# #         color='primary',
# #         dark=True,
# #         children=[
# #             dbc.NavItem(dbc.NavLink('Settings', href='#')),
# #         ]
# #     ),
# #     dbc.Container(fluid=True, children=[
# #         dbc.Row(
# #             [dbc.Col(dcc.Graph(id='sales_graph'), width=12, lg=4),
# #              # Add more tiles with dbc.Col as needed
# #             ],
# #             className='mb-4',
# #         ),
# #         # More rows for additional content
# #     ]),
# #     dbc.Footer(
# #         html.P(
# #             'Copyright Information, Privacy Policy, and Terms of Service links',
# #             className='text-center'
# #         ),
# #     ),
# # ])
# #
# # # Callbacks to update graphs in real-time
# # @app.callback(
# #     Output('sales_graph', 'figure'),
# #     [Input('interval-component', 'n_intervals')]
# # )
# # def update_graph_live(n):
# #     query = "SELECT * FROM sales_data WHERE date BETWEEN CURDATE() - INTERVAL 1 DAY AND CURDATE()"
# #     data = fetch_data(query)
# #     figure = generate_figure(data, 'line', 'date', 'total_sales', 'Daily Sales')
# #     return figure
#
#
# # Start working script
# # conn = sqlite3.connect('/media/seif/1cbb163a-5410-4ad8-b622-86d0e3e57702/seif/PycharmProjects/CashierBase/db.sqlite3')
# #
# # products = pd.read_sql('SELECT * FROM main.Cashier_product', conn)
# # invoices = pd.read_sql('SELECT * FROM main.Cashier_invoice', conn)
# # invoice_items = pd.read_sql('SELECT * FROM main.Cashier_invoiceitem', conn)
# #
# # invoices['date'] = pd.to_datetime(invoices['date'])
# # total_by_day = invoices.groupby(invoices['date'].dt.date)['total'].sum()
# #
# # # Get the current day, week, month, and year
# # today = datetime.date.today()
# # current_week = today.isocalendar()[1]
# # current_month = today.month
# # current_year = today.year
# #
# # # Calculate the total earnings for the current day, week, month, and year
# # current_day_total = invoices.loc[invoices['date'] == pd.to_datetime(today)]['total'].sum()
# # current_week_total = invoices.loc[invoices['date'].dt.isocalendar().week == current_week]['total'].sum()
# # current_month_total = invoices.loc[invoices['date'].dt.month == current_month]['total'].sum()
# # current_year_total = invoices.loc[invoices['date'].dt.year == current_year]['total'].sum()
# #
# # # Calculate the difference between the current and last day, week, month, and year earnings
# # last_day_total = invoices.loc[invoices['date'] == today - datetime.timedelta(days=1)]['total'].sum()
# # last_week_total = invoices.loc[invoices['date'].dt.isocalendar().week == current_week - 1]['total'].sum()
# # last_month_total = invoices.loc[invoices['date'].dt.month == current_month - 1]['total'].sum()
# # last_year_total = invoices.loc[invoices['date'].dt.year == current_year - 1]['total'].sum()
# #
# # app = DjangoDash('DashboardApp', external_stylesheets=[themes.BOOTSTRAP],
# #                  external_scripts=['static/bootstrap/js/bootstrap'
# #                                    '.min.js',
# #                                    'static/js/chart.min.js',
# #                                    'static/js/bs-init.js', ])
#
# ### END Working Script
#
#
# # earnings = {
# #     "Daily": "40,000",
# #     "Weekly": "215,000",
# #     "Monthly": "1,200,000",
# #     "Yearly": "5,000,000"
# # }
# # data_points = [40000, 80000, 60000, 120000, 100000, 200000]
#
# #
# # @app.callback(
# #     Output('pie-chart', 'figure'),
# #     DashInput('pie-chart', 'relayoutData')
# # )
# # def pie_chart(relayoutData):
# #     fig = px.pie(earnings.items())
# #     return fig
# #
# #
# # @app.callback(
# #     Output('line-chart', 'figure'),
# #     DashInput('line-chart', 'relayoutData')
# # )
# # def line_chart(relayoutData):
# #     # Create a Plotly line chart
# #     fig = px.line(y=data_points, labels={'y': 'Earnings'}, line_shape='spline')
# #
# #     return fig
#
# #
#
# # app.layout = html.Main(
# #     [
# #         html.Header(
# #             [
# #                 Container(
# #                     [
# #                         html.Div(
# #                             [html.H3("Dashboard", className="text-dark mb-0"),
# #                              html.A(className="btn btn-primary btn-sm d-none d-sm-inline-block", role="button",
# #                                     href="#",
# #                                     children=[html.I(className="fas fa-download fa-sm text-white-50"),
# #                                               "Generate Report"])
# #                              ]
# #                             , className="d-sm-flex justify-content-between align-items-center mb-4"
# #                         )
# #                     ], class_name='mt-5'
# #                 )
# #                 , Row(style={'margin': '8%'},
# #                       children=[*[Col(className='col-md-6 col-xl-3 mb-4',
# #                                       children=[
# #                                           card(e, v)
# #                                       ]) for e, v in earnings.items()],
# #                                 ])
# #                 , Row(style={'margin': '8%'},
# #                       children=[Col(className='col-lg-7 col-xl-8', children=[
# #                           Card(className='shadow mb-4', children=[
# #                               CardHeader(className='d-flex justify-content-between align-items-center',
# #                                          children=[
# #                                              html.H6(className='text-primary fw-bold m-0',
# #                                                      children=['Earnings Overview'])
# #                                          ]),
# #                               CardBody(children=[
# #                                   html.Div(className='chart-area', children=[
# #                                       dcc.Graph(id='line-chart')
# #                                   ])
# #                               ])
# #                           ])
# #                       ]),
# #                                 Col(className='col-lg-5 col-xl-4', children=[
# #                                     Card(className='shadow mb-4', children=[
# #                                         CardHeader(className='d-flex justify-content-between align-items-center',
# #                                                    children=
# #                                                    [
# #                                                        html.H6(className='text-primary fw-bold m-0',
# #                                                                children=['Earnings Overview'])
# #                                                    ]),
# #                                         CardBody(children=[
# #                                             html.Div(className='chart-area', children=[
# #                                                 dcc.Graph(id='pie-chart')
# #                                             ])
# #                                         ])
# #                                     ])
# #                                 ]),
# #                                 ]),
# #             ]), ]
# # )
# ### Google Bard's code
# # app.layout = Container([
# #     # مبيعات section
# #     Row([
# #         Col(html.H1("المبيعات", className="text-center"), width=12)
# #     ]),
# #     Row([
# #         Col(Card([
# #             CardHeader("Daily Revenues"),
# #             CardBody(html.H3(str(current_day_total), className="text-center")),
# #             CardFooter(
# #                 f"Change compared to yesterday: {str((current_day_total - last_day_total) / last_day_total * 100)} %")
# #         ]), width=4),
# #         Col(Card([
# #             CardHeader("Weekly Revenues"),
# #             CardBody(html.H3(str(current_week_total), className="text-center")),
# #             CardFooter("% Change compared to last week: " + str(
# #                 (current_week_total - last_week_total) / last_week_total * 100))
# #         ]), width=4),
# #         Col(Card([
# #             CardHeader("Monthly Revenues"),
# #             CardBody(html.H3(str(current_month_total), className="text-center")),
# #             CardFooter("% Change compared to last month: " + str(
# #                 (current_month_total - last_month_total) / last_month_total * 100))
# #         ]), width=4)
# #     ], className="mb-4"),
# #     Row([
# #         Col(Card([
# #             CardHeader(
# #                 ["Earnings By ",
# #                  dcc.Dropdown(
# #                      [
# #                          {"label": "Day", "value": "day"},
# #                          {"label": "Week", "value": "week"},
# #                          {"label": "Month", "value": "month"},
# #                          {"label": "Year", "value": "year"},
# #                      ],
# #                      id="earnings-by"
# #
# #                  )]),
# #             CardBody(html.H3(str(current_year_total), className="text-center")),
# #             CardFooter("% Change compared to last year: " + str(
# #                 (current_year_total - last_year_total) / last_year_total * 100))
# #         ]), width=12)
# #     ]),
# #     Row([
# #         Col(Card([
# #             CardHeader("مبيعات by department"),
# #             CardBody(dcc.Graph(id="مبيعات-by-department")),
# #             CardFooter("Compared to last year: +10%")
# #         ]), width=12)
# #     ], className="mb-4"),
# #     Row([
# #         Col(Card([
# #             CardHeader("مبيعات by product"),
# #             CardBody(dcc.Graph(id="مبيعات-by-product")),
# #             CardFooter("Compared to last year: +5%")
# #         ]), width=12)
# #     ], className="mb-4"),
# #
# #     # Reports section
# #     Row([
# #         Col(html.H1("Reports", className="text-center"), width=12)
# #     ], className="mb-4"),
# #     Row([
# #         Col(Button("Daily مبيعات report", id="generate-daily-مبيعات-report", className="btn btn-primary"), width=3),
# #         Col(Button("Weekly مبيعات report", id="generate-weekly-مبيعات-report", className="btn btn-primary"), width=3),
# #         Col(Button("Monthly مبيعات report", id="generate-monthly-مبيعات-report", className="btn btn-primary"), width=3),
# #         Col(Button("Inventory report", id="generate-inventory-report", className="btn btn-primary"), width=3)
# #     ], className="mb-4"),
# #     Row([
# #         Col(dcc.Download(id="daily-مبيعات-report")),
# #         Col(dcc.Download(id="weekly-مبيعات-report")),
# #         Col(dcc.Download(id="monthly-مبيعات-report")),
# #         Col(dcc.Download(id="inventory-report"))
# #     ], className="mb-4")
# # ])
