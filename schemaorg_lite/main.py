import re
from contextlib import suppress
from logging import getLogger

from schemaorg_lite.data import (
    find_similar_types,
    get_schemaorg_version,
    get_versions,
    read_properties_csv,
    read_types_csv,
)

get_schemaorg_version()

logger = getLogger("schemaorg_lite")


class Schema:
    def __init__(
        self,
        schema_type: str,
        version: str | float | None = None,
        base: str | None = None,
    ) -> None:
        self.type = schema_type
        self.loaded = {}
        self.properties = {}
        self._properties = {}
        self._set_base(base)
        self._set_version(version)
        self.load_type(schema_type)

    def __str__(self) -> str:
        return self.type

    def __repr__(self) -> str:
        return self.__str__()

    def _set_base(self, base: str | None) -> None:
        if base is None:
            base = "https://www.schema.org"
        if not re.search("^http", base):
            logger.error(f"{base} must be a valid URL starting with http or https")
        # logger.debug(f"Specification base set to {base}")
        self.base = base

    def _set_version(self, version: str | float | None) -> None:
        available = get_versions()
        if version is None:
            version = available[-1]
        version = str(version)
        if version not in available:
            logger.warning(f"Version {version} is not found in the data folder")
            version = available[-1]
        self.version = version

    def add_property(self, name: str, value: str) -> None:
        if value not in ("", None, [], ()) and name in self._properties:
            self.properties[name] = value
            logger.debug(f"{name} set to {value}")

    def remove_property(self, name: str) -> None:
        del self.properties[name.lower()]

    def load_type(self, schema_type: str) -> None:
        self._load_type(schema_type)
        self._load_props()
        self._load_attributes()

    def _load_custom_props(self, key: str = "mapping", field: str = "property") -> None:
        lookup = read_properties_csv(version=self.version)
        props = self.loaded[key]
        for prop in props:
            name = f"https://schema.org/{prop[field]}"
            self._properties[prop[field]] = {}
            prop = {k: v for k, v in prop.items() if v}
            if isinstance(lookup, dict):
                if name in lookup:
                    self._properties[prop[field]] = lookup[name]
                self._properties[prop[field]].update(prop)
        logger.debug(f"{self.type}: found {len(self._properties)} properties")

    def _load_props(self) -> None:
        lookup = read_properties_csv(version=self.version)
        with suppress(AttributeError):
            props = self.type_spec["properties"].split(",")  # type: ignore
            props = [p.strip() for p in props]
            for prop in props:
                if prop in lookup:
                    # The label is the most human friendly key
                    self._properties[lookup[prop]["label"]] = lookup[  # type: ignore
                        prop
                    ]
            logger.debug(f"{self.type}: found {len(self._properties)} properties")

    def _load_type(self, schema_type: str) -> None:
        typs = read_types_csv(version=self.version)
        if schema_type not in typs:
            logger.error(f"{schema_type} is not a valid type!")
            self.print_similar_types(schema_type)
            return
        self._set_type(schema_type)
        # logger.info(f"Found {self.url}")
        if isinstance(typs, dict):
            self.type_spec = typs[self.type]

    def _set_type(self, schema_type: str) -> None:
        self.type = schema_type
        self.url = "/".join([self.base, self.type])

    def _load_attributes(self) -> None:
        with suppress(AttributeError):
            for attr in list(self.type_spec.keys()):  # type: ignore
                if attr != "properties":
                    setattr(self, attr, self.type_spec[attr])

    def print_similar_types(self, schema_type: str | None = None) -> None:
        contenders = find_similar_types(schema_type or self.type)
        if contenders:
            logger.info("Did you mean:")
            logger.info("\n\t".join(contenders))
