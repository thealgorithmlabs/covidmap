from pymongo import MongoClient
from dash.dependencies import Input, Output, State
import dash
import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objs as go 
import numpy as np 
import requests, json
import pandas as pd
import service
import base64

client = MongoClient()
db = client.covid_data
collection = db.covid_historic

collection_spain = db.covid_spain
collection_italy = db.covid_italy
collection_france = db.covid_france
collection_germany = db.covid_germany
collection_china = db.covid_china
collection_usa = db.covid_usa



data = pd.DataFrame(list(collection.find()))

data_spain = pd.DataFrame(list(collection_spain.find()))
data_italy = pd.DataFrame(list(collection_italy.find()))
data_france = pd.DataFrame(list(collection_france.find()))
data_germany = pd.DataFrame(list(collection_germany.find()))
data_china = pd.DataFrame(list(collection_china.find()))
data_usa = pd.DataFrame(list(collection_usa.find()))

total_deaths_sp = (data_spain["today_new_confirmed"].sum()/46940000) * 100
total_deaths_it = (data_italy["today_new_confirmed"].sum()/60360000) * 100
total_deaths_fr = (data_france["today_new_confirmed"].sum()/66990000) * 100
total_deaths_ge = (data_germany["today_new_confirmed"].sum()/83020000) * 100
total_deaths_ch = (data_china["today_new_confirmed"].sum()/ 1400000000) * 100
total_deaths_us = (data_usa["today_new_confirmed"].sum()/328200000) * 100

countries = ["Spain", "Italy", "France", "Germany", "China", "USA"]
death_avgs = [total_deaths_sp, total_deaths_it, total_deaths_fr, total_deaths_ge, total_deaths_ch, total_deaths_us]


numeric_vals = html.Div([
    html.Div(id="numeric_deaths_total",children="Total amount of deaths worldwide: "+str(data["today_new_deaths"].sum())),
    html.Div(id="numeric_deaths_today",children="Total amount of deaths worldwide, today: "+str(data["today_new_deaths"].iloc[-1])),
    html.Div(id="numeric_cases_spain",children="Total amount of cases in Spain: "+str(data_spain["today_new_confirmed"].sum())),
    html.Div(id="numeric_cases_spain_today",children="Total amount of cases in Spain today: "+str(data["today_new_confirmed"].iloc[-1])),

])
print(total_deaths_sp)


print(data_spain.head())

print(data.columns)

app = dash.Dash()




historic_death = html.Div([
    dcc.Graph(id='historic_deaths', 
        figure = {'data': [
            go.Line(
            x=data['date'],
            y=data['today_confirmed'], name="Cases accumulated", line=dict(color='green')  ),
            go.Line(
            x=data['date'],
            y=data['today_recovered'], name="Recovered cases accumulated", line=dict(color='pink')  ),
            go.Line(
            x=data['date'],
            y=data['today_deaths'], name="Deaths accumulated", line=dict(color='black'))
            ],
    'layout':go.Layout(title='covid19 deaths evolution (world-wide)')
    }
    )
])


historic_cases_day = html.Div([
    dcc.Graph(id='cases_xday', 
        figure = {'data': [
            go.Line(
            x=data['date'],
            y=data['today_new_confirmed'], name="Cases per day", line=dict(color='green')  ),
            go.Line(
            x=data['date'],
            y=data['today_new_deaths'], name="Deaths per day", line=dict(color='black')  )
            
            ],
    'layout':go.Layout(title='cases per day evolution (worldwide)')
    }
    )
])

deaths_per_day = html.Div([
    dcc.Graph(id='deaths_per_day', 
        figure = {'data': [
            go.Line(
            x=data['date'],
            y=data['today_new_deaths'], name="Deaths per day", line=dict(color='black')  )
            
            ],
    'layout':go.Layout(title='Deaths per day evolution (worldwide)')
    }
    )
])

uci_spain = html.Div([
    dcc.Graph(id='uci_spain', 
        figure = {'data': [
            go.Line(
            x=data_spain['date'],
            y=data_spain['today_new_deaths'], name="Deaths per day, Spain", line=dict(color='red')  ),
            go.Line(
            x=data_italy['date'],
            y=data_italy['today_new_deaths'], name="Deaths per day, Italy", line=dict(color='blue')  ),
            go.Line(
            x=data_france['date'],
            y=data_france['today_new_deaths'], name="Deaths per day, France", line=dict(color='pink')  ),
            go.Line(
            x=data_germany['date'],
            y=data_germany['today_new_deaths'], name="Deaths per day, Germany", line=dict(color='black')  )
            
            ],
    'layout':go.Layout(title='Deaths per day Europe')
    }
    )
])


bars_deaths = html.Div([
    dcc.Graph(id='bars_deaths', 
        figure = {'data': [
            go.Bar(
            x=countries,
            y=death_avgs,
            marker=dict(color=['red','blue','pink','black','yellow','cyan']))
            
            ],
    'layout':go.Layout(title='Total percentage of population infected')
    }
    )
])
dates = data_spain["date"].unique()

initial_img = base64.b64encode(open("choropleths/choropleth_deaths_2020-03-14.png", 'rb').read()).decode('ascii')
choropleth_map_deaths = html.Div([
    
    html.Div(id='choropleth_div',children=html.Img(src='data:image/png;base64,{}'.format(initial_img))),
    html.Hr(),
    dcc.Slider(
        id='map-slider',
        min=0,
        max=len(dates),
        step=1,
        value=0,
    )
    ])
@app.callback(
    dash.dependencies.Output('choropleth_div', 'children'),
    [dash.dependencies.Input('map-slider', 'value')])
def update_output(value):
    map_img = base64.b64encode(open("choropleths/choropleth_deaths_"+dates[value]+".png", 'rb').read()).decode('ascii')
    return html.Img(src='data:image/png;base64,{}'.format(map_img))




app.layout = html.Div([
    html.Div(id='numerics',children=numeric_vals, style={'width':'500px', 'float':'left'}),
    html.Div(id='deaths',children=historic_death, style={'width':'500px', 'float':'left'}),
    html.Div(id='cases_day',children=historic_cases_day, style={'width':'500px', 'float':'left'}),
    html.Div(id='deaths_day',children=deaths_per_day, style={'width':'500px', 'float':'left'}),
    html.Div(id='intensive_spain',children=uci_spain, style={'width':'800px', 'float':'left'}),
    html.Div(id='bars_deaths_total',children=bars_deaths, style={'width':'500px', 'float':'left'}),
    html.Div(id='choropleth_deaths',children=choropleth_map_deaths, style={ 'float':'left'})
    
])




if __name__ == '__main__':
    app.run_server()