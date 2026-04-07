#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Script pour télécharger les données ERA5 à l'aide de l'API CDS.

Assurez-vous d'avoir un compte sur le site de Copernicus 
            https://cds.climate.copernicus.eu/datasets/reanalysis-era5-single-levels?tab=download

Configurez votre clé d'API avant d'exécuter ce script:
        dans votre home, créer le fichier nommé .cdsapirc 
        il doit contenir les deux lignes suivantes
            url: https://cds.climate.copernicus.eu/api
            key: votre_token_disponible_dans_votre_compte

"""

import cdsapi
import os

# config
output_dir = "." #"data/era5"   # 
os.makedirs(output_dir, exist_ok=True)

dataset = "reanalysis-era5-single-levels"  # nom du dataset choisi, il en 
                                           # existe des dizaines sur ERA5
# paramètres de la requête
# Après cette ligne vous pouvez ajouter une boucle for pour itérer sur les années: L39
request_base = {
    "product_type": ["reanalysis"],
    "variable": [ # lister les variables d'intérêt tel que labelisé sur le site d'ERA5
        "10m_u_component_of_wind",
        "10m_v_component_of_wind",
        "total_precipitation",
        "surface_net_solar_radiation",
        "surface_net_thermal_radiation",
        "evaporation"
    ],
    "year": ["2010"], # préciser l'année d'intérêt
    "time": [
        "00:00", "01:00", "02:00", "03:00", "04:00", "05:00",
        "06:00", "07:00", "08:00", "09:00", "10:00", "11:00",
        "12:00", "13:00", "14:00", "15:00", "16:00", "17:00",
        "18:00", "19:00", "20:00", "21:00", "22:00", "23:00"
    ],
    "data_format": "netcdf", # formats disponibles: netcdf, grib
    "download_format": "zip",
    "area": [10, 3, -7, 15]   # limites du domaine: nord, ouest, sud, est
}

# jours dans chaque mois (année ordinaire, changer Février si année bissextile)
year = "no_leap"  # "leap"
if year == "no_leap":
    days_in_month = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
else:
    days_in_month = [31, 29, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]

client = cdsapi.Client()

# ici on télécharge les données par lot mensuel
# chaque fichier téléchargé contient pour chaque jour les données horaires cf. L40-44
for month in range(1, 13):
    # construire la liste des jours pour chaque mois
    days = [f"{day:02d}" for day in range(1, days_in_month[month-1] + 1)]

    request = request_base.copy()
    request["month"] = [f"{month:02d}"]
    request["day"] = days

    # format du fichier de sortie : era5_YYYYMM.nc
    filename = f"era5_{request['year'][0]}{request['month'][0]}.nc"
    filepath = os.path.join(output_dir, filename)

    print(f"Downloading {filepath} ...")
    client.retrieve(dataset, request).download(filepath)
    print(f"Saved to {filepath}")

    
