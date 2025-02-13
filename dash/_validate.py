import sys
from collections.abc import MutableSequence
import re
from textwrap import dedent
from keyword import iskeyword
import flask

from ._grouping import grouping_len, map_grouping
from ._no_update import NoUpdate
from .development.base_component import Component
from . import exceptions
from ._utils import (
    patch_collections_abc,
    stringify_id,
    to_json,
    coerce_to_list,
    clean_property_name,
)


def validate_callback(outputs, inputs, state, extra_args, types):
    Input, Output, State = types
    if extra_args:
        if not isinstance(extra_args[0], (Output, Input, State)):
            raise exceptions.IncorrectTypeException(
                dedent(
                    f"""
                    Callback arguments must be `Output`, `Input`, or `State` objects,
                    optionally wrapped in a list or tuple. We found (possibly after
                    unwrapping a list or tuple):
                    {repr(extra_args[0])}
                    """
                )
            )

        raise exceptions.IncorrectTypeException(
            dedent(
                f"""
                In a callback definition, you must provide all Outputs first,
                then all Inputs, then all States. After this item:
                {(outputs + inputs + state)[-1]!r}
                we found this item next:
                {extra_args[0]!r}
                """
            )
        )

    for args in [outputs, inputs, state]:
        for arg in args:
            validate_callback_arg(arg)


def validate_callback_arg(arg):
    if not isinstance(getattr(arg, "component_property", None), str):
        raise exceptions.IncorrectTypeException(
            dedent(
                f"""
                component_property must be a string, found {arg.component_property!r}
                """
            )
        )

    if hasattr(arg, "component_event"):
        raise exceptions.NonExistentEventException(
            """
            Events have been removed.
            Use the associated property instead.
            """
        )

    if isinstance(arg.component_id, dict):
        validate_id_dict(arg)

    elif isinstance(arg.component_id, str):
        validate_id_string(arg)

    else:
        raise exceptions.IncorrectTypeException(
            dedent(
                f"""
                component_id must be a string or dict, found {arg.component_id!r}
                """
            )
        )


def validate_id_dict(arg):
    arg_id = arg.component_id

    for k in arg_id:
        # Need to keep key type validation on the Python side, since
        # non-string keys will be converted to strings in json.dumps and may
        # cause unwanted collisions
        if not isinstance(k, str):
            raise exceptions.IncorrectTypeException(
                dedent(
                    f"""
                    Wildcard ID keys must be non-empty strings,
                    found {k!r} in id {arg_id!r}
                    """
                )
            )


def validate_id_string(arg):
    arg_id = arg.component_id

    invalid_chars = ".{"
    invalid_found = [x for x in invalid_chars if x in arg_id]
    if invalid_found:
        raise exceptions.InvalidComponentIdError(
            f"""
            The element `{arg_id}` contains `{"`, `".join(invalid_found)}` in its ID.
            Characters `{"`, `".join(invalid_chars)}` are not allowed in IDs.
            """
        )


def validate_output_spec(output, output_spec, Output):
    """
    This validation is for security and internal debugging, not for users,
    so the messages are not intended to be clear.
    `output` comes from the callback definition, `output_spec` from the request.
    """
    if not isinstance(output, (list, tuple)):
        output, output_spec = [output], [output_spec]
    elif len(output) != len(output_spec):
        raise exceptions.CallbackException("Wrong length output_spec")

    for outi, speci in zip(output, output_spec):
        speci_list = speci if isinstance(speci, (list, tuple)) else [speci]
        for specij in speci_list:
            if (
                not Output(specij["id"], clean_property_name(specij["property"]))
                == outi
            ):
                raise exceptions.CallbackException(
                    "Output does not match callback definition"
                )


def validate_and_group_input_args(flat_args, arg_index_grouping):
    if grouping_len(arg_index_grouping) != len(flat_args):
        raise exceptions.CallbackException("Inputs do not match callback definition")

    args_grouping = map_grouping(lambda ind: flat_args[ind], arg_index_grouping)
    if isinstance(arg_index_grouping, dict):
        func_args = []
        func_kwargs = args_grouping
        for key in func_kwargs:
            if not key.isidentifier():
                raise exceptions.CallbackException(
                    f"{key} is not a valid Python variable name"
                )
    elif isinstance(arg_index_grouping, (tuple, list)):
        func_args = list(args_grouping)
        func_kwargs = {}
    else:
        # Scalar input
        func_args = [args_grouping]
        func_kwargs = {}

    return func_args, func_kwargs


def validate_multi_return(output_lists, output_values, callback_id):
    if not isinstance(output_values, (list, tuple)):
        raise exceptions.InvalidCallbackReturnValue(
            dedent(
                f"""
                The callback {callback_id} is a multi-output.
                Expected the output type to be a list or tuple but got:
                {output_values!r}.
                """
            )
        )

    if len(output_values) != len(output_lists):
        raise exceptions.InvalidCallbackReturnValue(
            f"""
            Invalid number of output values for {callback_id}.
            Expected {len(output_lists)}, got {len(output_values)}
            """
        )

    for i, output_spec in enumerate(output_lists):
        if isinstance(output_spec, list):
            output_value = output_values[i]
            if not isinstance(output_value, (list, tuple)):
                raise exceptions.InvalidCallbackReturnValue(
                    dedent(
                        f"""
                        The callback {callback_id} output {i} is a wildcard multi-output.
                        Expected the output type to be a list or tuple but got:
                        {output_value!r}.
                        output spec: {output_spec!r}
                        """
                    )
                )

            if len(output_value) != len(output_spec):
                raise exceptions.InvalidCallbackReturnValue(
                    dedent(
                        f"""
                        Invalid number of output values for {callback_id} item {i}.
                        Expected {len(output_spec)}, got {len(output_value)}
                        output spec: {output_spec!r}
                        output value: {output_value!r}
                        """
                    )
                )


def fail_callback_output(output_value, output):
    valid_children = (str, int, float, type(None), Component, NoUpdate)
    valid_props = (str, int, float, type(None), tuple, MutableSequence, NoUpdate)

    def _raise_invalid(bad_val, outer_val, path, index=None, toplevel=False):
        bad_type = type(bad_val).__name__
        outer_id = f"(id={outer_val.id:s})" if getattr(outer_val, "id", False) else ""
        outer_type = type(outer_val).__name__
        if toplevel:
            location = dedent(
                """
                The value in question is either the only value returned,
                or is in the top level of the returned list,
                """
            )
        else:
            index_string = "[*]" if index is None else f"[{index:d}]"
            location = dedent(
                f"""
                The value in question is located at
                {index_string} {outer_type} {outer_id}
                {path},
                """
            )

        obj = "tree with one value" if not toplevel else "value"
        raise exceptions.InvalidCallbackReturnValue(
            dedent(
                f"""
                The callback for `{output!r}`
                returned a {obj:s} having type `{bad_type}`
                which is not JSON serializable.

                {location}
                and has string representation
                `{bad_val}`

                In general, Dash properties can only be
                dash components, strings, dictionaries, numbers, None,
                or lists of those.
                """
            )
        )

    def _valid_child(val):
        return isinstance(val, valid_children)

    def _valid_prop(val):
        return isinstance(val, valid_props)

    def _can_serialize(val):
        if not (_valid_child(val) or _valid_prop(val)):
            return False
        try:
            to_json(val)
        except TypeError:
            return False
        return True

    def _validate_value(val, index=None):
        # val is a Component
        if isinstance(val, Component):
            unserializable_items = []
            # pylint: disable=protected-access
            for p, j in val._traverse_with_paths():
                # check each component value in the tree
                if not _valid_child(j):
                    _raise_invalid(bad_val=j, outer_val=val, path=p, index=index)

                if not _can_serialize(j):
                    # collect unserializable items separately, so we can report
                    # only the deepest level, not all the parent components that
                    # are just unserializable because of their children.
                    unserializable_items = [
                        i for i in unserializable_items if not p.startswith(i[0])
                    ]
                    if unserializable_items:
                        # we already have something unserializable in a different
                        # branch - time to stop and fail
                        break
                    if all(not i[0].startswith(p) for i in unserializable_items):
                        unserializable_items.append((p, j))

                # Children that are not of type Component or
                # list/tuple not returned by traverse
                child = getattr(j, "children", None)
                if not isinstance(child, (tuple, MutableSequence)):
                    if child and not _can_serialize(child):
                        _raise_invalid(
                            bad_val=child,
                            outer_val=val,
                            path=p + "\n" + "[*] " + type(child).__name__,
                            index=index,
                        )
            if unserializable_items:
                p, j = unserializable_items[0]
                # just report the first one, even if there are multiple,
                # as that's how all the other errors work
                _raise_invalid(bad_val=j, outer_val=val, path=p, index=index)

            # Also check the child of val, as it will not be returned
            child = getattr(val, "children", None)
            if not isinstance(child, (tuple, MutableSequence)):
                if child and not _can_serialize(val):
                    _raise_invalid(
                        bad_val=child,
                        outer_val=val,
                        path=type(child).__name__,
                        index=index,
                    )

        if not _can_serialize(val):
            _raise_invalid(
                bad_val=val,
                outer_val=type(val).__name__,
                path="",
                index=index,
                toplevel=True,
            )

    if isinstance(output_value, list):
        for i, val in enumerate(output_value):
            _validate_value(val, index=i)
    else:
        _validate_value(output_value)

    # if we got this far, raise a generic JSON error
    raise exceptions.InvalidCallbackReturnValue(
        f"""
        The callback for output `{output!r}`
        returned a value which is not JSON serializable.

        In general, Dash properties can only be dash components, strings,
        dictionaries, numbers, None, or lists of those.
        """
    )


def check_obsolete(kwargs):
    for key in kwargs:
        if key in ["components_cache_max_age", "static_folder"]:
            raise exceptions.ObsoleteKwargException(
                f"""
                {key} is no longer a valid keyword argument in Dash since v1.0.
                See https://dash.plotly.com for details.
                """
            )
        if key in ["dynamic_loading", "preloaded_libraries"]:
            # Only warns as this was only available for a short time.
            print(
                f"{key} has been removed and no longer a valid keyword argument in Dash.",
                file=sys.stderr,
            )
            continue
        # any other kwarg mimic the built-in exception
        raise TypeError(f"Dash() got an unexpected keyword argument '{key}'")


def validate_js_path(registered_paths, package_name, path_in_package_dist):
    if package_name not in registered_paths:
        raise exceptions.DependencyException(
            f"""
            Error loading dependency. "{package_name}" is not a registered library.
            Registered libraries are:
            {list(registered_paths.keys())}
            """
        )

    if path_in_package_dist not in registered_paths[package_name]:
        raise exceptions.DependencyException(
            f"""
            "{package_name}" is registered but the path requested is not valid.
            The path requested: "{path_in_package_dist}"
            List of registered paths: {registered_paths}
            """
        )


def validate_index(name, checks, index):
    missing = [i for check, i in checks if not re.compile(check).search(index)]
    if missing:
        plural = "s" if len(missing) > 1 else ""
        raise exceptions.InvalidIndexException(
            f"Missing item{plural} {', '.join(missing)} in {name}."
        )


def validate_layout_type(value):
    if not isinstance(
        value, (Component, patch_collections_abc("Callable"), list, tuple)
    ):
        raise exceptions.NoLayoutException(
            """
            Layout must be a single dash component, a list of dash components,
            or a function that returns a dash component.
            """
        )


def validate_layout(layout, layout_value):
    if layout is None:
        raise exceptions.NoLayoutException(
            """
            The layout was `None` at the time that `run_server` was called.
            Make sure to set the `layout` attribute of your application
            before running the server.
            """
        )

    component_ids = set()

    def _validate(value):
        def _validate_id(comp):
            component_id = stringify_id(getattr(comp, "id", None))
            if component_id and component_id in component_ids:
                raise exceptions.DuplicateIdError(
                    f"""
                    Duplicate component id found in the initial layout: `{component_id}`
                    """
                )
            component_ids.add(component_id)

        _validate_id(value)

        for component in value._traverse():  # pylint: disable=protected-access
            _validate_id(component)

    if isinstance(layout_value, (list, tuple)):
        for component in layout_value:
            if isinstance(component, (str,)):
                continue
            if isinstance(component, (Component,)):
                _validate(component)
            else:
                raise exceptions.NoLayoutException(
                    "Only strings and components are allowed in a list layout."
                )
    else:
        _validate(layout_value)


def validate_template(template):
    variable_names = re.findall("<(.*?)>", template)

    for name in variable_names:
        if not name.isidentifier() or iskeyword(name):
            raise Exception(
                f'`{name}` is not a valid Python variable name in `path_template`: "{template}".'
            )


def check_for_duplicate_pathnames(registry):
    path_to_module = {}
    for page in registry.values():
        if page["path"] not in path_to_module:
            path_to_module[page["path"]] = [page["module"]]
        else:
            path_to_module[page["path"]].append(page["module"])

    for modules in path_to_module.values():
        if len(modules) > 1:
            raise Exception(f"modules {modules} have duplicate paths")


def validate_registry(registry):
    for page in registry.values():
        if "layout" not in page:
            raise exceptions.NoLayoutException(
                f"No layout in module `{page['module']}` in dash.page_registry"
            )
        if page["module"] == "__main__":
            raise Exception(
                """
                When registering pages from app.py, `__name__` is not a valid module name.  Use a string instead.
                For example, `dash.register_page("my_module_name")`, rather than `dash.register_page(__name__)`
                """
            )


def validate_pages_layout(module, page):
    if not hasattr(page, "layout"):
        raise exceptions.NoLayoutException(
            f"""
            No layout found in module {module}
            A variable or a function named "layout" is required.
            """
        )


def validate_use_pages(config):
    if not config.get("assets_folder", None):
        raise exceptions.PageError(
            "`dash.register_page()` must be called after app instantiation"
        )

    if flask.has_request_context():
        raise exceptions.PageError(
            """
            dash.register_page() can’t be called within a callback as it updates dash.page_registry, which is a global variable.
             For more details, see https://dash.plotly.com/sharing-data-between-callbacks#why-global-variables-will-break-your-app
            """
        )


def validate_module_name(module):
    if not isinstance(module, str):
        raise exceptions.PageError(
            "The first attribute of dash.register_page() must be a string or '__name__'"
        )
    return module


def validate_long_callbacks(callback_map):
    # Validate that long callback side output & inputs are not circular
    # If circular, triggering a long callback would result in a fatal server/computer crash.
    all_outputs = set()
    input_indexed = {}
    for callback in callback_map.values():
        out = coerce_to_list(callback["output"])
        all_outputs.update(out)
        for o in out:
            input_indexed.setdefault(o, set())
            input_indexed[o].update(coerce_to_list(callback["raw_inputs"]))

    for callback in (x for x in callback_map.values() if x.get("long")):
        long_info = callback["long"]
        progress = long_info.get("progress", [])
        running = long_info.get("running", [])

        long_inputs = coerce_to_list(callback["raw_inputs"])
        outputs = set([x[0] for x in running] + progress)
        circular = [
            x
            for x in set(k for k, v in input_indexed.items() if v.intersection(outputs))
            if x in long_inputs
        ]

        if circular:
            raise exceptions.LongCallbackError(
                f"Long callback circular error!\n{circular} is used as input for a long callback"
                f" but also used as output from an input that is updated with progress or running argument."
            )


def validate_duplicate_output(
    output, prevent_initial_call, config_prevent_initial_call
):
    if "initial_duplicate" in (prevent_initial_call, config_prevent_initial_call):
        return

    def _valid(out):
        if (
            out.allow_duplicate
            and not prevent_initial_call
            and not config_prevent_initial_call
        ):
            raise exceptions.DuplicateCallback(
                "allow_duplicate requires prevent_initial_call to be True. The order of the call is not"
                " guaranteed to be the same on every page load. "
                "To enable duplicate callback with initial call, set prevent_initial_call='initial_duplicate' "
                " or globally in the config prevent_initial_callbacks='initial_duplicate'"
            )

    if isinstance(output, (list, tuple)):
        for o in output:
            _valid(o)

        return

    _valid(output)
