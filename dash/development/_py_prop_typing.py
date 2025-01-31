import collections
import json
import string
import textwrap

import stringcase


shapes = {}
shape_template = """{name} = TypedDict(
    "{name}",
    {values}
)
"""
custom_imports = collections.defaultdict(lambda: collections.defaultdict(list))


def _clean_key(key):
    k = ""
    for ch in key:
        if ch not in string.ascii_letters + "_":
            k += "_"
        else:
            k += ch
    return k


def generate_any(*_):
    return "typing.Any"


def generate_shape(type_info, component_name: str, prop_name: str):
    props = []
    name = stringcase.pascalcase(prop_name)

    for prop_key, prop_type in type_info["value"].items():
        typed = get_prop_typing(
            prop_type["name"], component_name, f"{prop_name}_{prop_key}", prop_type
        )
        if not prop_type.get("required"):
            props.append(f'        "{prop_key}": NotRequired[{typed}]')
        else:
            props.append(f'        "{prop_key}": {typed}')

    shapes.setdefault(component_name, {})
    shapes[component_name][name] = textwrap.indent(
        shape_template.format(
            name=name, values="    {\n" + ",\n".join(props) + "\n    }"
        ),
        "    ",
    )

    return f'"{name}"'


def generate_union(type_info, component_name: str, prop_name: str):
    types = []
    for union in type_info["value"]:
        u_type = get_prop_typing(union["name"], component_name, prop_name, union)
        if u_type not in types:
            types.append(u_type)
    return f"typing.Union[{', '.join(types)}]"


def generate_tuple(
    type_info,
    component_name: str,
    prop_name: str,
):
    els = type_info.get("elements")
    elements = ", ".join(
        get_prop_typing(x.get("name"), component_name, prop_name, x) for x in els
    )
    return f"typing.Tuple[{elements}]"


def generate_array_of(
    type_info,
    component_name: str,
    prop_name: str,
):
    typed = get_prop_typing(
        type_info["value"]["name"], component_name, prop_name, type_info["value"]
    )
    return f"typing.Sequence[{typed}]"


def generate_object_of(type_info, component_name: str, prop_name: str):
    typed = get_prop_typing(
        type_info["value"]["name"], component_name, prop_name, type_info["value"]
    )
    return f"typing.Dict[typing.Union[str, float, int], {typed}]"


def generate_type(typename):
    def type_handler(*_):
        return typename

    return type_handler


def _get_literal_value(value):
    if isinstance(value, str):
        value = json.loads(value.replace("'", '"'))

    if value is None:
        return "None"

    if isinstance(value, bool):
        return str(value)

    return json.dumps(value)


def generate_enum(type_info, *_):
    values = [_get_literal_value(v["value"]) for v in type_info["value"] if v]
    return f"Literal[{', '.join(values)}]"


def get_prop_typing(
    type_name: str, component_name: str, prop_name: str, type_info, namespace=None
):
    if prop_name == "id":
        # Id is always the same either a string or a dict for pattern matching.
        return "typing.Union[str, dict]"

    if namespace:
        # Only check the namespace once
        special = (
            special_cases.get(namespace, {}).get(component_name, {}).get(prop_name)
        )
        if special:
            return special(type_info, component_name, prop_name)

    prop_type = PROP_TYPING.get(type_name, generate_any)(
        type_info, component_name, prop_name
    )
    return prop_type


def generate_plotly_figure(*_):
    custom_imports["dash_core_components"]["Graph"].append(
        "from plotly.graph_objects import Figure"
    )
    return "typing.Union[Figure, dict]"


def generate_datetime_prop(component, array=False):
    if "import datetime" not in custom_imports["dash_core_components"][component]:
        custom_imports["dash_core_components"][component].append("import datetime")

    def generator(*_):
        datetime_type = "typing.Union[str, datetime.datetime]"
        if array:
            datetime_type = f"typing.Sequence[{datetime_type}]"
        return datetime_type

    return generator


special_cases = {
    "dash_core_components": {
        "Graph": {"figure": generate_plotly_figure},
        "DatePickerRange": {
            "start_date": generate_datetime_prop("DatePickerRange"),
            "end_date": generate_datetime_prop("DatePickerRange"),
            "min_date_allowed": generate_datetime_prop("DatePickerRange"),
            "max_date_allowed": generate_datetime_prop("DatePickerRange"),
            "disabled_days": generate_datetime_prop("DatePickerRange", True),
        },
        "DatePickerSingle": {
            "date": generate_datetime_prop("DatePickerSingle"),
            "min_date_allowed": generate_datetime_prop("DatePickerSingle"),
            "max_date_allowed": generate_datetime_prop("DatePickerSingle"),
            "disabled_days": generate_datetime_prop("DatePickerSingle", True),
            "initial_visible_month": generate_datetime_prop("DatePickerSingle"),
        },
    }
}


PROP_TYPING = {
    "array": generate_type("typing.Sequence"),
    "arrayOf": generate_array_of,
    "object": generate_type("dict"),
    "shape": generate_shape,
    "exact": generate_shape,
    "string": generate_type("str"),
    "bool": generate_type("bool"),
    "number": generate_type("typing.Union[int, float, numbers.Number]"),
    "node": generate_type(
        "typing.Union[str, int, float, ComponentType,"
        " typing.Sequence[typing.Union"
        "[str, int, float, ComponentType]]]"
    ),
    "func": generate_any,
    "element": generate_type("ComponentType"),
    "union": generate_union,
    "any": generate_any,
    "custom": generate_any,
    "enum": generate_enum,
    "objectOf": generate_object_of,
    "tuple": generate_tuple,
}
