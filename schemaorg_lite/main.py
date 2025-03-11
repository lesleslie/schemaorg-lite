import re
import typing as t
from collections.abc import Mapping
from contextlib import suppress
from logging import getLogger

from schemaorg_lite.data import (
    find_similar_types,
    get_versions,
    read_properties_csv,
    read_types_csv,
)

logger = getLogger("schemaorg_lite")


class Schema:
    def __init__(
        self,
        schema_type: str,
        version: str | float | None = None,
        base: str | None = None,
    ) -> None:
        self.type: str = schema_type
        self.loaded: dict[str, t.Any] = {}
        self.properties: dict[str, str] = {}
        self._properties: dict[str, dict[str, t.Any]] = {}
        self.type_spec: dict[str, t.Any] = {}
        self._set_base(base)
        self._set_version(version)
        self.load_type(schema_type)
        self.url: str | None = None
        self._set_type(schema_type)

    def __str__(self) -> str:
        return f"{self.type} ({self.version})"

    def __repr__(self) -> str:
        return self.__str__()

    def _set_base(self, base: str | None) -> None:
        if base is None:
            base = "https://www.schema.org"
        if not re.search("^http", base):
            logger.error(f"{base} must be a valid URL starting with http or https")
        self.base = base

    def _set_version(self, version: str | float | None) -> None:
        available: list[str] = get_versions()
        if version is None:
            version = available[-1]
        version = str(version)
        if version not in available:
            logger.warning(f"Version {version} is not found in the data folder")
            version = available[-1]
        self.version = version

    def add_property(self, name: str, value: t.Any) -> None:
        if value not in ("", None, [], ()) and name in self._properties:
            self.properties[name] = value
            logger.debug(f"{name} set to {value}")

    def remove_property(self, name: str) -> None:
        if name.lower() in self.properties:
            del self.properties[name.lower()]

    def load_type(self, schema_type: str) -> None:
        self._load_type(schema_type)
        self._load_props()
        self._load_attributes()

    def _load_custom_props(self, key: str = "mapping", field: str = "property") -> None:
        lookup: Mapping[str, dict[str, t.Any]] = read_properties_csv(
            version=self.version
        )
        props: list[dict[str, t.Any]] = self.loaded.get(key, [])
        for prop in props:
            name = f"https://schema.org/{prop[field]}"
            self._properties[prop[field]] = {}
            prop = {k: v for k, v in prop.items() if v}
            if name in lookup:
                self._properties[prop[field]].update(lookup[name])
            self._properties[prop[field]].update(prop)
        logger.debug(f"{self.type}: found {len(self._properties)} properties")

    def _load_props(self) -> None:
        lookup: Mapping[str, dict[str, t.Any]] = read_properties_csv(
            version=self.version
        )
        with suppress(AttributeError):
            if "properties" in self.type_spec:
                props = self.type_spec["properties"].split(",")
                props = [p.strip() for p in props]
                for prop in props:
                    if prop in lookup:
                        prop_data = lookup[prop]
                        label = prop_data.get("label")
                        if label:
                            self._properties[label] = prop_data
                logger.debug(f"{self.type}: found {len(self._properties)} properties")

    def _load_type(self, schema_type: str) -> None:
        typs: t.Union[dict[str, dict[str, t.Any]], dict[str, str], list[str]] = (
            read_types_csv(version=self.version)
        )
        if isinstance(typs, dict):
            if schema_type not in typs:
                logger.error(f"{schema_type} is not a valid type!")
                self.print_similar_types(schema_type)
                return
            type_spec = typs.get(self.type)
            if isinstance(type_spec, dict):
                self.type_spec = type_spec
            else:
                logger.error(
                    f"Type specification for {self.type} is not a valid dictionary."
                )
        else:
            logger.error(f"Unexpected type returned from read_types_csv: {type(typs)}")

    def _set_type(self, schema_type: str) -> None:
        self.type = schema_type
        self.url = "/".join([self.base, self.type])

    def _load_attributes(self) -> None:
        with suppress(AttributeError):
            for attr in list(self.type_spec.keys()):
                if attr != "properties":
                    setattr(self, attr, self.type_spec[attr])

    def print_similar_types(self, schema_type: str | None = None) -> None:
        contenders = find_similar_types(schema_type or self.type)
        if contenders:
            logger.info("Did you mean:")
            logger.info("\n\t".join(contenders))
