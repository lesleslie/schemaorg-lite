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
        schema = Schema(schema_type="ValidType")
        schema._properties["validName"] = {"property": "validName"}
        schema.add_property("validName", "validValue")
        assert schema.properties["validName"] == "validValue"

    def test_add_property_ignores_empty_values(self, mocker: MockerFixture) -> None:
        schema = Schema(schema_type="ValidType")
        schema._properties["validName"] = {"property": "validName"}
        schema.add_property("validName", "")
        assert "validName" not in schema.properties
        schema.add_property("validName", None)
        assert "validName" not in schema.properties
        schema.add_property("validName", [])
        assert "validName" not in schema.properties
        schema.add_property("validName", ())
        assert "validName" not in schema.properties

    def test_remove_property_with_existing_name(self, mocker: MockerFixture) -> None:
        schema = Schema(schema_type="ValidType")
        schema._properties["existingname"] = {"property": "existingName"}
        schema.add_property("existingname", "value")
        schema.remove_property("existingname")
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

    def test_set_base_logs_error_for_invalid_base(self, mocker: MockerFixture) -> None:
        mock_logger = mocker.patch("schemaorg_lite.main.logger")
        Schema(schema_type="Person", base="invalid_base")
        mock_logger.error.assert_called_once_with(
            "invalid_base must be a valid URL starting with http or https"
        )

    def test_set_version_logs_warning_for_invalid_version(
        self, mocker: MockerFixture
    ) -> None:
        mock_logger = mocker.patch("schemaorg_lite.main.logger")
        mock_get_versions = mocker.patch("schemaorg_lite.main.get_versions")
        mock_get_versions.return_value = ["13.0", "14.0"]
        mock_read_types = mocker.patch("schemaorg_lite.main.read_types_csv")
        mock_read_types.return_value = {"Person": {}}
        mocker.patch("schemaorg_lite.main.read_properties_csv")

        schema = Schema(schema_type="Person", version="99.0")

        mock_logger.warning.assert_called_once_with(
            "Version 99.0 is not found in the data folder"
        )
        assert schema.version == "14.0"  # Ensure it defaults to latest
        mock_get_versions.assert_called_once()
        mock_read_types.assert_called_once()

    def test_load_custom_props_with_data(self, mocker: MockerFixture) -> None:
        mock_read_properties_csv = mocker.patch(
            "schemaorg_lite.main.read_properties_csv"
        )
        mock_read_properties_csv.return_value = {
            "testProperty": {"label": "testProperty", "property": "testProperty"}
        }
        schema = Schema(schema_type="Person")
        schema.loaded = {
            "mapping": [{"property": "testProperty", "description": "testDescription"}]
        }

        schema._load_custom_props()

        assert "testProperty" in schema._properties
        assert schema._properties["testProperty"]["property"] == "testProperty"
        # Adjust the assertion to expect two calls
        assert mock_read_properties_csv.call_count == 2

    def test_load_type_invalid_type_spec(self, mocker: MockerFixture) -> None:
        mock_logger = mocker.patch("schemaorg_lite.main.logger")

        mock_read_types = mocker.patch("schemaorg_lite.main.read_types_csv")
        mock_read_types.return_value = {"Person": "not a dictionary"}

        Schema(schema_type="Person")

        mock_logger.error.assert_called_once_with(
            "Type specification for Person is not a valid dictionary."
        )
        mock_read_types.assert_called_once()

    def test_set_attribute_sets_attributes(self, mocker: MockerFixture) -> None:
        schema = Schema(schema_type="Person")
        schema.type_spec = {"attr1": "value1", "attr2": "value2"}

        schema._load_attributes()

        assert schema.attr1 == "value1"  # type: ignore
        assert schema.attr2 == "value2"  # type: ignore

    def test_repr_returns_correct_string(self, mocker: MockerFixture) -> None:
        mock_get_versions = mocker.patch("schemaorg_lite.main.get_versions")
        mock_get_versions.return_value = ["23.0"]
        schema = Schema("Person")
        assert repr(schema) == "Person (23.0)"
        mock_get_versions.assert_called_once()

    def test_load_props_with_data(self, mocker: MockerFixture) -> None:
        mock_read_properties_csv = mocker.patch(
            "schemaorg_lite.main.read_properties_csv"
        )
        mock_read_properties_csv.return_value = {
            "name": {
                "label": "name",
                "description": "testDescription",
                "property": "name",
            }
        }
        mock_read_types = mocker.patch("schemaorg_lite.main.read_types_csv")
        mock_read_types.return_value = {"ValidType": {"properties": "name,email"}}

        schema = Schema(schema_type="ValidType")
        schema._load_props()

        assert "name" in schema._properties
        assert schema._properties["name"]["description"] == "testDescription"
        # Adjust the assertion to expect two calls
        assert mock_read_properties_csv.call_count == 2
        mock_read_types.assert_called_once()
