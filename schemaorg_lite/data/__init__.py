import csv
from pathlib import Path

from schemaorg_lite.main import logger


def get_installdir():
    """get_installdir returns the installation directory of the application"""
    return Path(__file__).parent.parent.parent


# csv


def read_csv(filename, mode: str = "r", delim: str = ",", header=None, keyfield=None):
    """read a comma separated value file, with default delimiter as comma.
    we assume reading a header, and use some identifier as key.

    Parameters
    ==========
    filename: the name of the csv file to read
    mode: the mode to read in (defaults to r)
    delim: the delimiter (defaults to comma)
    """
    file = Path(filename)

    if not file.exists():
        logger.error("{filename} does not exist.")

    # If we have a keyfield, return dictionary
    data = []
    if keyfield is not None:
        data = dict()

    with open(filename, mode="r", encoding="utf-8") as csv_file:
        csv_reader = csv.DictReader(csv_file, fieldnames=header)
        for row in csv_reader:
            if keyfield is not None:
                data[row[keyfield]] = row
            else:
                data.append(row)
    return data


################################################################################
# Software Versions
################################################################################


def get_versions():
    """list versions available, based on subfolders in a subfolder under the
    database. We default to listing those under "release."
    """
    base = get_database()
    versions = (base / "releases").iterdir()
    versions = [float(x.name) for x in versions]
    versions.sort()
    return [str(x) for x in versions]


def get_schemaorg_version():
    """determine the schemaorg_lite version to use based on an environmental variable
    first followed by  using the latest.
    """
    version = get_versions()[-1]

    logger.debug(f"schemaorg_lite version {version} selected")
    return version


def get_release(version=None):
    """get a subfolder for a particular release, defaults to latest"""
    base = get_database()
    if version is None:
        version = get_schemaorg_version()
    return base / "releases" / version


def get_database():
    """get the data folder with "release" and "ext" subfolders"""
    return get_installdir() / "schemaorg_lite" / "data"


# courtesy functions for schema.org exports

""" List of available csv --------------------------------------
all-layers-properties.csv  ext-health-lifesci-properties.csv
all-layers-types.csv       ext-health-lifesci-types.csv
ext-attic-properties.csv   ext-meta-properties.csv
ext-attic-types.csv        ext-meta-types.csv
ext-auto-properties.csv    ext-pending-properties.csv
ext-auto-types.csv         ext-pending-types.csv
ext-bib-properties.csv     schemaorg_lite-all-https-properties.csv
ext-bib-types.csv          schemaorg_lite-all-http-types.csv
"""


def read_properties_csv(keyfield: str = "id", version=None):
    """read in the properties csv (with all types), defaulting to using
    the "id" as the lookup key. We do this because the properties listed
    in the types csv include the full uri.

    Parameters
    ==========
    keyfield: the key to use to generate the lookup, a header in the csv
    version: release version under data/releases to use, defaults to latest
    """
    release_dir = get_release(version=version)
    filename = release_dir / "schemaorg_lite-all-https-properties.csv"
    return read_csv(filename, keyfield=keyfield)


def read_types_csv(keyfield: str = "label", version=None):
    """read in the types csv, with default lookup key as "label" since the
    likely use case will be the user searching for an item of interest.

    Parameters
    ==========
    keyfield: the key to use to generate the lookup, a header in the csv
    version: release version under data/releases to use, defaults to latest
    """
    release_dir = get_release(version=version)
    filename = release_dir / "schemaorg_lite-all-https-types.csv"
    return read_csv(filename, keyfield=keyfield)


def find_similar_types(term, version=None):
    """find similar types, with intent to show to the user in case
    capitalization was off.

    Parameters
    ==========
    term: a term to search for, in entirety. Casing doesn't matter
    version: release version under data/releases to use, defaults to latest
    """
    typs = read_types_csv(version=version)

    # In case the user provided an url, remove it
    term = term.split("/")[-1].lower()

    # Look for entire term
    return [x for x in typs if term in x.lower()]
