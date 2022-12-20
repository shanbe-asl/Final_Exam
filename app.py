import sqlite3
import matplotlib.pyplot as plt
import plotly.graph_objects as go
import pandas as pd
from dash import Input, Output
from dash import Dash, dcc, html
import dash
import plotly.express as px
import os
import numpy as np
from bs4 import BeautifulSoup
import pandas as pd
import lxml
import requests
import utils.dash_reusable_components as drc

# https://docs.python.org/3/library/sqlite3.html
# https://www.sqlitetutorial.net/sqlite-python/sqlite-python-select/

conn = sqlite3.connect('hr')


df_job_titles = pd.read_sql(
    "SELECT employees.first_name, jobs.job_title "
    + "FROM employees "
    + "INNER JOIN jobs ON employees.job_id "
    + "= jobs.job_id",
    conn,
)
# https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.read_sql.html

df_salary = pd.read_sql(
    "SELECT job_title, min_salary, max_salary FROM jobs", conn)
df_salary.drop(index=0, axis=0, inplace=True)
job_titles = df_job_titles.groupby("job_title").count().index


# Exercise 2
def ex2(jobs):
    job = df_job_titles
    if jobs == "All":
        count_job = job.groupby("job_title").count().reset_index()
        count_job.columns = ["Job Title", "Count"]
    else:
        job = job[job.job_title.isin(jobs)]
        count_job = job.groupby("job_title").count().reset_index()
        count_job.columns = ["Job Title", "Count"]

    fig = px.bar(count_job, x="Job Title", y="Count", color='Job Title')
    return fig


# Exercise 3
def ex3(min, max):
    df_salary_ex3 = df_salary
    df_salary_ex3["difference"] = df_salary_ex3["max_salary"] - \
        df_salary_ex3["min_salary"]
    difference = int(max) - int(min)
    df_salary_ex3 = df_salary_ex3[df_salary_ex3["difference"] <= difference]
    fig = px.bar(
        df_salary_ex3, x=df_salary_ex3.difference, y=df_salary_ex3.job_title, orientation="h"
    )
    fig["layout"]["yaxis"]["title"] = "Job Title"
    return fig

# Exercise 4
# # https://medium.com/analytics-vidhya/how-to-scrape-a-table-from-website-using-python-ce90d0cfb607


def scraping():
    url = 'https://www.itjobswatch.co.uk/jobs/uk/sqlite.do'
    page = requests.get(url)
    soup = BeautifulSoup(page.text, 'lxml')
    table1 = soup.find("table", attrs={'class': 'summary'})

    headers = []
    for i in table1.find_all('th'):
        title = i.text
        headers.append(title)

    headers.pop(0)
    headers[0] = "index"

    salaries = pd.read_sql("SELECT employees.salary " +
                           "FROM employees", conn)
    avg_salary = salaries['salary'].mean()

    data = pd.DataFrame(columns=headers)

    for j in table1.find_all('tr')[2:]:
        row_data = j.find_all('td')
        row = [i.text for i in row_data]
        length = len(data)
        data.loc[length] = row

    data.drop(index=[0, 1, 2, 3, 4, 5, 8, 9, 12, 13], axis=0, inplace=True)

    data['Same period 2021'] = data['Same period 2021'].str.replace('£', '')
    data['Same period 2021'] = data['Same period 2021'].str.replace(',', '')
    data['Same period 2021'] = data['Same period 2021'].str.replace(
        '-', '0').astype(float)
    data['6 months to19 Dec 2022'] = data['6 months to19 Dec 2022'].str.replace(
        '£', '')
    data['6 months to19 Dec 2022'] = data['6 months to19 Dec 2022'].str.replace(
        ',', '').astype(float)
    data['Same period 2020'] = data['Same period 2020'].str.replace('£', '')
    data['Same period 2020'] = data['Same period 2020'].str.replace(
        ',', '').astype(float)

    data.loc[4] = ['Average', avg_salary, avg_salary, avg_salary]
    return data


data = scraping()


def ex4(val):
    salary_frame = data[val]
    colors = ["#fdca40", "#fdca40", "#fdca40", "#fdca40", "black"]
    fig = px.scatter(
        x=data["index"], y=salary_frame, color=colors, color_discrete_map="identity", symbol= colors
    )
    fig.update_traces(marker_size=10)
    fig["layout"]["yaxis"]["title"] = "Salary"
    fig["layout"]["xaxis"]["title"] = "Percentiles"

    return fig


# Exercise 5
# Dashboard used the code from my previous dashboard
app = Dash(
    __name__,
    meta_tags=[
        {"name": "viewport", "content": "width=device-width, initial-scale=1.0"}
    ],
)
app.title = "Shanbe - Final Exam"
server = app.server
app.layout = html.Div(children=[
    html.Div(
        className="banner", children=[
            html.Div(className="container scalable", children=[
                html.H2(
                    id="banner-title",
                    children=[
                        html.A(
                            "HR",
                            style={
                                "text-decoration": "none",
                                "color": "inherit",
                            },
                        )
                    ],
                ),
                html.A(
                    id="banner-logo",
                    children=[
                        html.Img(
                            src=app.get_asset_url("logo.png"))
                    ]
                ),
            ],
            )
        ],
    ),
    html.Div(
        id="body",
        className="container scalable",
        children=[
            html.Div(
                id="app-container",
                children=[
                    html.Div(
                        id="left-column",
                        children=[
                            drc.Card(
                                children=[
                                    html.P("Job Filter"),
                                    dcc.Dropdown(
                                        id="job_filter",
                                        multi=True,
                                        options=job_titles,
                                        value="All",
                                    ),
                                ],
                            ),
                            drc.Card(
                                id="slider",
                                children=[
                                    html.P("Range Filter: Min to Max"),
                                    dcc.RangeSlider(0, 20000, 1000, value=[
                                                    0, 20000], id='slider1'),
                                ],
                            ),
                            drc.Card(
                                id="last-card",
                                children=[
                                    html.P("Year Filter"),
                                    dcc.Dropdown(
                                        options=scraping().columns[1:],
                                        value=scraping().columns[-1],
                                        id="years"
                                    ),
                                ],
                            ),
                        ]
                    ),
                    html.Div(
                        id="dgraphs",
                        children=[dcc.Graph(id="graph_1"),
                                  dcc.Graph(id="graph_2"),
                                  dcc.Graph(id="graph_3"),
                                  ],
                    ),
                ],
            )
        ],
    ),
]
)


@app.callback(
    [
        Output("graph_1", "figure"),
        Output("graph_2", "figure"),
        Output('graph_3', 'figure'),

    ],
    [
        Input("job_filter", "value"),
        Input("slider1", "value"),
        Input('years', 'value')

    ],
)
def update_output(jobs, slider, val):
    if jobs == None or len(jobs) == 0:
        jobs = "All"

    return ex2(jobs), ex3(slider[0], slider[1]), ex4(val)


if __name__ == "__main__":
    app.run_server("0.0.0.0", debug=False, port=int(
        os.environ.get("PORT", 8000)))


conn.close()
