import csv
from logging import getLogger
from pathlib import Path

logger = getLogger("schemaorg_lite")


def get_installdir():
    return Path(__file__).parent.parent.parent


# csv


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
                data[row[keyfield]] = row  # type: ignore
            else:
                data.append(row)
    return data


################################################################################
# Software Versions
################################################################################


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


# courtesy functions for schema.org exports

""" List of available csv --------------------------------------
all-layers-properties.csv  ext-health-lifesci-properties.csv
all-layers-types.csv       ext-health-lifesci-types.csv
ext-attic-properties.csv   ext-meta-properties.csv
ext-attic-types.csv        ext-meta-types.csv
ext-auto-properties.csv    ext-pending-properties.csv
ext-auto-types.csv         ext-pending-types.csv
ext-bib-properties.csv     schemaorg-all-https-properties.csv
ext-bib-types.csv          schemaorg-all-http-types.csv
"""


def read_properties_csv(
    keyfield: str = "id", version: str | None = None
) -> dict[str, str] | list[str]:
    release_dir = get_release(version=version)
    filename = release_dir / "schemaorg-all-https-properties.csv"
    return read_csv(filename, keyfield=keyfield)


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
