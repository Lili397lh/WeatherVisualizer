import requests
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

def stations_inventory():
    url = "https://opendata.aemet.es/opendata/api/valores/climatologicos/inventarioestaciones/todasestaciones/"

    querystring = {"api_key":"eyJhbGciOiJIUzI1NiJ9.eyJzdWIiOiJsaWxpYW5hODRsQGhvdG1haWwuY29tIiwianRpIjoiOWY0OTk0ZWUtMTE4Ny00OTU1LWEyYzctYTIzZTBlYmVlM2I0IiwiaXNzIjoiQUVNRVQiLCJpYXQiOjE3NjU5Nzg2MDMsInVzZXJJZCI6IjlmNDk5NGVlLTExODctNDk1NS1hMmM3LWEyM2UwZWJlZTNiNCIsInJvbGUiOiIifQ.va-U-NR29pk8l1qqPcK0rrTxJCVC82piyBBA1auTM2U"}

    headers = {
        'cache-control': "no-cache"
        }

    response = requests.request("GET", url, headers=headers, params=querystring)
    response_json = response.json()

    # Obtain URL
    data_url = response_json["datos"]

    # Get data from URL
    response_data = requests.get(data_url)
    data = response_data.json()
    inventorydf = pd.DataFrame(data)
    names = inventorydf[['indicativo', 'nombre']]

    return names

selected_station = None
def store_selected_station(station):
    global selected_station
    selected_station = station
    return selected_station

def station_met_data():
    global selected_station
    station = selected_station
    url = "https://opendata.aemet.es/opendata/api/observacion/convencional/datos/estacion/" + station + "/"
    
    querystring = {"api_key":"eyJhbGciOiJIUzI1NiJ9.eyJzdWIiOiJsaWxpYW5hODRsQGhvdG1haWwuY29tIiwianRpIjoiOWY0OTk0ZWUtMTE4Ny00OTU1LWEyYzctYTIzZTBlYmVlM2I0IiwiaXNzIjoiQUVNRVQiLCJpYXQiOjE3NjU5Nzg2MDMsInVzZXJJZCI6IjlmNDk5NGVlLTExODctNDk1NS1hMmM3LWEyM2UwZWJlZTNiNCIsInJvbGUiOiIifQ.va-U-NR29pk8l1qqPcK0rrTxJCVC82piyBBA1auTM2U"}

    headers = {
        'cache-control': "no-cache"
        }

    response = requests.request("GET", url, headers=headers, params=querystring)
    response_json = response.json()

    # Obtain URL
    data_url = response_json["datos"]

    # Get data from URL
    response_data = requests.get(data_url)
    data = response_data.json()
    meteodatadf = pd.DataFrame(data)

    # Datetime
    meteodatadf['datetime'] = pd.to_datetime(meteodatadf['fint'].str[:-5].str.replace('T', ' '))
    
    return meteodatadf

def wind_rose():
    global selected_station
    station = station_met_data()
    if 'dv' not in station.columns:
        raise ValueError("La columna 'dv' no existe en los datos de la estación.")
    
    # 16 sectors creation centered in 0º
    def get_sector(direction):
        if pd.isna(direction):
            return None
        # Sector calculation
        direction = direction % 360
        sector_index = ((direction + 11.25) // 22.5) % 16
        # Sector center
        sector_center = sector_index * 22.5
        return sector_center
    
    station['sector'] = station['dv'].apply(get_sector)

    sectors = [i * 22.5 for i in range(16)]
    frecuencia = station['sector'].value_counts().reindex(sectors, fill_value=0).values
    wind_rose_df = pd.DataFrame({'sectors': sectors, 'frecuencia': frecuencia})
    
    return wind_rose_df