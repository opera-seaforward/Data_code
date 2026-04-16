from datetime import datetime, timedelta
import os, sys, warnings, copernicusmarine, cdsapi
from dotenv import load_dotenv

warnings.filterwarnings('ignore')


def download_era5( dataset, variables, year, area, output_dir ):
    
    os.makedirs(output_dir, exist_ok=True)
    
    # paramètres de la requête
    # Après cette ligne vous pouvez ajouter une boucle for pour itérer sur les années: L39
    request_base = {
        "product_type": ["reanalysis"],
        "variable": variables,
        "year": year, # préciser l'année d'intérêt
        "time": [
            "00:00", "01:00", "02:00", "03:00", "04:00", "05:00",
            "06:00", "07:00", "08:00", "09:00", "10:00", "11:00",
            "12:00", "13:00", "14:00", "15:00", "16:00", "17:00",
            "18:00", "19:00", "20:00", "21:00", "22:00", "23:00"
        ],
        "data_format": "netcdf", # formats disponibles: netcdf, grib
        "download_format": "zip",
        "area": area   # limites du domaine: nord, ouest, sud, est
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

def download_glorys12(
    dataset,
    start_date,
    end_date,
    variables,
    longitudes,
    latitudes,
    depth,
    output_directory,
    username,
    password 
):

    # Boucle à travers chaque pour la période choisie
    current_date = datetime.strptime(start_date, "%Y-%m-%d")
    end_date = datetime.strptime(end_date,"%Y-%m-%d")
    while current_date <= end_date:
        # Formatage de la date de début pour le jour courant
        start_datetime = current_date.strftime("%Y-%m-%d")
        
        # Construire le nom du fichier de sortie basé sur la date actuelle
        output_filename = f"GG_cmems_data_{current_date.strftime('%Y%m%d')}.nc"
        
        try:
            # Appeler la fonction de sous-ensemble pour télécharger les variables spécifiées
            copernicusmarine.subset(
                dataset_id= dataset, 
                # nom du produit téléchargé (voir: https://data.marine.copernicus.eu/product/GLOBAL_ANALYSISFORECAST_PHY_001_024/services)
                variables=variables,
                # limites géographiques du domaine
                minimum_longitude=longitudes[0],
                maximum_longitude=longitudes[1],
                minimum_latitude=latitudes[0],
                maximum_latitude=latitudes[1],
                #
                start_datetime=start_datetime,
                end_datetime=start_datetime,  # Utilisez la même date ici
                minimum_depth=depth[0],
                maximum_depth=depth[1], # profondeur maximale jusquà 5700m
                output_filename=output_filename,
                output_directory=output_directory,
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

def main():
    
    load_dotenv()
        
    if len(sys.argv) == 1:
        # si aucun argument, alors on recherche les variable dans le fichier .env
        try:
            dataset = os.getenv("DATASET")
        except Exception as e:
            print(" Vous devez definir le dataset dans votre fichier .env")
        
        if 'era5' in dataset:
            try:
                variable = os.getenv("VARIABLE_ERA5").split(",")
                year = os.getenv("YEAR").split(",")
                area = [float(x) for x in os.getenv("AREA").split(",")]
                output_dir = os.getenv("OUTPUT_DIR")
                download_era5(dataset,variable,year,area,output_dir)
            except Exception as e:
                print(" Erreur : configurez correctement votre fichier .env")
                print("Vous devez définir : VARIABLE, YEAR, AREA et OUTPUT_DIR")
                print("Consultez la documentation pour plus de détails.")
                # print(f"Détails techniques : {e}")
           
            
        elif 'cmems' in dataset:
            
            try:
                variables = os.getenv("VARIABLE_GLORYS12").split(",")
                longitudes = [float(x) for x in os.getenv("LONGITUDE").split(",")]
                latitudes = [float(x) for x in os.getenv("LATITUDE").split(",")]
                start_date = os.getenv("START_DATE")
                end_date =os.getenv("END_DATE")
                end_date = end_date
                depth = [float(x) for x in os.getenv("DEPTH").split(",")]
                username = os.getenv("USERNAME_CMEMS")
                password = os.getenv("PASSWORD_CMENS")
                output_directory = os.getenv("OUTPUT_DIRECTORY")
                print(username)
                download_glorys12(
                    dataset,
                    start_date,
                    end_date,
                    variables,
                    longitudes,
                    latitudes,
                    depth,
                    output_directory,
                    username,
                    password 
                )
            except Exception as e:
                print(" Erreur : configurez correctement votre fichier .env")
                print("Vous devez définir : VARIABLE, logitude, latitude, start date, end date, depth, username, password and output_dir")
                print("Consultez la documentation pour plus de détails.")
                print(f"Détails techniques : {e}")
            
        else:
            
            print("we take into account only era5 or glorys12 data")
            sys.exit(1)
        
    else:
        dataset = sys.argv[1]

        
        if 'era5' in dataset:
            if len(sys.argv) < 6:
                print("Usage: python download_era5.py <dataset> <variable> <year> <area> <output_dir>")
                sys.exit(1)
            variable_arg = sys.argv[2]
            variable = variable_arg.split(",")
            year = sys.argv[3].split(",")
            area_arg = sys.argv[4] 
            area = [float(x) for x in area_arg.split(",")]
            output_dir = sys.argv[5]  
              
            download_era5(dataset,variable,year,area,output_dir)
            
        elif 'cmems' in dataset:
            if len(sys.argv) < 11:
                print("Usage: python download_glorys12.py <dataset> <variable> <longitudes> <latitudes> <start_date> <end_date> <depth> <username> <password> <output_directory>")
                sys.exit(1)
            variables = sys.argv[2].split(",")
            longitudes = [float(x) for x in sys.argv[3]]
            latitudes = [float(x) for x in sys.argv[4]]
            start_date = sys.argv[5]
            end_date = sys.argv[6]
            depth = [float(x) for x in sys.argv[7]]
            username="ikamga"
            password="Ines@24/1999"
            output_directory="data_copernicus"
            
            download_glorys12(
                dataset,
                start_date,
                end_date,
                variables,
                longitudes,
                latitudes,
                depth,
                output_directory,
                username,
                password 
            )
            
        else:
            
            print("we take into account only era5 or glorys12 data")
            sys.exit(1)



if __name__ == "__main__":
    main()