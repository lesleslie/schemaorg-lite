# schemaorg-lite

[![Code style: crackerjack](https://img.shields.io/badge/code%20style-crackerjack-000042)](https://github.com/lesleslie/crackerjack)

`schemaorg-lite` is a lightweight Python library for working with [Schema.org](https://schema.org/) vocabulary. It provides a simple interface to access Schema.org types and properties, allowing you to easily integrate structured data into your applications. This library is a streamlined alternative to the full schema.org release, focusing on core functionality for tagging content.

## Purpose

`schemaorg-lite` aims to:

*   **Simplify Access:** Provide an easy way to access and use Schema.org types and properties.
*   **Content Tagging:** Facilitate tagging web content with Schema.org metadata.
*   **Core Functionality:** Offer a core subset of Schema.org functionality.
*   **Stay Updated:** Ensure access to current Schema.org versions.

## Key Features

*   **Type Loading:** Easily load Schema.org types (e.g., `Person`, `Organization`, `Product`).
*   **Property Management:** Add, manage, and remove properties for Schema.org types.
*   **Version Handling:** Access specific Schema.org versions (23.0 and later).
*   **URL Generation:** Automatically generate URLs for Schema.org types.
*   **Type Validation:** Check if a Schema.org type is valid.
*   **Similar Type Suggestions:** Suggest similar types if an invalid type is requested.

## What `schemaorg-lite` is NOT

*   **Full Ontology Management:** This library does not provide advanced features for querying or manipulating the full Schema.org ontology.
*   **Complex Reasoning:** It does not support complex reasoning or inference over the Schema.org graph.
*   **JSON-LD Generation:** This library does not generate JSON-LD.

## Installation

`pip install schemaorg-lite`

## Usage

`schemaorg-lite` makes working with Schema.org types and properties straightforward. Here's how to get started:

`from schemaorg_lite.main import Schema`

#### Load a Schema.org type (defaults to the latest version)

`person = Schema("Person")
print(person)  # Output: Person (latest version)`

#### Load a Schema.org type with a specific version

`organization = Schema("Organization", version="14.0")
print(organization)  # Output: Organization (14.0)`

#### Add properties to a Schema.org type

```
person.add_property("name", "John Doe")
person.add_property("email", "john.doe@example.com")
print(person.properties)  # Output: {'name': 'John Doe', 'email': 'john.doe@example.com'}
```

#### Remove a property

```
person.remove_property("email")
print(person.properties)  # Output: {'name': 'John Doe'}
```

#### Get the base URL

`print(person.base)  # Output: https://www.schema.org`

#### Get the version

`print(person.version)  # Output: The latest version (e.g., 23.0)`

## Contributing

Contributions are welcome! Please feel free to open a pull request or issue. We use crackerjack for development.
**See [crackerjack](https://github.com/lesleslie/crackerjack) for more information on setup and usage.**

To contribute:

1. Add Crackerjack as a development dependency to your project. From the project root, run:
  ```
  pdm add -G dev crackerjack
  ```

2. Run checks and tests before submitting. From the project root, run:
  ```
  python -m crackerjack -x -t
  ```

This ensures your code meets all quality standards before submission.

## License

This project is licensed under the terms of the **BSD 3-Clause License**. See the `LICENSE` file for details.

## Acknowledgments

*   [Schema.org](https://schema.org/): For creating and maintaining the vocabulary.
*   [schema-org](https://www.github.com/schemaorg/schemaorg): A Python package for working with schema.org that helped inform
    the design of `schemaorg-lite`.
