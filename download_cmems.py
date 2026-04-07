#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script pour télécharger les données GLORYS12 à l'aide de l'API copernicusmarine.
Créer un compte sur: 
                        https://data.marine.copernicus.eu/products

il est recommandé de créer un env. python dédié et ensuite d'y installer la librairie
        conda create -n cmems && conda activate cmems
        pip install copernicusmarine
"""

# Importations nécessaires
from datetime import datetime, timedelta
import copernicusmarine  
import warnings
warnings.filterwarnings('ignore')


# cas 1: Définir vos identifiants 
username = "xxxxxxxx"
password = "xxxxxxxx"

"""
# cas 2: considérez l'utilisation de variables d'environnement pour la sécurité
# dans votre .bashrc ajouter les deux lignes suivantes:
#           export COPERNICUSMARINE_SERVICE_USERNAME=identifiant
#           export COPERNICUSMARINE_SERVICE_PASSWORD=mot_de_passe
"""



# Définir les dates de début et de fin pour l'année de votre choix
start_date = datetime(2020, 1, 1)
end_date = datetime(2020, 6, 30)

# Définir les variables à télécharger
variables = ["uo","vo", "thetao", "so"] #, "mlotst", "zos"]

# Boucle à travers chaque pour la période choisie
current_date = start_date
while current_date <= end_date:
    # Formatage de la date de début pour le jour courant
    start_datetime = current_date.strftime("%Y-%m-%d")
    
    # Construire le nom du fichier de sortie basé sur la date actuelle
    output_filename = f"GG_cmems_data_{current_date.strftime('%Y%m%d')}.nc"
    
    try:
        # Appeler la fonction de sous-ensemble pour télécharger les variables spécifiées
        copernicusmarine.subset(
            dataset_id="cmems_mod_glo_phy_my_0.083deg_P1D-m", 
            # nom du produit téléchargé (voir: https://data.marine.copernicus.eu/product/GLOBAL_ANALYSISFORECAST_PHY_001_024/services)
            variables=variables,
            # limites géographiques du domaine
            minimum_longitude=-10.0,
            maximum_longitude=12.0,
            minimum_latitude=7,
            maximum_latitude=-6,
            #
            start_datetime=start_datetime,
            end_datetime=start_datetime,  # Utilisez la même date ici
            minimum_depth=0,
            maximum_depth=500, # profondeur maximale jusquà 5700m
            output_filename=output_filename,
            output_directory="/home/data_copernicus/",
            # supprimer les deux lignes ci-dessous pour cas 2, cf. L25
            username=username,
            password=password
        )
        print(f"\nTéléchargement des données pour {start_datetime} réussi.\n")
    except Exception as e:
        print(f"\nÉchec du téléchargement des données pour {start_datetime} : {e}\n")
    
    # Incrémenter la date courante d'un jour
    current_date += timedelta(days=1)

print("\nTous les téléchargements sont terminés !\n")