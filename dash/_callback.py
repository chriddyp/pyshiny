import collections
import hashlib
from functools import wraps

from typing import Callable, Optional, Any, List, Tuple, Union


import flask

from .dependencies import (
    handle_callback_args,
    handle_grouped_callback_args,
    Output,
    ClientsideFunction,
    Input,
)
from .development.base_component import ComponentRegistry
from .exceptions import (
    InvalidCallbackReturnValue,
    PreventUpdate,
    WildcardInLongCallback,
    MissingLongCallbackManagerError,
    BackgroundCallbackError,
    ImportedInsideCallbackError,
)

from ._grouping import (
    flatten_grouping,
    make_grouping_by_index,
    grouping_len,
)
from ._utils import (
    create_callback_id,
    stringify_id,
    to_json,
    coerce_to_list,
    AttributeDict,
    clean_property_name,
)

from . import _validate
from .background_callback.managers import BaseBackgroundCallbackManager
from ._callback_context import context_value


def _invoke_callback(func, *args, **kwargs):  # used to mark the frame for the debugger
    return func(*args, **kwargs)  # %% callback invoked %%


class NoUpdate:
    def to_plotly_json(self):  # pylint: disable=no-self-use
        return {"_dash_no_update": "_dash_no_update"}

    @staticmethod
    def is_no_update(obj):
        return isinstance(obj, NoUpdate) or (
            isinstance(obj, dict) and obj == {"_dash_no_update": "_dash_no_update"}
        )


GLOBAL_CALLBACK_LIST = []
GLOBAL_CALLBACK_MAP = {}
GLOBAL_INLINE_SCRIPTS = []


# pylint: disable=too-many-locals
def callback(
    *_args,
    background: bool = False,
    interval: int = 1000,
    progress: Optional[Union[List[Output], Output]] = None,
    progress_default: Any = None,
    running: Optional[List[Tuple[Output, Any, Any]]] = None,
    cancel: Optional[Union[List[Input], Input]] = None,
    manager: Optional[BaseBackgroundCallbackManager] = None,
    cache_args_to_ignore: Optional[list] = None,
    on_error: Optional[Callable[[Exception], Any]] = None,
    **_kwargs,
):
    """
    Normally used as a decorator, `@dash.callback` provides a server-side
    callback relating the values of one or more `Output` items to one or
    more `Input` items which will trigger the callback when they change,
    and optionally `State` items which provide additional information but
    do not trigger the callback directly.

    `@dash.callback` is an alternative to `@app.callback` (where `app = dash.Dash()`)
    introduced in Dash 2.0.
    It allows you to register callbacks without defining or importing the `app`
    object. The call signature is identical and it can be used instead of `app.callback`
    in all cases.

    The last, optional argument `prevent_initial_call` causes the callback
    not to fire when its outputs are first added to the page. Defaults to
    `False` and unlike `app.callback` is not configurable at the app level.

    :Keyword Arguments:
        :param background:
            Mark the callback as a background callback to execute in a manager for
            callbacks that take a long time without locking up the Dash app
            or timing out.
        :param manager:
            A background callback manager instance. Currently, an instance of one of
            `DiskcacheManager` or `CeleryManager`.
            Defaults to the `background_callback_manager` instance provided to the
            `dash.Dash constructor`.
            - A diskcache manager (`DiskcacheManager`) that runs callback
              logic in a separate process and stores the results to disk using the
              diskcache library. This is the easiest backend to use for local
              development.
            - A Celery manager (`CeleryManager`) that runs callback logic
              in a celery worker and returns results to the Dash app through a Celery
              broker like RabbitMQ or Redis.
        :param running:
            A list of 3-element tuples. The first element of each tuple should be
            an `Output` dependency object referencing a property of a component in
            the app layout. The second element is the value that the property
            should be set to while the callback is running, and the third element
            is the value the property should be set to when the callback completes.
        :param cancel:
            A list of `Input` dependency objects that reference a property of a
            component in the app's layout.  When the value of this property changes
            while a callback is running, the callback is canceled.
            Note that the value of the property is not significant, any change in
            value will result in the cancellation of the running job (if any).
        :param progress:
            An `Output` dependency grouping that references properties of
            components in the app's layout. When provided, the decorated function
            will be called with an extra argument as the first argument to the
            function.  This argument, is a function handle that the decorated
            function should call in order to provide updates to the app on its
            current progress. This function accepts a single argument, which
            correspond to the grouping of properties specified in the provided
            `Output` dependency grouping
        :param progress_default:
            A grouping of values that should be assigned to the components
            specified by the `progress` argument when the callback is not in
            progress. If `progress_default` is not provided, all the dependency
            properties specified in `progress` will be set to `None` when the
            callback is not running.
        :param cache_args_to_ignore:
            Arguments to ignore when caching is enabled. If callback is configured
            with keyword arguments (Input/State provided in a dict),
            this should be a list of argument names as strings. Otherwise,
            this should be a list of argument indices as integers.
        :param interval:
            Time to wait between the background callback update requests.
        :param on_error:
            Function to call when the callback raises an exception. Receives the
            exception object as first argument. The callback_context can be used
            to access the original callback inputs, states and output.
    """

    background_spec = None

    config_prevent_initial_callbacks = _kwargs.pop(
        "config_prevent_initial_callbacks", False
    )
    callback_map = _kwargs.pop("callback_map", GLOBAL_CALLBACK_MAP)
    callback_list = _kwargs.pop("callback_list", GLOBAL_CALLBACK_LIST)

    if background:
        background_spec: Any = {
            "interval": interval,
        }

        if manager:
            background_spec["manager"] = manager

        if progress:
            background_spec["progress"] = coerce_to_list(progress)
            validate_background_inputs(background_spec["progress"])

        if progress_default:
            background_spec["progressDefault"] = coerce_to_list(progress_default)

            if not len(background_spec["progress"]) == len(
                background_spec["progressDefault"]
            ):
                raise Exception(
                    "Progress and progress default needs to be of same length"
                )

        if cancel:
            cancel_inputs = coerce_to_list(cancel)
            validate_background_inputs(cancel_inputs)

            background_spec["cancel"] = [c.to_dict() for c in cancel_inputs]
            background_spec["cancel_inputs"] = cancel_inputs

        if cache_args_to_ignore:
            background_spec["cache_args_to_ignore"] = cache_args_to_ignore

    return register_callback(
        callback_list,
        callback_map,
        config_prevent_initial_callbacks,
        *_args,
        **_kwargs,
        background=background_spec,
        manager=manager,
        running=running,
        on_error=on_error,
    )


def validate_background_inputs(deps):
    for dep in deps:
        if dep.has_wildcard():
            raise WildcardInLongCallback(
                f"""
                background callbacks does not support dependencies with
                pattern-matching ids
                    Received: {repr(dep)}\n"""
            )


ClientsideFuncType = Union[str, ClientsideFunction]


def clientside_callback(clientside_function: ClientsideFuncType, *args, **kwargs):
    return register_clientside_callback(
        GLOBAL_CALLBACK_LIST,
        GLOBAL_CALLBACK_MAP,
        False,
        GLOBAL_INLINE_SCRIPTS,
        clientside_function,
        *args,
        **kwargs,
    )


# pylint: disable=too-many-arguments
def insert_callback(
    callback_list,
    callback_map,
    config_prevent_initial_callbacks,
    output,
    outputs_indices,
    inputs,
    state,
    inputs_state_indices,
    prevent_initial_call,
    background=None,
    manager=None,
    running=None,
    dynamic_creator: Optional[bool] = False,
    no_output=False,
):
    if prevent_initial_call is None:
        prevent_initial_call = config_prevent_initial_callbacks

    _validate.validate_duplicate_output(
        output, prevent_initial_call, config_prevent_initial_callbacks
    )

    callback_id = create_callback_id(output, inputs, no_output)
    callback_spec = {
        "output": callback_id,
        "inputs": [c.to_dict() for c in inputs],
        "state": [c.to_dict() for c in state],
        "clientside_function": None,
        # prevent_initial_call can be a string "initial_duplicates"
        # which should not prevent the initial call.
        "prevent_initial_call": prevent_initial_call is True,
        "background": background
        and {
            "interval": background["interval"],
        },
        "dynamic_creator": dynamic_creator,
        "no_output": no_output,
    }
    if running:
        callback_spec["running"] = running

    callback_map[callback_id] = {
        "inputs": callback_spec["inputs"],
        "state": callback_spec["state"],
        "outputs_indices": outputs_indices,
        "inputs_state_indices": inputs_state_indices,
        "background": background,
        "output": output,
        "raw_inputs": inputs,
        "manager": manager,
        "allow_dynamic_callbacks": dynamic_creator,
        "no_output": no_output,
    }
    callback_list.append(callback_spec)

    return callback_id


def _set_side_update(ctx, response) -> bool:
    side_update = dict(ctx.updated_props)
    if len(side_update) > 0:
        response["sideUpdate"] = side_update
        return True
    return False


# pylint: disable=too-many-branches,too-many-statements
def register_callback(
    callback_list, callback_map, config_prevent_initial_callbacks, *_args, **_kwargs
):
    (
        output,
        flat_inputs,
        flat_state,
        inputs_state_indices,
        prevent_initial_call,
    ) = handle_grouped_callback_args(_args, _kwargs)
    if isinstance(output, Output):
        # Insert callback with scalar (non-multi) Output
        insert_output = output
        multi = False
        has_output = True
    else:
        # Insert callback as multi Output
        insert_output = flatten_grouping(output)
        multi = True
        has_output = len(output) > 0

    background = _kwargs.get("background")
    manager = _kwargs.get("manager")
    running = _kwargs.get("running")
    on_error = _kwargs.get("on_error")
    if running is not None:
        if not isinstance(running[0], (list, tuple)):
            running = [running]
        running = {
            "running": {str(r[0]): r[1] for r in running},
            "runningOff": {str(r[0]): r[2] for r in running},
        }
    allow_dynamic_callbacks = _kwargs.get("_allow_dynamic_callbacks")

    output_indices = make_grouping_by_index(output, list(range(grouping_len(output))))
    callback_id = insert_callback(
        callback_list,
        callback_map,
        config_prevent_initial_callbacks,
        insert_output,
        output_indices,
        flat_inputs,
        flat_state,
        inputs_state_indices,
        prevent_initial_call,
        background=background,
        manager=manager,
        dynamic_creator=allow_dynamic_callbacks,
        running=running,
        no_output=not has_output,
    )

    # pylint: disable=too-many-locals
    def wrap_func(func):

        if background is not None:
            background_key = BaseBackgroundCallbackManager.register_func(
                func,
                background.get("progress") is not None,
                callback_id,
            )

        @wraps(func)
        def add_context(*args, **kwargs):
            output_spec = kwargs.pop("outputs_list")
            app_callback_manager = kwargs.pop("background_callback_manager", None)

            callback_ctx = kwargs.pop(
                "callback_context", AttributeDict({"updated_props": {}})
            )
            app = kwargs.pop("app", None)
            callback_manager = background and background.get(
                "manager", app_callback_manager
            )
            error_handler = on_error or kwargs.pop("app_on_error", None)
            original_packages = set(ComponentRegistry.registry)

            if has_output:
                _validate.validate_output_spec(insert_output, output_spec, Output)

            context_value.set(callback_ctx)

            func_args, func_kwargs = _validate.validate_and_group_input_args(
                args, inputs_state_indices
            )

            response: dict = {"multi": True}
            has_update = False

            if background is not None:
                if not callback_manager:
                    raise MissingLongCallbackManagerError(
                        "Running `background` callbacks requires a manager to be installed.\n"
                        "Available managers:\n"
                        "- Diskcache (`pip install dash[diskcache]`) to run callbacks in a separate Process"
                        " and store results on the local filesystem.\n"
                        "- Celery (`pip install dash[celery]`) to run callbacks in a celery worker"
                        " and store results on redis.\n"
                    )

                progress_outputs = background.get("progress")
                cache_key = flask.request.args.get("cacheKey")
                job_id = flask.request.args.get("job")
                old_job = flask.request.args.getlist("oldJob")

                current_key = callback_manager.build_cache_key(
                    func,
                    # Inputs provided as dict is kwargs.
                    func_args if func_args else func_kwargs,
                    background.get("cache_args_to_ignore", []),
                )

                if old_job:
                    for job in old_job:
                        callback_manager.terminate_job(job)

                if not cache_key:
                    cache_key = current_key

                    job_fn = callback_manager.func_registry.get(background_key)

                    ctx_value = AttributeDict(**context_value.get())
                    ctx_value.ignore_register_page = True
                    ctx_value.pop("background_callback_manager")
                    ctx_value.pop("dash_response")

                    job = callback_manager.call_job_fn(
                        cache_key,
                        job_fn,
                        func_args if func_args else func_kwargs,
                        ctx_value,
                    )

                    data = {
                        "cacheKey": cache_key,
                        "job": job,
                    }

                    cancel = background.get("cancel")
                    if cancel:
                        data["cancel"] = cancel

                    progress_default = background.get("progressDefault")
                    if progress_default:
                        data["progressDefault"] = {
                            str(o): x
                            for o, x in zip(progress_outputs, progress_default)
                        }
                    return to_json(data)
                if progress_outputs:
                    # Get the progress before the result as it would be erased after the results.
                    progress = callback_manager.get_progress(cache_key)
                    if progress:
                        response["progress"] = {
                            str(x): progress[i] for i, x in enumerate(progress_outputs)
                        }

                output_value = callback_manager.get_result(cache_key, job_id)
                # Must get job_running after get_result since get_results terminates it.
                job_running = callback_manager.job_running(job_id)
                if not job_running and output_value is callback_manager.UNDEFINED:
                    # Job canceled -> no output to close the loop.
                    output_value = NoUpdate()

                elif (
                    isinstance(output_value, dict)
                    and "background_callback_error" in output_value
                ):
                    error = output_value.get("background_callback_error", {})
                    exc = BackgroundCallbackError(
                        f"An error occurred inside a background callback: {error['msg']}\n{error['tb']}"
                    )
                    if error_handler:
                        output_value = error_handler(exc)

                        if output_value is None:
                            output_value = NoUpdate()
                        # set_props from the error handler uses the original ctx
                        # instead of manager.get_updated_props since it runs in the
                        # request process.
                        has_update = (
                            _set_side_update(callback_ctx, response)
                            or output_value is not None
                        )
                    else:
                        raise exc

                if job_running and output_value is not callback_manager.UNDEFINED:
                    # cached results.
                    callback_manager.terminate_job(job_id)

                if multi and isinstance(output_value, (list, tuple)):
                    output_value = [
                        NoUpdate() if NoUpdate.is_no_update(r) else r
                        for r in output_value
                    ]
                updated_props = callback_manager.get_updated_props(cache_key)
                if len(updated_props) > 0:
                    response["sideUpdate"] = updated_props
                    has_update = True

                if output_value is callback_manager.UNDEFINED:
                    return to_json(response)
            else:
                try:
                    output_value = _invoke_callback(func, *func_args, **func_kwargs)
                except PreventUpdate as err:
                    raise err
                except Exception as err:  # pylint: disable=broad-exception-caught
                    if error_handler:
                        output_value = error_handler(err)

                        # If the error returns nothing, automatically puts NoUpdate for response.
                        if output_value is None and has_output:
                            output_value = NoUpdate()
                    else:
                        raise err

            component_ids = collections.defaultdict(dict)

            if has_output:
                if not multi:
                    output_value, output_spec = [output_value], [output_spec]
                    flat_output_values = output_value
                else:
                    if isinstance(output_value, (list, tuple)):
                        # For multi-output, allow top-level collection to be
                        # list or tuple
                        output_value = list(output_value)

                    if NoUpdate.is_no_update(output_value):
                        flat_output_values = [output_value]
                    else:
                        # Flatten grouping and validate grouping structure
                        flat_output_values = flatten_grouping(output_value, output)

                if not NoUpdate.is_no_update(output_value):
                    _validate.validate_multi_return(
                        output_spec, flat_output_values, callback_id
                    )

                for val, spec in zip(flat_output_values, output_spec):
                    if NoUpdate.is_no_update(val):
                        continue
                    for vali, speci in (
                        zip(val, spec) if isinstance(spec, list) else [[val, spec]]
                    ):
                        if not NoUpdate.is_no_update(vali):
                            has_update = True
                            id_str = stringify_id(speci["id"])
                            prop = clean_property_name(speci["property"])
                            component_ids[id_str][prop] = vali
            else:
                if output_value is not None:
                    raise InvalidCallbackReturnValue(
                        f"No-output callback received return value: {output_value}"
                    )
                output_value = []
                flat_output_values = []

            if not background:
                has_update = _set_side_update(callback_ctx, response) or has_update

            if not has_update:
                raise PreventUpdate

            response["response"] = component_ids

            if len(ComponentRegistry.registry) != len(original_packages):
                diff_packages = list(
                    set(ComponentRegistry.registry).difference(original_packages)
                )
                if not allow_dynamic_callbacks:
                    raise ImportedInsideCallbackError(
                        f"Component librar{'y' if len(diff_packages) == 1 else 'ies'} was imported during callback.\n"
                        "You can set `_allow_dynamic_callbacks` to allow for development purpose only."
                    )
                dist = app.get_dist(diff_packages)
                response["dist"] = dist

            try:
                jsonResponse = to_json(response)
            except TypeError:
                _validate.fail_callback_output(output_value, output)

            return jsonResponse

        callback_map[callback_id]["callback"] = add_context

        return func

    return wrap_func


_inline_clientside_template = """
(function() {{
    var clientside = window.dash_clientside = window.dash_clientside || {{}};
    var ns = clientside["{namespace}"] = clientside["{namespace}"] || {{}};
    ns["{function_name}"] = {clientside_function};
}})();
"""


def register_clientside_callback(
    callback_list,
    callback_map,
    config_prevent_initial_callbacks,
    inline_scripts,
    clientside_function: ClientsideFuncType,
    *args,
    **kwargs,
):
    output, inputs, state, prevent_initial_call = handle_callback_args(args, kwargs)
    no_output = isinstance(output, (list,)) and len(output) == 0
    insert_callback(
        callback_list,
        callback_map,
        config_prevent_initial_callbacks,
        output,
        None,
        inputs,
        state,
        None,
        prevent_initial_call,
        no_output=no_output,
    )

    # If JS source is explicitly given, create a namespace and function
    # name, then inject the code.
    if isinstance(clientside_function, str):
        namespace = "_dashprivate_clientside_funcs"
        # Create a hash from the function, it will be the same always
        function_name = hashlib.sha256(clientside_function.encode("utf-8")).hexdigest()

        inline_scripts.append(
            _inline_clientside_template.format(
                namespace=namespace,
                function_name=function_name,
                clientside_function=clientside_function,
            )
        )

    # Callback is stored in an external asset.
    else:
        namespace = clientside_function.namespace
        function_name = clientside_function.function_name

    callback_list[-1]["clientside_function"] = {
        "namespace": namespace,
        "function_name": function_name,
    }
