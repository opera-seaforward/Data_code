from __future__ import annotations

import argparse
import calendar
import os
import warnings
from datetime import datetime, timedelta
from typing import Optional

from dotenv import load_dotenv

warnings.filterwarnings("ignore")


def _split_csv(value: str) -> list[str]:
    return [item.strip() for item in value.split(",") if item.strip()]


def _parse_float_csv(value: str, expected_len: Optional[int] = None) -> list[float]:
    values = [float(item.strip()) for item in value.split(",") if item.strip()]
    if expected_len is not None and len(values) != expected_len:
        raise ValueError(f"Valeur invalide: attendu {expected_len} nombres, obtenu {len(values)}")
    return values


def _env(name: str, fallback: Optional[str] = None, required: bool = False) -> Optional[str]:
    value = os.getenv(name)
    if value is None:
        value = fallback
    if required and (value is None or value.strip() == ""):
        raise ValueError(f"Variable d'environnement manquante: {name}")
    return value


def download_era5(dataset: str, variables: list[str], years: list[str], area: list[float], output_dir: str) -> None:
    try:
        import cdsapi
    except ImportError as exc:
        raise RuntimeError("Le package 'cdsapi' est requis. Installez-le avec: pip install cdsapi") from exc

    cdsapirc_path = os.path.expanduser("~/.cdsapirc")
    if not os.path.isfile(cdsapirc_path):
        raise RuntimeError(
            "Configuration CDS manquante. Creez le fichier "
            f"{cdsapirc_path} avec:\n"
            "url: https://cds.climate.copernicus.eu/api\n"
            "key: votre_token_disponible_dans_votre_compte"
        )

    os.makedirs(output_dir, exist_ok=True)

    request_base = {
        "product_type": ["reanalysis"],
        "variable": variables,
        "time": [
            "00:00", "01:00", "02:00", "03:00", "04:00", "05:00",
            "06:00", "07:00", "08:00", "09:00", "10:00", "11:00",
            "12:00", "13:00", "14:00", "15:00", "16:00", "17:00",
            "18:00", "19:00", "20:00", "21:00", "22:00", "23:00",
        ],
        "data_format": "netcdf",
        "download_format": "zip",
        "area": area,
    }

    client = cdsapi.Client()

    for year in years:
        year_int = int(year)
        for month in range(1, 13):
            num_days = calendar.monthrange(year_int, month)[1]
            days = [f"{day:02d}" for day in range(1, num_days + 1)]

            request = request_base.copy()
            request["year"] = [str(year_int)]
            request["month"] = [f"{month:02d}"]
            request["day"] = days

            filename = f"era5_{year_int}{month:02d}.nc"
            filepath = os.path.join(output_dir, filename)

            print(f"[ERA5] Download: {filepath}")
            client.retrieve(dataset, request).download(filepath)
            print(f"[ERA5] OK: {filepath}")


def download_cmems(
    dataset: str,
    start_date: str,
    end_date: str,
    variables: list[str],
    longitudes: list[float],
    latitudes: list[float],
    depth: list[float],
    output_directory: str,
    username: Optional[str] = None,
    password: Optional[str] = None,
) -> None:
    try:
        import copernicusmarine
    except ImportError as exc:
        raise RuntimeError(
            "Le package 'copernicusmarine' est requis. Installez-le avec: pip install copernicusmarine"
        ) from exc

    os.makedirs(output_directory, exist_ok=True)
    current_date = datetime.strptime(start_date, "%Y-%m-%d")
    last_date = datetime.strptime(end_date, "%Y-%m-%d")

    while current_date <= last_date:
        day_str = current_date.strftime("%Y-%m-%d")
        output_filename = f"cmems_{current_date.strftime('%Y%m%d')}.nc"

        kwargs = {
            "dataset_id": dataset,
            "variables": variables,
            "minimum_longitude": longitudes[0],
            "maximum_longitude": longitudes[1],
            "minimum_latitude": latitudes[0],
            "maximum_latitude": latitudes[1],
            "start_datetime": day_str,
            "end_datetime": day_str,
            "minimum_depth": depth[0],
            "maximum_depth": depth[1],
            "output_filename": output_filename,
            "output_directory": output_directory,
        }

        # If credentials are omitted, copernicusmarine can use environment variables.
        if username and password:
            kwargs["username"] = username
            kwargs["password"] = password

        try:
            print(f"[CMEMS] Download: {output_filename}")
            copernicusmarine.subset(**kwargs)
            print(f"[CMEMS] OK: {output_filename}")
        except KeyboardInterrupt:
            print("[CMEMS] Interrompu par l'utilisateur.")
            break
        except Exception as exc:  # pragma: no cover - network/API dependent
            print(f"[CMEMS] Erreur pour {day_str}: {exc}")

        current_date += timedelta(days=1)


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Téléchargement ERA5 et CMEMS avec paramètres CLI ou .env"
    )
    parser.add_argument(
        "--env-file",
        default=".env",
        help="Chemin du fichier .env (défaut: .env)",
    )

    subparsers = parser.add_subparsers(dest="source")

    era5 = subparsers.add_parser("era5", help="Télécharger des données ERA5")
    era5.add_argument("--dataset", required=True, help="Ex: reanalysis-era5-single-levels")
    era5.add_argument("--variables", required=True, help="Variables CSV")
    era5.add_argument("--years", required=True, help="Années CSV, ex: 2020,2021")
    era5.add_argument("--area", required=True, help="Nord,Ouest,Sud,Est")
    era5.add_argument("--output-dir", required=True, help="Dossier de sortie")

    cmems = subparsers.add_parser("cmems", help="Télécharger des données CMEMS/GLORYS12")
    cmems.add_argument("--dataset", required=True, help="Ex: cmems_mod_glo_phy_anfc_0.083deg_P1D-m")
    cmems.add_argument("--variables", required=True, help="Variables CSV")
    cmems.add_argument("--longitudes", required=True, help="MinLon,MaxLon")
    cmems.add_argument("--latitudes", required=True, help="MinLat,MaxLat")
    cmems.add_argument("--start-date", required=True, help="Format YYYY-MM-DD")
    cmems.add_argument("--end-date", required=True, help="Format YYYY-MM-DD")
    cmems.add_argument("--depth", required=True, help="MinDepth,MaxDepth")
    cmems.add_argument("--output-dir", required=True, help="Dossier de sortie")
    cmems.add_argument("--username", help="Compte Copernicus Marine")
    cmems.add_argument("--password", help="Mot de passe Copernicus Marine")

    return parser


def _run_from_env() -> None:
    source = (_env("DATA_SOURCE", fallback="") or "").strip().lower()
    dataset_any = (_env("DATASET", fallback="") or "").strip().lower()

    if not source:
        if "era5" in dataset_any:
            source = "era5"
        elif "cmems" in dataset_any or "glorys" in dataset_any:
            source = "cmems"

    if source == "era5":
        dataset = _env("ERA5_DATASET", fallback=_env("DATASET"), required=True)
        variables = _split_csv(_env("ERA5_VARIABLES", fallback=_env("VARIABLE_ERA5"), required=True))
        years = _split_csv(_env("ERA5_YEARS", fallback=_env("YEAR"), required=True))
        area = _parse_float_csv(_env("ERA5_AREA", fallback=_env("AREA"), required=True), expected_len=4)
        output_dir = _env("ERA5_OUTPUT_DIR", fallback=_env("OUTPUT_DIR"), required=True)

        download_era5(dataset=dataset, variables=variables, years=years, area=area, output_dir=output_dir)
        return

    if source == "cmems":
        dataset = _env("CMEMS_DATASET", fallback=_env("DATASET"), required=True)
        variables = _split_csv(_env("CMEMS_VARIABLES", fallback=_env("VARIABLE_GLORYS12"), required=True))
        longitudes = _parse_float_csv(_env("CMEMS_LONGITUDES", fallback=_env("LONGITUDE"), required=True), 2)
        latitudes = _parse_float_csv(_env("CMEMS_LATITUDES", fallback=_env("LATITUDE"), required=True), 2)
        start_date = _env("CMEMS_START_DATE", fallback=_env("START_DATE"), required=True)
        end_date = _env("CMEMS_END_DATE", fallback=_env("END_DATE"), required=True)
        depth = _parse_float_csv(_env("CMEMS_DEPTH", fallback=_env("DEPTH"), required=True), 2)
        output_directory = _env("CMEMS_OUTPUT_DIR", fallback=_env("OUTPUT_DIRECTORY"), required=True)
        username = _env("CMEMS_USERNAME", fallback=_env("USERNAME_CMEMS"))
        password = _env("CMEMS_PASSWORD", fallback=_env("PASSWORD_CMEMS"))

        download_cmems(
            dataset=dataset,
            start_date=start_date,
            end_date=end_date,
            variables=variables,
            longitudes=longitudes,
            latitudes=latitudes,
            depth=depth,
            output_directory=output_directory,
            username=username,
            password=password,
        )
        return

    raise ValueError(
        "Impossible de déterminer la source dans .env. "
        "Définissez DATA_SOURCE=era5 ou DATA_SOURCE=cmems."
    )


def main() -> None:
    parser = _build_parser()
    args = parser.parse_args()

    load_dotenv(args.env_file)

    try:
        # No subcommand provided: fallback to .env mode.
        if args.source is None:
            _run_from_env()
            return

        if args.source == "era5":
            download_era5(
                dataset=args.dataset,
                variables=_split_csv(args.variables),
                years=_split_csv(args.years),
                area=_parse_float_csv(args.area, expected_len=4),
                output_dir=args.output_dir,
            )
            return

        if args.source == "cmems":
            download_cmems(
                dataset=args.dataset,
                variables=_split_csv(args.variables),
                longitudes=_parse_float_csv(args.longitudes, 2),
                latitudes=_parse_float_csv(args.latitudes, 2),
                start_date=args.start_date,
                end_date=args.end_date,
                depth=_parse_float_csv(args.depth, 2),
                output_directory=args.output_dir,
                username=args.username,
                password=args.password,
            )
            return

        parser.print_help()
    except Exception as exc:
        print(f"Erreur: {exc}")
        raise SystemExit(1) from exc


if __name__ == "__main__":
    main()