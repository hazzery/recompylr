from typing import Type


type_names = {
    int: "integer",
    float: "number",
    list: "list",
    dict: "table",
    str: "string",
    (list, str): "list of strings",
}


def check_for_property(
    dictionary: dict,
    property_name: str,
    property_type: Type,
    error_list: list[str],
) -> None:
    """Check that the provided dictionary contains a specific property.

    :property_name: The name of the property that must be present in the build specification.
    :property_type: The python type which the property should be.
    """
    if property_name not in dictionary:
        error_list.append(
            f"Must contain a {type_names[property_type]} named `{property_name}`"
        )

    elif not isinstance(dictionary[property_name], property_type):
        error_list.append(f"Value `{property_name}` must be a {property_type}")
