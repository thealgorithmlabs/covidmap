import json
import datetime
import requests
import scrapy
import pymongo
import time

dbclient = pymongo.MongoClient("mongodb://localhost:27017/")
covid_db = dbclient["covid_data"]
covid_historic = covid_db["covid_historic"]
covid_spain = covid_db["covid_spain"]
covid_germany = covid_db["covid_germany"]
covid_france = covid_db["covid_france"]
covid_italy = covid_db["covid_italy"]
covid_china = covid_db["covid_china"]
covid_usa = covid_db["covid_usa"]


restrictions_provinces = covid_db["restrictions_provinces"]

dt = datetime.datetime.today().strftime('%Y-%m-%d')
x = covid_historic.find_one(sort=[( 'date', pymongo.DESCENDING )])

last_date = x["date"]



def get_covid_data_historic(dst):
    print(dst)
    dt = datetime.datetime.today().strftime('%Y-%m-%d')
    url="https://api.covid19tracking.narrativa.com/api?"+dst
    r = requests.get(url = url)
    cv_js=(r.json())
    dates = cv_js["dates"]

    for d in dates.keys():
        countries = (dates[d]["countries"].keys())
        today_confirmed = 0
        today_deaths = 0
        today_new_confirmed = 0
        today_new_deaths = 0
        today_new_open_cases = 0
        today_new_recovered = 0
        today_open_cases = 0
        today_recovered = 0

        spain_data = dates[d]["countries"]["Spain"]
        italy_data = dates[d]["countries"]["Italy"]
        germany_data = dates[d]["countries"]["Germany"]
        france_data = dates[d]["countries"]["France"]
        china_data = dates[d]["countries"]["China"]
        usa_data = dates[d]["countries"]["US"]

        x = covid_spain.insert_one(spain_data)
        print(x.inserted_id)

        x = covid_italy.insert_one(italy_data)
        print(x.inserted_id)

        x = covid_france.insert_one(france_data)
        print(x.inserted_id)

        x = covid_germany.insert_one(germany_data)
        print(x.inserted_id)

        x = covid_china.insert_one(china_data)
        print(x.inserted_id)

        x = covid_usa.insert_one(usa_data)
        print(x.inserted_id)
        for c in countries:
            country = dates[d]["countries"][c]
            today_confirmed += int(country["today_confirmed"])
            today_deaths += int(country["today_deaths"])
            today_new_confirmed += int(country["today_new_confirmed"])
            today_new_deaths += int(country["today_new_deaths"])
            today_new_open_cases += int(country["today_new_open_cases"])
            today_new_recovered += int(country["today_new_recovered"])
            today_open_cases += int(country["today_open_cases"])
            today_recovered += int(country["today_recovered"])
        
        obj_date = {
            "date":d,
            "today_confirmed":today_confirmed,
            "today_deaths":today_deaths,
            "today_new_confirmed":today_new_confirmed,
            "today_new_deaths":today_new_deaths,
            "today_new_open_cases":today_new_open_cases,
            "today_new_recovered":today_new_recovered,
            "today_open_cases":today_open_cases,
            "today_recovered":today_recovered
        }
        x = covid_historic.insert_one(obj_date)
        print(x.inserted_id)
    time.sleep(4)



def get_covid_data_today():
    narrativa_api_endpoint = "https://api.covid19tracking.narrativa.com/api/"
    dt = datetime.datetime.today().strftime('%Y-%m-%d')
    r = requests.get(url = narrativa_api_endpoint+dt)
    cv_js=(r.json())
    sp = cv_js["dates"][dt]["countries"]["Spain"]
    total = cv_js["total"]


def get_restrictions(postal="17740"):
    url = "https://quecovid.es/restricciones.php"
    headers = {
        "Content-Type":"application/x-www-form-urlencoded"
    }
    post_data = {"postal":postal,"buscarRestricciones":""}
    r = requests.post(url=url, headers=headers, data=post_data)
    rc = r.text

    get_cards = '//div[@class="container"]//div[@class="collapse"]//div[@class="card-body"]'
    res = scrapy.Selector(text=rc).xpath(get_cards).extract()
    #get_titles = '//button[@class="btn btn-link btn-block text-left collapsed"]//text()'
    #res = scrapy.Selector(text=rc).xpath(get_titles).extract()

    restrictions = {
        "cierre":[],
        "aforo":[],
        "horario":[],
        "movilidad":[],
        "otros":[]

    }

    for r in res:

        if "aforo" in r or "Afor" in r or "reunir" in r or "personas" in r or "%" in r:
            restrictions["aforo"].append(r.strip())
        
        elif "entrada" in r or "salida" in r or "cierre" in r or "Cierre" in r or "salir" in r or "entra" in r:
            restrictions["cierre"].append(r.strip())

        elif "horario" in r or "Hora" in r or "hora" in r or "desde" in r or "hasta" in r:
            restrictions["horario"].append(r.strip())
        
        elif "movilidad" in r or "Mov" in r:
            restrictions["movilidad"].append(r.strip())
        else:
            restrictions["otros"].append(r.strip())



    return restrictions


def update_restrictions_quecovid():
    cps = {'madrid': {'population': 3266126, 'cp': '28000'}, 
    'barcelona': {'population': 1636762, 'cp': '08012'}, 
    'valencia': {'population': 794288, 'cp': '46026'}, 
    'sevilla': {'population': 688592, 'cp': '41001'}, 
    'zaragoza': {'population': 674997, 'cp': '50018'}, 
    'malaga': {'population': 574654, 'cp': '29002'}, 
    'murcia': {'population': 453258, 'cp': '30001'}, 
    'palma': {'population': 416065, 'cp': '07012'}, 
    'las palmas de gran canaria': {'population': 379925, 'cp': '35229'}, 
    'bilbao': {'population': 346843, 'cp': '48015'}, 
    'alicante': {'population': 334887, 'cp': '03010'}, 
    'cordoba': {'population': 325701, 'cp': '14070'}, 
    'valladolid': {'population': 298412, 'cp': '47070'}, 
    'vitoria': {'population': 251774, 'cp': '01008'}, 
    'la coruña': {'population': 245711, 'cp': '15005'}, 
    'granada': {'population': 232462, 'cp': '18015'}, 
    'oviedo': {'population': 219686, 'cp': '33013'}, 
    'santa cruz de tenerife': {'population': 207312, 'cp': '38003'}, 
    'pamplona': {'population': 201653, 'cp': '31071'}, 
    'almeria': {'population': 198533, 'cp': '04009'}, 
    'san sebastian': {'population': 187415, 'cp': '20007'}, 
    'burgos': {'population': 175821, 'cp': '09007'}, 
    'albacete': {'population': 173329, 'cp': '02006'}, 
    'santander': {'population': 172539, 'cp': '39012'}, 
    'castellon de la plana': {'population': 171728, 'cp': '12003'}, 
    'logroño': {'population': 151136, 'cp': '26003'}, 
    'badajoz': {'population': 150702, 'cp': '06011'}, 
    'salamanca': {'population': 144228, 'cp': '37008'}, 
    'huelva': {'population': 143663, 'cp': '21007'}, 
    'lerida': {'population': 138956, 'cp': '25003'}, 
    'tarragona': {'population': 134515, 'cp': '43205'}, 
    'leon': {'population': 124303, 'cp': '24070'}, 
    'cadiz': {'population': 116027, 'cp': '11012'}, 
    'jaen': {'population': 112999, 'cp': '23009'}, 
    'orense': {'population': 105233, 'cp': '32003'}, 
    'gerona': {'population': 101852, 'cp': '17003'}, 
    'lugo': {'population': 98276, 'cp': '27004'}, 
    'caceres': {'population': 96126, 'cp': '10005'}, 
    'melilla': {'population': 86487, 'cp': '52006'}, 
    'guadalajara': {'population': 85871, 'cp': '19005'}, 
    'toledo': {'population': 84873, 'cp': '45008'}, 
    'ceuta': {'population': 84777, 'cp': '51080'}, 
    'pontevedra': {'population': 83029, 'cp': '36005'}, 
    'palencia': {'population': 78412, 'cp': '34005'}, 
    'ciudad real': {'population': 74746, 'cp': '13003'}, 
    'zamora': {'population': 61406, 'cp': '49032'}, 
    'avila': {'population': 57744, 'cp': '05005'}, 
    'cuenca': {'population': 54690, 'cp': '16004'}, 
    'huesca': {'population': 53132, 'cp': '22080'}, 
    'segovia': {'population': 51674, 'cp': '40006'}, 
    'soria': {'population': 39398, 'cp': '42005'}, 
    'teruel': {'population': 35890, 'cp': '44070'}}
    from geopy.geocoders import Nominatim
    geolocator = Nominatim(user_agent='myapplication')
    for k in cps.keys():
        cp = (cps[k]["cp"])
        location = geolocator.geocode(k)
        loc_box = (location.raw["boundingbox"])
        lat = (location.raw["lat"])
        lon = (location.raw["lon"])
        cp_restrictions = get_restrictions(postal=cp)
        
        cps[k]["restrictions"] = cp_restrictions
        cps[k]["box"] = loc_box
        cps[k]["lat"] = lat
        cps[k]["lon"] = lon
    dt = datetime.datetime.today().strftime('%Y-%m-%d')
    cps["date"] = dt
    x = restrictions_provinces.insert_one(cps)
    print(x.inserted_id)






"""
mar = "date_from=2020-03-14&date_to=2020-04-01"
get_covid_data_historic(mar)
mar = "date_from=2020-04-02&date_to=2020-04-14"
get_covid_data_historic(mar)
mar = "date_from=2020-04-15&date_to=2020-05-01"
get_covid_data_historic(mar)
mar = "date_from=2020-05-02&date_to=2020-05-14"
get_covid_data_historic(mar)
mar = "date_from=2020-05-15&date_to=2020-06-01"
get_covid_data_historic(mar)
mar = "date_from=2020-06-02&date_to=2020-06-14"
get_covid_data_historic(mar)
mar = "date_from=2020-06-15&date_to=2020-07-01"
get_covid_data_historic(mar)
mar = "date_from=2020-07-02&date_to=2020-07-14"
get_covid_data_historic(mar)
mar = "date_from=2020-07-15&date_to=2020-08-01"
get_covid_data_historic(mar)
mar = "date_from=2020-08-02&date_to=2020-08-14"
get_covid_data_historic(mar)
mar = "date_from=2020-08-15&date_to=2020-09-01"
get_covid_data_historic(mar)
mar = "date_from=2020-09-02&date_to=2020-09-14"
get_covid_data_historic(mar)
mar = "date_from=2020-09-15&date_to=2020-10-01"
get_covid_data_historic(mar)
mar = "date_from=2020-10-02&date_to=2020-10-14"
get_covid_data_historic(mar)
mar = "date_from=2020-10-15&date_to=2020-11-01"
get_covid_data_historic(mar)
mar = "date_from=2020-11-02&date_to=2020-11-14"
get_covid_data_historic(mar)
mar = "date_from=2020-11-15&date_to=2020-12-01"
get_covid_data_historic(mar)
"""




if last_date != dt:
    dst = "date_from="+last_date+"&date_to="+dt+""
    get_covid_data_historic(dst)

    update_restrictions_quecovid()



update_restrictions_quecovid()





import dash
import dash_html_components as html
import dash_leaflet as dl
import dash_leaflet.express as dlx
import geopy.distance
import json
from geopy.geocoders import Nominatim
import dash_bootstrap_components as dbc

geolocator = Nominatim(user_agent="dashboardcovid1111")
from dash.dependencies import Output, Input
from dash_extensions.javascript import Namespace, arrow_function
import geojson
import psycopg2
import psycopg2.extras

conn = psycopg2.connect(host="127.0.0.1",
                        port="5432",
                        user="cov",
                        password="cov",
                        database="covid_map")  # To remove slash

cursor = conn.cursor()
"""
create table community_statistics (id serial, community integer, source varchar, retrieval_date DATE DEFAULT CURRENT_DATE,
today_confirmed integer, today_deaths integer, today_recovered integer,
today_open_cases integer, today_new_confirmed integer, today_new_deaths integer,
today_new_open_cases integer, today_new_recovered integer,
PRIMARY KEY (id), FOREIGN KEY (community) REFERENCES community(id) ON DELETE CASCADE);
"""


def get_communities():
    q = "select community.id,st_asgeojson(community.shape), source, retrieval_date," \
        "today_confirmed, today_deaths, today_recovered, today_open_cases," \
        "today_new_confirmed, today_new_deaths, today_new_open_cases," \
        "today_new_recovered, community.name from community, community_statistics where " \
        "community_statistics.community = community.id"
    cursor.execute(q)
    c = cursor.fetchall()

    features = []

    for f in c:
        ff = {
            "type": "Feature",
            "geometry": json.loads(f[1]),
            "properties": {
                'id': f[0],
                'source': f[2],
                'RetrievalDate': f[3],
                'TodayConfirmed': f[4],
                'TodayDeaths': f[5],
                'TodayRecovered': f[6],
                'TodayOpenCases': f[7],
                'TodayNewConfirmed': f[8],
                'TodayNewDeaths': f[9],
                'TodayNewOpenCases': f[10],
                'TodayNewRecovered': f[11],
                'name': f[12]}
        }

        features.append(ff)

    collection_feats = {
        "type": "FeatureCollection",
        "features": features
    }
    return collection_feats


"""
create table restrictions (id serial, province integer, retrieval_date DATE DEFAULT CURRENT_DATE, restrictions json,
PRIMARY KEY (id), FOREIGN KEY (province) REFERENCES province(id) ON DELETE CASCADE);
"""


def get_provinces(community_id):
    q = "select province.id,st_asgeojson(province.shape), name,retrieval_date, restrictions from province,restrictions" \
        " where community=%s" % community_id
    cursor.execute(q)
    c = cursor.fetchall()

    features = []

    for f in c:
        ff = {"type": "Feature", "geometry": json.loads(f[1]), "properties": {'id': f[0],
             'name': f[2],
             'retrievaldate': f[3],
             'restrictions': f[4]}}

        features.append(ff)

    collection_feats = {
        "type": "FeatureCollection",
        "features": features
    }
    print(features)
    return collection_feats


def get_towns(town_id):
    q = "select id, st_asgeojson(shape) from town where province=%s" % town_id
    cursor.execute(q)
    c = cursor.fetchall()

    features = []

    for f in c:
        ff = {"type": "Feature", "geometry": json.loads(f[1]), "properties": {'id': f[0]}}

        features.append(ff)

    collection_feats = {
        "type": "FeatureCollection",
        "features": features
    }
    return collection_feats


colorscale = ['#FFEDA0', '#FED976', '#FEB24C', '#FD8D3C', '#FC4E2A', '#E31A1C', '#BD0026', '#800026']
classes = [0, 5, 10, 30, 60, 80, 200, 400]
style_map = dict(weight=2, opacity=1, color='white', dashArray='3', fillOpacity=0.2)

ns = Namespace("dlx", "choropleth")
geojson = dl.GeoJSON(data=get_communities(),  # url to geojson file
                     options=dict(style=ns("style")),  # how to style each polygon
                     zoomToBounds=True,  # when true, zooms to bounds when data changes (e.g. on load)
                     hoverStyle=arrow_function(dict(weight=5, color='red', dashArray='')),
                     # special style applied on hover
                     hideout=dict(colorscale=colorscale, classes=classes, style=style_map,
                                  colorProp="today_new_confirmed"),
                     id="geojson")

# The external stylesheet holds the location button icon.
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP,
                                                "https://maxcdn.bootstrapcdn.com/font-awesome/4.7.0/css/font-awesome.min.css"],
                prevent_initial_callbacks=True)
app.layout = html.Div([html.Div(id="community", children=""), html.Div(id="province", children=""),
                       dl.Map([dl.TileLayer(), dl.LayerGroup(id="provinces"), dl.LayerGroup(id="towns"), geojson,
                               dl.LocateControl(options={'locateOptions': {'enableHighAccuracy': True}})],
                              id="map", center=[40.91, -3.75],
                              style={'width': '100%', 'height': '100vh', 'margin': "auto", "display": "block",
                                     "float": "left"})
                       ])


@app.callback([Output("provinces", "children"),
               Output("community", "children")],
              [Input("geojson", "click_feature")])
def map_click_community(feature):
    if feature:
        community_id = int((feature["properties"]["id"]))
    else:
        community_id = None
    community_name = feature["properties"]["name"]
    provinces_community = get_provinces(community_id)
    provinces_layer = dl.GeoJSON(data=provinces_community,  # url to geojson file
                                 options=dict(style=ns("style")),  # how to style each polygon
                                 zoomToBounds=True,  # when true, zooms to bounds when data changes (e.g. on load)
                                 hoverStyle=arrow_function(dict(weight=5, color='red', dashArray='')),
                                 hideout=dict(colorscale=colorscale, classes=classes, style=style_map),
                                 id="provinces_data")

    rows = [
        html.Tr([html.Th(c, className='table-item') for c in feature["properties"].keys()]),
        html.Tr([html.Td(feature["properties"][c]) for c in feature["properties"].keys()]),
    ]

    table_body = [html.Tbody(rows)]
    table = dbc.Table(table_body, bordered=True,
                      dark=True,
                      hover=True,
                      responsive=True,
                      striped=True)
    table_container = html.Div(id='community_statistics', children=[dbc.Label(community_name), table])
    return provinces_layer, table_container


@app.callback([Output("towns", "children"),
               Output("province", "children")], [Input("provinces_data", "click_feature")])
def map_click_province(feature):
    if feature:
        province_id = int((feature["properties"]["id"]))
    else:
        province_id = 0
    towns_province = get_towns(province_id)
    geojson = dl.GeoJSON(data=towns_province)
    restrictions = []
    if feature:
        for r in feature["properties"]["restrictions"].keys():
            collapse = html.Div(
                [
                    dbc.Button(
                        r,
                        id="collapse-button",
                        className="mb-3",
                        color="primary",
                    ),
                    dbc.Collapse(
                        dbc.Card(dbc.CardBody(feature["properties"]["restrictions"][r])),
                        id="collapse",
                    ),
                ]
            )
            restrictions.append(collapse)

    return geojson, ""


@app.callback(Output("text", "children"), [Input("map", "location_lat_lon_acc")])
def update_location(location):
    return "You are within {} meters of (lat,lon) = ({},{})".format(location[2], location[0], location[1])


if __name__ == '__main__':
    app.run_server()
