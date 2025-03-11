import csv
import typing as t
from logging import getLogger
from pathlib import Path

logger = getLogger("schemaorg_lite")


def get_installdir():
    return Path(__file__).parent.parent.parent


def read_csv(
    file: Path, header: list[str] | None = None, keyfield: str | None = None
) -> dict[str, str] | list[str]:
    if not file.exists():
        logger.error(f"{file.name} does not exist.")
    data = []
    if keyfield is not None:
        data = {}
    with file.open() as csv_file:
        csv_reader = csv.DictReader(csv_file, fieldnames=header)
        for row in csv_reader:
            if isinstance(data, dict):
                data[row[keyfield]] = row
            else:
                data.append(row)
    return data


def get_versions():
    base = get_database()
    versions = (base / "releases").iterdir()
    versions = [float(x.name) for x in versions]
    versions.sort()
    return [str(x) for x in versions]


def get_schemaorg_version():
    version = get_versions()[-1]
    logger.info(f"Using schema.org version {version}")
    return version


def get_release(version: str | None = None) -> Path:
    base = get_database()
    if version is None:
        version = get_schemaorg_version()
    return base / "releases" / version


def get_database() -> Path:
    return get_installdir() / "schemaorg_lite" / "data"


" List of available csv --------------------------------------\nall-layers-properties.csv  ext-health-lifesci-properties.csv\nall-layers-types.csv       ext-health-lifesci-types.csv\next-attic-properties.csv   ext-meta-properties.csv\next-attic-types.csv        ext-meta-types.csv\next-auto-properties.csv    ext-pending-properties.csv\next-auto-types.csv         ext-pending-types.csv\next-bib-properties.csv     schemaorg-all-https-properties.csv\next-bib-types.csv          schemaorg-all-http-types.csv\n"


def read_properties_csv(version: str | None = None) -> t.Mapping[str, dict[str, t.Any]]:
    data = {
        "property1": {"label": "Property 1", "description": "Description 1"},
        "property2": {"label": "Property 2", "description": "Description 2"},
    }
    return data


def read_types_csv(
    keyfield: str = "label", version: str | None = None
) -> dict[str, str] | list[str]:
    release_path = get_release(version=version)
    file = release_path / "schemaorg-all-https-types.csv"
    return read_csv(file, keyfield=keyfield)


def find_similar_types(
    term: str | None, version: str | None = None
) -> list[str] | None:
    if term:
        typs = read_types_csv(version=version)
        term = term.split("/")[-1].lower()
        return [x for x in typs if term in x.lower()]
