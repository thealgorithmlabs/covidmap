create table community(id serial, name varchar, code varchar, shape geometry, population integer, PRIMARY KEY (id));

create table province(id serial, name varchar, code varchar, community integer,shape geometry, PRIMARY KEY(id),
FOREIGN KEY (community) REFERENCES community(id) ON DELETE CASCADE);

create table town(id serial, name varchar, province integer, shape geometry, PRIMARY KEY(id),
FOREIGN KEY (province) REFERENCES province(id) ON DELETE CASCADE);

create table town_area (id serial, zip varchar, name varchar, town integer, shape geometry, center geometry,
PRIMARY KEY (id), FOREIGN KEY (town) REFERENCES town(id) ON DELETE CASCADE );

create table restrictions (id serial, province integer, retrieval_date DATE DEFAULT CURRENT_DATE, restrictions json,
PRIMARY KEY (id), FOREIGN KEY (province) REFERENCES province(id) ON DELETE CASCADE);

create table community_statistics (id serial, community integer, source varchar, retrieval_date DATE DEFAULT CURRENT_DATE,
today_confirmed integer, today_deaths integer, today_recovered integer,
today_open_cases integer, today_new_confirmed integer, today_new_deaths integer,
today_new_open_cases integer, today_new_recovered integer,
PRIMARY KEY (id), FOREIGN KEY (community) REFERENCES community(id) ON DELETE CASCADE

create table province_statistics (id serial, province integer, source varchar, retrieval_date DATE DEFAULT CURRENT_DATE,
today_confirmed integer, today_deaths integer, today_recovered integer,
today_open_cases integer, today_new_confirmed integer, today_new_deaths integer,
today_new_open_cases integer, today_new_recovered integer,
PRIMARY KEY (id), FOREIGN KEY (province) REFERENCES province(id) ON DELETE CASCADE);

create table town_statistics(id serial, town integer, retrieval_date DATE DEFAULT CURRENT_DATE, source varchar,
pob_2019 integer, fecha_act varchar, total_casos integer, casos_ult_14dias integer, ia_total float,
ia_ult_14dias float, porc_ult14 float, PRIMARY KEY(id), FOREIGN KEY (town) REFERENCES town(id) ON DELETE CASCADE);

create table social_place (id serial, town_area integer, name varchar, surface integer,
activity varchar, source varchar, PRIMARY KEY (id), FOREIGN KEY(town_area) REFERENCES town_area(id) ON DELETE CASCADE);

create table query (id serial, town_area integer, location geometry, ip varchar, query_date DATE DEFAULT CURRENT_DATE,
os varchar, PRIMARY KEY (id), FOREIGN KEY (town_area) REFERENCES town_area(id) ON DELETE CASCADE);