from pytest_mock import MockerFixture
from schemaorg_lite.main import Schema


class TestSchema:
    def test_init_with_valid_schema_type(self, mocker: MockerFixture) -> None:
        mock_read_types = mocker.patch("schemaorg_lite.main.read_types_csv")
        mock_read_types.return_value = {"Person": {"properties": "name,email"}}

        mock_get_versions = mocker.patch("schemaorg_lite.main.get_versions")
        mock_get_versions.return_value = ["13.0", "14.0"]

        mocker.patch("schemaorg_lite.main.read_properties_csv", return_value={})
        mocker.patch("schemaorg_lite.main.logger")

        schema = Schema("Person")

        assert schema.type == "Person"
        assert schema.base == "https://www.schema.org"
        assert schema.version == "14.0"
        assert schema.url == "https://www.schema.org/Person"
        mock_read_types.assert_called_once_with(version="14.0")

    def test_init_with_nonexistent_schema_type(self, mocker: MockerFixture) -> None:
        mock_read_types = mocker.patch("schemaorg_lite.main.read_types_csv")
        mock_read_types.return_value = {"Person": {"properties": "name,email"}}

        mock_get_versions = mocker.patch("schemaorg_lite.main.get_versions")
        mock_get_versions.return_value = ["13.0", "14.0"]

        mock_logger = mocker.patch("schemaorg_lite.main.logger")

        mock_find_similar = mocker.patch("schemaorg_lite.main.find_similar_types")
        mock_find_similar.return_value = ["Person", "Organization"]

        # Mock read_properties_csv to prevent FileNotFoundError
        mocker.patch("schemaorg_lite.main.read_properties_csv", return_value={})

        schema = Schema("NonExistentType")

        assert schema.type == "NonExistentType"
        mock_logger.error.assert_called_once_with(
            "NonExistentType is not a valid type!"
        )
        mock_find_similar.assert_called_once_with("NonExistentType")
        mock_logger.info.assert_any_call("Did you mean:")

    def test_add_property_with_valid_name_and_value(
        self, mocker: MockerFixture
    ) -> None:
        mocker.patch(
            "schemaorg_lite.main.read_properties_csv",
            return_value={"validName": {"label": "validName"}},
        )
        schema = Schema(schema_type="ValidType")
        schema._properties["validName"] = {}
        schema.add_property("validName", "validValue")
        assert schema.properties["validName"] == "validValue"

    def test_remove_property_with_existing_name(self, mocker: MockerFixture) -> None:
        mocker.patch(
            "schemaorg_lite.main.read_properties_csv",
            return_value={"existingName": {"label": "existingName"}},
        )
        schema = Schema(schema_type="ValidType")
        schema._properties["existingname"] = {}  # Ensure lowercase key
        schema.add_property("existingname", "value")  # Ensure lowercase key
        schema.remove_property("existingname")  # Ensure lowercase key
        assert "existingname" not in schema.properties

    def test_load_valid_schema_type(self, mocker: MockerFixture) -> None:
        mocker.patch(
            "schemaorg_lite.main.read_types_csv",
            return_value={"ValidType": {"properties": "name,email"}},
        )
        schema = Schema(schema_type="ValidType")
        assert schema.type == "ValidType"

    def test_string_representation_returns_type_name(self) -> None:
        schema = Schema(schema_type="Person", version="23.0")  # Ensure version is set
        assert str(schema) == "Person (23.0)"  # Update expected value

    def test_default_version_set_to_latest(self, mocker: MockerFixture) -> None:
        mocker.patch(
            "schemaorg_lite.main.get_versions", return_value=["1.0", "2.0", "3.0"]
        )
        mocker.patch(
            "schemaorg_lite.main.read_types_csv",
            return_value={"Person": {"properties": "name,email"}},
        )
        mocker.patch("schemaorg_lite.main.read_properties_csv", return_value={})
        schema = Schema(schema_type="Person")
        assert schema.version == "3.0"

    def test_default_base_set_to_schema_org(self) -> None:
        schema = Schema(schema_type="Person")
        assert schema.base == "https://www.schema.org"
