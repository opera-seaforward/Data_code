# Data_code

Script Python pour telecharger des donnees ERA5 et CMEMS/GLORYS12.

Le script principal est: download_data.py

## Guide d'utilisation

Suivez ces etapes dans cet ordre pour eviter les erreurs d'acces API.

### Etape 1 - Creer les comptes sur les plateformes

1. Creer un compte Copernicus Climate Data Store (pour ERA5).
2. Creer un compte Copernicus Marine (pour CMEMS/GLORYS12).

### Etape 2 - Configurer les acces API / cles

#### ERA5 (CDS)

1. Recuperer votre token API depuis votre compte CDS.
2. Creer le fichier `$HOME/.cdsapirc` avec ce contenu:

	url: https://cds.climate.copernicus.eu/api
	key: votre_token_disponible_dans_votre_compte

#### CMEMS

1. Recuperer vos identifiants Copernicus Marine.
2. Vous pourrez soit:
	- les passer en arguments `--username` et `--password`,
	- soit les definir dans le fichier `.env`.
NB : si vous ne définissez pas vos identifiants, vous serez amené à les saisir manuellement lors du lancement du téléchargement du dataset.

### Etape 3 - Accepter les licences ERA5 (obligatoire)

Avant le premier telechargement ERA5, allez sur la page du jeu de donnees que vous voulez utiliser (ex: `reanalysis-era5-single-levels`) et acceptez les licences/conditions d'utilisation.

Si cette etape n'est pas faite, les requetes API peuvent echouer meme si la cle est correcte.

### Etape 4 - Creer l'environnement virtuel

1. Se placer dans le dossier du projet:

	cd /chemin/vers/projet

2. Creer et activer l'environnement Python:

	python3 -m venv .venv
	source .venv/bin/activate

### Etape 5 - Installer les dependances

	pip install --upgrade pip
	pip install -r requirements.txt

### Etape 6 - Configurer `.env`

Creer `.env` depuis le modele qui correspond a votre cas.

Cas ERA5:

	cp .env.era5.example .env

Cas CMEMS:

	cp .env.cmems.example .env

Puis modifier `.env` avec vos valeurs.

### Etape 7 - Lancer le script

Execution via `.env`:

	python3 download_data.py

## Utilisation en ligne de commande (sans .env)

### Exemple ERA5

python3 download_data.py era5 \
	--dataset reanalysis-era5-single-levels \
	--variables "10m_u_component_of_wind,10m_v_component_of_wind" \
	--years "2020,2021" \
	--area "10,3,-7,15" \
	--output-dir ./data_era5

### Exemple CMEMS / GLORYS12

python3 download_data.py cmems \
	--dataset cmems_mod_glo_phy_anfc_0.083deg_P1D-m \
	--variables "uo,vo,thetao,so" \
	--longitudes "-10,12" \
	--latitudes "-6,7" \
	--start-date 2020-01-01 \
	--end-date 2020-01-03 \
	--depth "0,500" \
	--output-dir ./data_copernicus \
	--username "votre_user" \
	--password "votre_password"

## Parametres attendus dans .env

Vous pouvez utiliser les variables suivantes:

- DATA_SOURCE=era5 ou DATA_SOURCE=cmems

ERA5:
- ERA5_DATASET
- ERA5_VARIABLES
- ERA5_YEARS
- ERA5_AREA
- ERA5_OUTPUT_DIR

CMEMS:
- CMEMS_DATASET
- CMEMS_VARIABLES
- CMEMS_LONGITUDES
- CMEMS_LATITUDES
- CMEMS_START_DATE
- CMEMS_END_DATE
- CMEMS_DEPTH
- CMEMS_OUTPUT_DIR
- CMEMS_USERNAME
- CMEMS_PASSWORD

Des exemples sont fournis dans:
- .env.era5.example
- .env.cmems.example
- .env.example (version combinee des deux cas)

## Aide

Afficher l'aide generale:

python3 download_data.py --help

Afficher l'aide d'une source:

python3 download_data.py era5 --help
python3 download_data.py cmems --help