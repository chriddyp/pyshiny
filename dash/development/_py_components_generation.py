from collections import OrderedDict
import copy
import os
from textwrap import fill, dedent

from dash.development.base_component import _explicitize_args
from dash.exceptions import NonExistentEventException
from ._all_keywords import python_keywords
from ._collect_nodes import collect_nodes, filter_base_nodes
from .base_component import Component


# pylint: disable=unused-argument,too-many-locals
def generate_class_string(
    typename,
    props,
    description,
    namespace,
    prop_reorder_exceptions=None,
    max_props=None,
):
    """Dynamically generate class strings to have nicely formatted docstrings,
    keyword arguments, and repr.
    Inspired by http://jameso.be/2013/08/06/namedtuple.html
    Parameters
    ----------
    typename
    props
    description
    namespace
    prop_reorder_exceptions
    Returns
    -------
    string
    """
    # TODO _prop_names, _type, _namespace, and available_properties
    # can be modified by a Dash JS developer via setattr
    # TODO - Tab out the repr for the repr of these components to make it
    # look more like a hierarchical tree
    # TODO - Include "description" "defaultValue" in the repr and docstring
    #
    # TODO - Handle "required"
    #
    # TODO - How to handle user-given `null` values? I want to include
    # an expanded docstring like Dropdown(value=None, id=None)
    # but by templating in those None values, I have no way of knowing
    # whether a property is None because the user explicitly wanted
    # it to be `null` or whether that was just the default value.
    # The solution might be to deal with default values better although
    # not all component authors will supply those.
    c = '''class {typename}(Component):
    """{docstring}"""
    _children_props = {children_props}
    _base_nodes = {base_nodes}
    _namespace = '{namespace}'
    _type = '{typename}'
    @_explicitize_args
    def __init__(self, {default_argtext}):
        self._prop_names = {list_of_valid_keys}
        self._valid_wildcard_attributes =\
            {list_of_valid_wildcard_attr_prefixes}
        self.available_properties = {list_of_valid_keys}
        self.available_wildcard_properties =\
            {list_of_valid_wildcard_attr_prefixes}
        _explicit_args = kwargs.pop('_explicit_args')
        _locals = locals()
        _locals.update(kwargs)  # For wildcard attrs and excess named props
        args = {args}
        {required_validation}
        super({typename}, self).__init__({argtext})
'''

    filtered_props = (
        filter_props(props)
        if (prop_reorder_exceptions is not None and typename in prop_reorder_exceptions)
        or (prop_reorder_exceptions is not None and "ALL" in prop_reorder_exceptions)
        else reorder_props(filter_props(props))
    )
    wildcard_prefixes = repr(parse_wildcards(props))
    list_of_valid_keys = repr(list(map(str, filtered_props.keys())))
    docstring = create_docstring(
        component_name=typename,
        props=filtered_props,
        description=description,
        prop_reorder_exceptions=prop_reorder_exceptions,
    ).replace("\r\n", "\n")
    required_args = required_props(filtered_props)
    is_children_required = "children" in required_args
    required_args = [arg for arg in required_args if arg != "children"]

    prohibit_events(props)

    # pylint: disable=unused-variable
    prop_keys = list(props.keys())
    if "children" in props and "children" in list_of_valid_keys:
        prop_keys.remove("children")
        default_argtext = "children=None, "
        args = "{k: _locals[k] for k in _explicit_args if k != 'children'}"
        argtext = "children=children, **args"
    else:
        default_argtext = ""
        args = "{k: _locals[k] for k in _explicit_args}"
        argtext = "**args"

    if len(required_args) == 0:
        required_validation = ""
    else:
        required_validation = f"""
        for k in {required_args}:
            if k not in args:
                raise TypeError(
                    'Required argument `' + k + '` was not specified.')
        """

    if is_children_required:
        required_validation += """
        if 'children' not in _explicit_args:
            raise TypeError('Required argument children was not specified.')
        """

    default_arglist = [
        (
            f"{p:s}=Component.REQUIRED"
            if props[p]["required"]
            else f"{p:s}=Component.UNDEFINED"
        )
        for p in prop_keys
        if not p.endswith("-*") and p not in python_keywords and p != "setProps"
    ]

    if max_props:
        final_max_props = max_props - (1 if "children" in props else 0)
        if len(default_arglist) > final_max_props:
            default_arglist = default_arglist[:final_max_props]
            docstring += (
                "\n\n"
                "Note: due to the large number of props for this component,\n"
                "not all of them appear in the constructor signature, but\n"
                "they may still be used as keyword arguments."
            )

    default_argtext += ", ".join(default_arglist + ["**kwargs"])
    nodes = collect_nodes({k: v for k, v in props.items() if k != "children"})

    return dedent(
        c.format(
            typename=typename,
            namespace=namespace,
            filtered_props=filtered_props,
            list_of_valid_wildcard_attr_prefixes=wildcard_prefixes,
            list_of_valid_keys=list_of_valid_keys,
            docstring=docstring,
            default_argtext=default_argtext,
            args=args,
            argtext=argtext,
            required_validation=required_validation,
            children_props=nodes,
            base_nodes=filter_base_nodes(nodes) + ["children"],
        )
    )


def generate_class_file(
    typename,
    props,
    description,
    namespace,
    prop_reorder_exceptions=None,
    max_props=None,
):
    """Generate a Python class file (.py) given a class string.
    Parameters
    ----------
    typename
    props
    description
    namespace
    prop_reorder_exceptions
    Returns
    -------
    """
    import_string = (
        "# AUTO GENERATED FILE - DO NOT EDIT\n\n"
        + "from dash.development.base_component import "
        + "Component, _explicitize_args\n\n\n"
    )

    class_string = generate_class_string(
        typename, props, description, namespace, prop_reorder_exceptions, max_props
    )
    file_name = f"{typename:s}.py"

    file_path = os.path.join(namespace, file_name)
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(import_string)
        f.write(class_string)

    print(f"Generated {file_name}")


def generate_imports(project_shortname, components):
    with open(
        os.path.join(project_shortname, "_imports_.py"), "w", encoding="utf-8"
    ) as f:
        component_imports = "\n".join(f"from .{x} import {x}" for x in components)
        all_list = ",\n".join(f'    "{x}"' for x in components)
        imports_string = f"{component_imports}\n\n__all__ = [\n{all_list}\n]"

        f.write(imports_string)


def generate_classes_files(project_shortname, metadata, *component_generators):
    components = []
    for component_path, component_data in metadata.items():
        component_name = component_path.split("/")[-1].split(".")[0]
        components.append(component_name)

        for generator in component_generators:
            generator(
                component_name,
                component_data["props"],
                component_data["description"],
                project_shortname,
            )

    return components


def generate_class(
    typename, props, description, namespace, prop_reorder_exceptions=None
):
    """Generate a Python class object given a class string.
    Parameters
    ----------
    typename
    props
    description
    namespace
    Returns
    -------
    """
    string = generate_class_string(
        typename, props, description, namespace, prop_reorder_exceptions
    )
    scope = {"Component": Component, "_explicitize_args": _explicitize_args}
    # pylint: disable=exec-used
    exec(string, scope)
    result = scope[typename]
    return result


def required_props(props):
    """Pull names of required props from the props object.
    Parameters
    ----------
    props: dict
    Returns
    -------
    list
        List of prop names (str) that are required for the Component
    """
    return [prop_name for prop_name, prop in list(props.items()) if prop["required"]]


def create_docstring(component_name, props, description, prop_reorder_exceptions=None):
    """Create the Dash component docstring.
    Parameters
    ----------
    component_name: str
        Component name
    props: dict
        Dictionary with {propName: propMetadata} structure
    description: str
        Component description
    Returns
    -------
    str
        Dash component docstring
    """
    # Ensure props are ordered with children first
    props = (
        props
        if (
            prop_reorder_exceptions is not None
            and component_name in prop_reorder_exceptions
        )
        or (prop_reorder_exceptions is not None and "ALL" in prop_reorder_exceptions)
        else reorder_props(props)
    )

    n = "n" if component_name[0].lower() in "aeiou" else ""
    args = "\n".join(
        create_prop_docstring(
            prop_name=p,
            type_object=prop["type"] if "type" in prop else prop["flowType"],
            required=prop["required"],
            description=prop["description"],
            default=prop.get("defaultValue"),
            indent_num=0,
            is_flow_type="flowType" in prop and "type" not in prop,
        )
        for p, prop in filter_props(props).items()
    )

    return (
        f"A{n} {component_name} component.\n{description}\n\nKeyword arguments:\n{args}"
    )


def prohibit_events(props):
    """Events have been removed. Raise an error if we see dashEvents or
    fireEvents.
    Parameters
    ----------
    props: dict
        Dictionary with {propName: propMetadata} structure
    Raises
    -------
    ?
    """
    if "dashEvents" in props or "fireEvents" in props:
        raise NonExistentEventException(
            "Events are no longer supported by dash. Use properties instead, "
            "eg `n_clicks` instead of a `click` event."
        )


def parse_wildcards(props):
    """Pull out the wildcard attributes from the Component props.
    Parameters
    ----------
    props: dict
        Dictionary with {propName: propMetadata} structure
    Returns
    -------
    list
        List of Dash valid wildcard prefixes
    """
    list_of_valid_wildcard_attr_prefixes = []
    for wildcard_attr in ["data-*", "aria-*"]:
        if wildcard_attr in props:
            list_of_valid_wildcard_attr_prefixes.append(wildcard_attr[:-1])
    return list_of_valid_wildcard_attr_prefixes


def reorder_props(props):
    """If "children" is in props, then move it to the front to respect dash
    convention, then 'id', then the remaining props sorted by prop name
    Parameters
    ----------
    props: dict
        Dictionary with {propName: propMetadata} structure
    Returns
    -------
    dict
        Dictionary with {propName: propMetadata} structure
    """

    # Constructing an OrderedDict with duplicate keys, you get the order
    # from the first one but the value from the last.
    # Doing this to avoid mutating props, which can cause confusion.
    props1 = [("children", "")] if "children" in props else []
    props2 = [("id", "")] if "id" in props else []
    return OrderedDict(props1 + props2 + sorted(list(props.items())))


def filter_props(props):
    """Filter props from the Component arguments to exclude:
        - Those without a "type" or a "flowType" field
        - Those with arg.type.name in {'func', 'symbol', 'instanceOf'}
    Parameters
    ----------
    props: dict
        Dictionary with {propName: propMetadata} structure
    Returns
    -------
    dict
        Filtered dictionary with {propName: propMetadata} structure
    Examples
    --------
    ```python
    prop_args = {
        'prop1': {
            'type': {'name': 'bool'},
            'required': False,
            'description': 'A description',
            'flowType': {},
            'defaultValue': {'value': 'false', 'computed': False},
        },
        'prop2': {'description': 'A prop without a type'},
        'prop3': {
            'type': {'name': 'func'},
            'description': 'A function prop',
        },
    }
    # filtered_prop_args is now
    # {
    #    'prop1': {
    #        'type': {'name': 'bool'},
    #        'required': False,
    #        'description': 'A description',
    #        'flowType': {},
    #        'defaultValue': {'value': 'false', 'computed': False},
    #    },
    # }
    filtered_prop_args = filter_props(prop_args)
    ```
    """
    filtered_props = copy.deepcopy(props)

    for arg_name, arg in list(filtered_props.items()):
        if "type" not in arg and "flowType" not in arg:
            filtered_props.pop(arg_name)
            continue

        # Filter out functions and instances --
        # these cannot be passed from Python
        if "type" in arg:  # These come from PropTypes
            arg_type = arg["type"]["name"]
            if arg_type in {"func", "symbol", "instanceOf"}:
                filtered_props.pop(arg_name)
        elif "flowType" in arg:  # These come from Flow & handled differently
            arg_type_name = arg["flowType"]["name"]
            if arg_type_name == "signature":
                # This does the same as the PropTypes filter above, but "func"
                # is under "type" if "name" is "signature" vs just in "name"
                if "type" not in arg["flowType"] or arg["flowType"]["type"] != "object":
                    filtered_props.pop(arg_name)
        else:
            raise ValueError

    return filtered_props


def fix_keywords(txt):
    """
    replaces javascript keywords true, false, null with Python keywords
    """
    fix_word = {"true": "True", "false": "False", "null": "None"}
    for js_keyword, python_keyword in fix_word.items():
        txt = txt.replace(js_keyword, python_keyword)
    return txt


# pylint: disable=too-many-arguments
# pylint: disable=too-many-locals
def create_prop_docstring(
    prop_name,
    type_object,
    required,
    description,
    default,
    indent_num,
    is_flow_type=False,
):
    """Create the Dash component prop docstring.
    Parameters
    ----------
    prop_name: str
        Name of the Dash component prop
    type_object: dict
        react-docgen-generated prop type dictionary
    required: bool
        Component is required?
    description: str
        Dash component description
    default: dict
        Either None if a default value is not defined, or
        dict containing the key 'value' that defines a
        default value for the prop
    indent_num: int
        Number of indents to use for the context block
        (creates 2 spaces for every indent)
    is_flow_type: bool
        Does the prop use Flow types? Otherwise, uses PropTypes
    Returns
    -------
    str
        Dash component prop docstring
    """
    py_type_name = js_to_py_type(
        type_object=type_object, is_flow_type=is_flow_type, indent_num=indent_num
    )
    indent_spacing = "  " * indent_num

    default = default["value"] if default else ""
    default = fix_keywords(default)

    is_required = "optional"
    if required:
        is_required = "required"
    elif default and default not in ["None", "{}", "[]"]:
        is_required = "default " + default.replace("\n", "")

    # formats description
    period = "." if description else ""
    description = description.strip().strip(".").replace('"', r"\"") + period
    desc_indent = indent_spacing + "    "
    description = fill(
        description,
        initial_indent=desc_indent,
        subsequent_indent=desc_indent,
        break_long_words=False,
        break_on_hyphens=False,
    )
    description = f"\n{description}" if description else ""
    colon = ":" if description else ""
    description = fix_keywords(description)

    if "\n" in py_type_name:
        # corrects the type
        dict_or_list = "list of dicts" if py_type_name.startswith("list") else "dict"

        # format and rewrite the intro to the nested dicts
        intro1, intro2, dict_descr = py_type_name.partition("with keys:")
        intro = f"`{prop_name}` is a {intro1}{intro2}"
        intro = fill(
            intro,
            initial_indent=desc_indent,
            subsequent_indent=desc_indent,
            break_long_words=False,
            break_on_hyphens=False,
        )

        # captures optional nested dict description and puts the "or" condition on a new line
        if "| dict with keys:" in dict_descr:
            dict_part1, dict_part2 = dict_descr.split(" |", 1)
            dict_part2 = "".join([desc_indent, "Or", dict_part2])
            dict_descr = f"{dict_part1}\n\n  {dict_part2}"

        # ensures indent is correct if there is a second nested list of dicts
        current_indent = dict_descr.lstrip("\n").find("-")
        if current_indent == len(indent_spacing):
            dict_descr = "".join(
                "\n\n    " + line for line in dict_descr.splitlines() if line != ""
            )

        return (
            f"\n{indent_spacing}- {prop_name} ({dict_or_list}; {is_required}){colon}"
            f"{description}"
            f"\n\n{intro}{dict_descr}"
        )
    tn = f"{py_type_name}; " if py_type_name else ""
    return f"\n{indent_spacing}- {prop_name} ({tn}{is_required}){colon}{description}"


def map_js_to_py_types_prop_types(type_object, indent_num):
    """Mapping from the PropTypes js type object to the Python type."""

    def shape_or_exact():
        return "dict with keys:\n" + "\n".join(
            create_prop_docstring(
                prop_name=prop_name,
                type_object=prop,
                required=prop["required"],
                description=prop.get("description", ""),
                default=prop.get("defaultValue"),
                indent_num=indent_num + 2,
            )
            for prop_name, prop in type_object["value"].items()
        )

    def array_of():
        inner = js_to_py_type(type_object["value"])
        if inner:
            return "list of " + (
                inner + "s"
                if inner.split(" ")[0] != "dict"
                else inner.replace("dict", "dicts", 1)
            )
        return "list"

    def tuple_of():
        elements = [js_to_py_type(element) for element in type_object["elements"]]
        return f"list of {len(elements)} elements: [{', '.join(elements)}]"

    return dict(
        array=lambda: "list",
        bool=lambda: "boolean",
        number=lambda: "number",
        string=lambda: "string",
        object=lambda: "dict",
        any=lambda: "boolean | number | string | dict | list",
        element=lambda: "dash component",
        node=lambda: "a list of or a singular dash component, string or number",
        # React's PropTypes.oneOf, TypeScript enum & const enum, or TypeScript string literal union
        enum=lambda: (
            "a value equal to: "
            + ", ".join(str(t["value"]) for t in type_object["value"] if t.get("value"))
        ),
        # React's PropTypes.oneOfType
        union=lambda: " | ".join(
            js_to_py_type(subType)
            for subType in type_object["value"]
            if js_to_py_type(subType) != ""
        ),
        # React's PropTypes.arrayOf
        arrayOf=array_of,
        # React's PropTypes.objectOf
        objectOf=lambda: (
            "dict with strings as keys and values of type "
            + js_to_py_type(type_object["value"])
        ),
        # React's PropTypes.shape
        shape=shape_or_exact,
        # React's PropTypes.exact
        exact=shape_or_exact,
        tuple=tuple_of,
    )


def map_js_to_py_types_flow_types(type_object):
    """Mapping from the Flow js types to the Python type."""
    return dict(
        array=lambda: "list",
        boolean=lambda: "boolean",
        number=lambda: "number",
        string=lambda: "string",
        Object=lambda: "dict",
        any=lambda: "bool | number | str | dict | list",
        Element=lambda: "dash component",
        Node=lambda: "a list of or a singular dash component, string or number",
        # React's PropTypes.oneOfType
        union=lambda: " | ".join(
            js_to_py_type(subType)
            for subType in type_object["elements"]
            if js_to_py_type(subType) != ""
        ),
        # Flow's Array type
        Array=lambda: "list"
        + (
            f' of {js_to_py_type(type_object["elements"][0])}s'
            if js_to_py_type(type_object["elements"][0]) != ""
            else ""
        ),
        # React's PropTypes.shape
        signature=lambda indent_num: (
            "dict with keys:\n"
            + "\n".join(
                create_prop_docstring(
                    prop_name=prop["key"],
                    type_object=prop["value"],
                    required=prop["value"]["required"],
                    description=prop["value"].get("description", ""),
                    default=prop.get("defaultValue"),
                    indent_num=indent_num + 2,
                    is_flow_type=True,
                )
                for prop in type_object["signature"]["properties"]
            )
        ),
    )


def js_to_py_type(type_object, is_flow_type=False, indent_num=0):
    """Convert JS types to Python types for the component definition.
    Parameters
    ----------
    type_object: dict
        react-docgen-generated prop type dictionary
    is_flow_type: bool
        Does the prop use Flow types? Otherwise, uses PropTypes
    indent_num: int
        Number of indents to use for the docstring for the prop
    Returns
    -------
    str
        Python type string
    """

    js_type_name = type_object["name"]
    js_to_py_types = (
        map_js_to_py_types_flow_types(type_object=type_object)
        if is_flow_type
        else map_js_to_py_types_prop_types(
            type_object=type_object, indent_num=indent_num
        )
    )

    if (
        "computed" in type_object
        and type_object["computed"]
        or type_object.get("type", "") == "function"
    ):
        return ""
    if js_type_name in js_to_py_types:
        if js_type_name == "signature":  # This is a Flow object w/ signature
            return js_to_py_types[js_type_name](indent_num)
        # All other types
        return js_to_py_types[js_type_name]()
    return ""
