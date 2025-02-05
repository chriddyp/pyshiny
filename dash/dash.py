import functools
import os
import sys
import collections
import importlib
import warnings
from contextvars import copy_context
from importlib.machinery import ModuleSpec
import pkgutil
import threading
import re
import logging
import time
import mimetypes
import hashlib
import base64
import traceback
from urllib.parse import urlparse
from typing import Any, Callable, Dict, Optional, Union, List

import asyncio
import flask

from importlib_metadata import version as _get_distribution_version

from dash import dcc
from dash import html
from dash import dash_table

from .fingerprint import build_fingerprint, check_fingerprint
from .resources import Scripts, Css
from .dependencies import (
    Input,
    Output,
    State,
)
from .development.base_component import ComponentRegistry
from .exceptions import (
    PreventUpdate,
    InvalidResourceError,
    ProxyError,
    DuplicateCallback,
)
from .version import __version__
from ._configs import get_combined_config, pathname_configs, pages_folder_config
from ._utils import (
    AttributeDict,
    format_tag,
    generate_hash,
    inputs_to_dict,
    inputs_to_vals,
    interpolate_str,
    patch_collections_abc,
    split_callback_id,
    to_json,
    convert_to_AttributeDict,
    gen_salt,
    hooks_to_js_object,
    parse_version,
    get_caller_name,
)
from . import _callback
from . import _get_paths
from . import _dash_renderer
from . import _validate
from . import _watch
from . import _get_app

from ._grouping import map_grouping, grouping_len, update_args_group

from . import _pages
from ._pages import (
    _parse_query_string,
    _page_meta_tags,
    _path_to_page,
    _import_layouts_from_pages,
)
from ._jupyter import jupyter_dash, JupyterDisplayMode
from .types import RendererHooks

# Add explicit mapping for map files
mimetypes.add_type("application/json", ".map", True)

_default_index = """<!DOCTYPE html>
<html>
    <head>
        {%metas%}
        <title>{%title%}</title>
        {%favicon%}
        {%css%}
    </head>
    <body>
        <!--[if IE]><script>
        alert("Dash v2.7+ does not support Internet Explorer. Please use a newer browser.");
        </script><![endif]-->
        {%app_entry%}
        <footer>
            {%config%}
            {%scripts%}
            {%renderer%}
        </footer>
    </body>
</html>"""

_app_entry = """
<div id="react-entry-point">
    <div class="_dash-loading">
        Loading...
    </div>
</div>
"""

_re_index_entry = "{%app_entry%}", "{%app_entry%}"
_re_index_config = "{%config%}", "{%config%}"
_re_index_scripts = "{%scripts%}", "{%scripts%}"

_re_index_entry_id = 'id="react-entry-point"', "#react-entry-point"
_re_index_config_id = 'id="_dash-config"', "#_dash-config"
_re_index_scripts_id = 'src="[^"]*dash[-_]renderer[^"]*"', "dash-renderer"
_re_renderer_scripts_id = 'id="_dash-renderer', "new DashRenderer"


_ID_CONTENT = "_pages_content"
_ID_LOCATION = "_pages_location"
_ID_STORE = "_pages_store"
_ID_DUMMY = "_pages_dummy"

# Handles the case in a newly cloned environment where the components are not yet generated.
try:
    page_container = html.Div(
        [
            dcc.Location(id=_ID_LOCATION, refresh="callback-nav"),
            html.Div(id=_ID_CONTENT, disable_n_clicks=True),
            dcc.Store(id=_ID_STORE),
            html.Div(id=_ID_DUMMY, disable_n_clicks=True),
        ]
    )
# pylint: disable-next=bare-except
except:  # noqa: E722
    page_container = None


def _get_traceback(secret, error: Exception):
    try:
        # pylint: disable=import-outside-toplevel
        from werkzeug.debug import tbtools
    except ImportError:
        tbtools = None

    def _get_skip(error):
        from dash._callback import (  # pylint: disable=import-outside-toplevel
            _invoke_callback,
            _async_invoke_callback,
        )

        tb = error.__traceback__
        skip = 1
        while tb.tb_next is not None:
            skip += 1
            tb = tb.tb_next
            if tb.tb_frame.f_code in [
                _invoke_callback.__code__,
                _async_invoke_callback.__code__,
            ]:
                return skip

        return skip

    def _do_skip(error):
        from dash._callback import (  # pylint: disable=import-outside-toplevel
            _invoke_callback,
            _async_invoke_callback,
        )

        tb = error.__traceback__
        while tb.tb_next is not None:
            if tb.tb_frame.f_code in [
                _invoke_callback.__code__,
                _async_invoke_callback.__code__,
            ]:
                return tb.tb_next
            tb = tb.tb_next
        return error.__traceback__

    # werkzeug<2.1.0
    if hasattr(tbtools, "get_current_traceback"):
        return tbtools.get_current_traceback(  # type: ignore
            skip=_get_skip(error)
        ).render_full()

    if hasattr(tbtools, "DebugTraceback"):
        # pylint: disable=no-member
        return tbtools.DebugTraceback(  # type: ignore
            error, skip=_get_skip(error)
        ).render_debugger_html(True, secret, True)

    return "".join(traceback.format_exception(type(error), error, _do_skip(error)))


# Singleton signal to not update an output, alternative to PreventUpdate
no_update = _callback.NoUpdate()  # pylint: disable=protected-access


async def execute_async_function(func, *args, **kwargs):
    # Check if the function is a coroutine function
    if asyncio.iscoroutinefunction(func):
        return await func(*args, **kwargs)
    # If the function is not a coroutine, call it directly
    return func(*args, **kwargs)


# pylint: disable=too-many-instance-attributes
# pylint: disable=too-many-arguments, too-many-locals
class Dash:
    """Dash is a framework for building analytical web applications.
    No JavaScript required.

    If a parameter can be set by an environment variable, that is listed as:
        env: ``DASH_****``
    Values provided here take precedence over environment variables.

    :param name: The name Flask should use for your app. Even if you provide
        your own ``server``, ``name`` will be used to help find assets.
        Typically ``__name__`` (the magic global var, not a string) is the
        best value to use. Default ``'__main__'``, env: ``DASH_APP_NAME``
    :type name: string

    :param server: Sets the Flask server for your app. There are three options:
        ``True`` (default): Dash will create a new server
        ``False``: The server will be added later via ``app.init_app(server)``
            where ``server`` is a ``flask.Flask`` instance.
        ``flask.Flask``: use this pre-existing Flask server.
    :type server: boolean or flask.Flask

    :param assets_folder: a path, relative to the current working directory,
        for extra files to be used in the browser. Default ``'assets'``.
        All .js and .css files will be loaded immediately unless excluded by
        ``assets_ignore``, and other files such as images will be served if
        requested.
    :type assets_folder: string

    :param pages_folder: a relative or absolute path for pages of a multi-page app.
        Default ``'pages'``.
    :type pages_folder: string or pathlib.Path

    :param use_pages: When True, the ``pages`` feature for multi-page apps is
        enabled. If you set a non-default ``pages_folder`` this will be inferred
        to be True. Default `None`.
    :type use_pages: boolean

    :param include_pages_meta: Include the page meta tags for twitter cards.
    :type include_pages_meta: bool

    :param assets_url_path: The local urls for assets will be:
        ``requests_pathname_prefix + assets_url_path + '/' + asset_path``
        where ``asset_path`` is the path to a file inside ``assets_folder``.
        Default ``'assets'``.
    :type asset_url_path: string

    :param assets_ignore: A regex, as a string to pass to ``re.compile``, for
        assets to omit from immediate loading. Ignored files will still be
        served if specifically requested. You cannot use this to prevent access
        to sensitive files.
    :type assets_ignore: string

    :param assets_external_path: an absolute URL from which to load assets.
        Use with ``serve_locally=False``. assets_external_path is joined
        with assets_url_path to determine the absolute url to the
        asset folder. Dash can still find js and css to automatically load
        if you also keep local copies in your assets folder that Dash can index,
        but external serving can improve performance and reduce load on
        the Dash server.
        env: ``DASH_ASSETS_EXTERNAL_PATH``
    :type assets_external_path: string

    :param include_assets_files: Default ``True``, set to ``False`` to prevent
        immediate loading of any assets. Assets will still be served if
        specifically requested. You cannot use this to prevent access
        to sensitive files. env: ``DASH_INCLUDE_ASSETS_FILES``
    :type include_assets_files: boolean

    :param url_base_pathname: A local URL prefix to use app-wide.
        Default ``'/'``. Both `requests_pathname_prefix` and
        `routes_pathname_prefix` default to `url_base_pathname`.
        env: ``DASH_URL_BASE_PATHNAME``
    :type url_base_pathname: string

    :param requests_pathname_prefix: A local URL prefix for file requests.
        Defaults to `url_base_pathname`, and must end with
        `routes_pathname_prefix`. env: ``DASH_REQUESTS_PATHNAME_PREFIX``
    :type requests_pathname_prefix: string

    :param routes_pathname_prefix: A local URL prefix for JSON requests.
        Defaults to ``url_base_pathname``, and must start and end
        with ``'/'``. env: ``DASH_ROUTES_PATHNAME_PREFIX``
    :type routes_pathname_prefix: string

    :param serve_locally: If ``True`` (default), assets and dependencies
        (Dash and Component js and css) will be served from local URLs.
        If ``False`` we will use CDN links where available.
    :type serve_locally: boolean

    :param compress: Use gzip to compress files and data served by Flask.
        To use this option, you need to install dash[compress]
        Default ``False``
    :type compress: boolean

    :param meta_tags: html <meta> tags to be added to the index page.
        Each dict should have the attributes and values for one tag, eg:
        ``{'name': 'description', 'content': 'My App'}``
    :type meta_tags: list of dicts

    :param index_string: Override the standard Dash index page.
        Must contain the correct insertion markers to interpolate various
        content into it depending on the app config and components used.
        See https://dash.plotly.com/external-resources for details.
    :type index_string: string

    :param external_scripts: Additional JS files to load with the page.
        Each entry can be a string (the URL) or a dict with ``src`` (the URL)
        and optionally other ``<script>`` tag attributes such as ``integrity``
        and ``crossorigin``.
    :type external_scripts: list of strings or dicts

    :param external_stylesheets: Additional CSS files to load with the page.
        Each entry can be a string (the URL) or a dict with ``href`` (the URL)
        and optionally other ``<link>`` tag attributes such as ``rel``,
        ``integrity`` and ``crossorigin``.
    :type external_stylesheets: list of strings or dicts

    :param suppress_callback_exceptions: Default ``False``: check callbacks to
        ensure referenced IDs exist and props are valid. Set to ``True``
        if your layout is dynamic, to bypass these checks.
        env: ``DASH_SUPPRESS_CALLBACK_EXCEPTIONS``
    :type suppress_callback_exceptions: boolean

    :param prevent_initial_callbacks: Default ``False``: Sets the default value
        of ``prevent_initial_call`` for all callbacks added to the app.
        Normally all callbacks are fired when the associated outputs are first
        added to the page. You can disable this for individual callbacks by
        setting ``prevent_initial_call`` in their definitions, or set it
        ``True`` here in which case you must explicitly set it ``False`` for
        those callbacks you wish to have an initial call. This setting has no
        effect on triggering callbacks when their inputs change later on.

    :param show_undo_redo: Default ``False``, set to ``True`` to enable undo
        and redo buttons for stepping through the history of the app state.
    :type show_undo_redo: boolean

    :param extra_hot_reload_paths: A list of paths to watch for changes, in
        addition to assets and known Python and JS code, if hot reloading is
        enabled.
    :type extra_hot_reload_paths: list of strings

    :param plugins: Extend Dash functionality by passing a list of objects
        with a ``plug`` method, taking a single argument: this app, which will
        be called after the Flask server is attached.
    :type plugins: list of objects

    :param title: Default ``Dash``. Configures the document.title
    (the text that appears in a browser tab).

    :param update_title: Default ``Updating...``. Configures the document.title
    (the text that appears in a browser tab) text when a callback is being run.
    Set to None or '' if you don't want the document.title to change or if you
    want to control the document.title through a separate component or
    clientside callback.

    :param long_callback_manager: Deprecated, use ``background_callback_manager``
        instead.

    :param background_callback_manager: Background callback manager instance
        to support the ``@callback(..., background=True)`` decorator.
        One of ``DiskcacheManager`` or ``CeleryManager`` currently supported.

    :param add_log_handler: Automatically add a StreamHandler to the app logger
        if not added previously.

    :param hooks: Extend Dash renderer functionality by passing a dictionary of
    javascript functions. To hook into the layout, use dict keys "layout_pre" and
    "layout_post". To hook into the callbacks, use keys "request_pre" and "request_post"

    :param routing_callback_inputs: When using Dash pages (use_pages=True), allows to
    add new States to the routing callback, to pass additional data to the layout
    functions. The syntax for this parameter is a dict of State objects:
    `routing_callback_inputs={"language": Input("language", "value")}`
    NOTE: the keys "pathname_" and "search_" are reserved for internal use.

    :param description:  Sets a default description for meta tags on Dash pages (use_pages=True).

    :param on_error: Global callback error handler to call when
        an exception is raised. Receives the exception object as first argument.
        The callback_context can be used to access the original callback inputs,
        states and output.

    :param use_async: When True, the app will create async endpoints, as a dev,
        they will be responsible for installing the `flask[async]` dependency.
    :type use_async: boolean
    """

    _plotlyjs_url: str
    STARTUP_ROUTES: list = []

    server: flask.Flask

    def __init__(  # pylint: disable=too-many-statements
        self,
        name: Optional[str] = None,
        server: Union[bool, flask.Flask] = True,
        assets_folder: str = "assets",
        pages_folder: str = "pages",
        use_pages: Optional[bool] = None,
        assets_url_path: str = "assets",
        assets_ignore: str = "",
        assets_external_path: Optional[str] = None,
        eager_loading: bool = False,
        include_assets_files: bool = True,
        include_pages_meta: bool = True,
        url_base_pathname: Optional[str] = None,
        requests_pathname_prefix: Optional[str] = None,
        routes_pathname_prefix: Optional[str] = None,
        serve_locally: bool = True,
        compress: Optional[bool] = None,
        meta_tags: Optional[List[Dict[str, Any]]] = None,
        index_string: str = _default_index,
        external_scripts: Optional[List[Union[str, Dict[str, Any]]]] = None,
        external_stylesheets: Optional[List[Union[str, Dict[str, Any]]]] = None,
        suppress_callback_exceptions: Optional[bool] = None,
        prevent_initial_callbacks: bool = False,
        show_undo_redo: bool = False,
        extra_hot_reload_paths: Optional[List[str]] = None,
        plugins: Optional[list] = None,
        title: str = "Dash",
        update_title: str = "Updating...",
        long_callback_manager: Optional[
            Any
        ] = None,  # Type should be specified if possible
        background_callback_manager: Optional[
            Any
        ] = None,  # Type should be specified if possible
        add_log_handler: bool = True,
        hooks: Optional[RendererHooks] = None,
        routing_callback_inputs: Optional[Dict[str, Union[Input, State]]] = None,
        description: Optional[str] = None,
        on_error: Optional[Callable[[Exception], Any]] = None,
        use_async: Optional[bool] = None,
        **obsolete,
    ):

        if use_async is None:
            try:
                import asgiref  # pylint: disable=unused-import, import-outside-toplevel # noqa

                use_async = True
            except ImportError:
                pass
        elif use_async:
            try:
                import asgiref  # pylint: disable=unused-import, import-outside-toplevel # noqa
            except ImportError as exc:
                raise Exception(
                    "You are trying to use dash[async] without having installed the requirements please install via: `pip install dash[async]`"
                ) from exc

        _validate.check_obsolete(obsolete)

        caller_name = None if name else get_caller_name()

        # We have 3 cases: server is either True (we create the server), False
        # (defer server creation) or a Flask app instance (we use their server)
        if isinstance(server, flask.Flask):
            self.server = server
            if name is None:
                name = getattr(server, "name", caller_name)
        elif isinstance(server, bool):
            name = name if name else caller_name
            self.server = flask.Flask(name) if server else None  # type: ignore
        else:
            raise ValueError("server must be a Flask app or a boolean")

        base_prefix, routes_prefix, requests_prefix = pathname_configs(
            url_base_pathname, routes_pathname_prefix, requests_pathname_prefix
        )

        self.config = AttributeDict(
            name=name,
            assets_folder=os.path.join(
                flask.helpers.get_root_path(name), assets_folder
            ),  # type: ignore
            assets_url_path=assets_url_path,
            assets_ignore=assets_ignore,
            assets_external_path=get_combined_config(
                "assets_external_path", assets_external_path, ""
            ),
            pages_folder=pages_folder_config(name, pages_folder, use_pages),
            eager_loading=eager_loading,
            include_assets_files=get_combined_config(
                "include_assets_files", include_assets_files, True
            ),
            url_base_pathname=base_prefix,
            routes_pathname_prefix=routes_prefix,
            requests_pathname_prefix=requests_prefix,
            serve_locally=serve_locally,
            compress=get_combined_config("compress", compress, False),
            meta_tags=meta_tags or [],
            external_scripts=external_scripts or [],
            external_stylesheets=external_stylesheets or [],
            suppress_callback_exceptions=get_combined_config(
                "suppress_callback_exceptions", suppress_callback_exceptions, False
            ),
            prevent_initial_callbacks=prevent_initial_callbacks,
            show_undo_redo=show_undo_redo,
            extra_hot_reload_paths=extra_hot_reload_paths or [],
            title=title,
            update_title=update_title,
            include_pages_meta=include_pages_meta,
            description=description,
        )
        self.config.set_read_only(
            [
                "name",
                "assets_folder",
                "assets_url_path",
                "eager_loading",
                "serve_locally",
                "compress",
                "pages_folder",
            ],
            "Read-only: can only be set in the Dash constructor",
        )
        self.config.finalize(
            "Invalid config key. Some settings are only available "
            "via the Dash constructor"
        )

        _get_paths.CONFIG = self.config
        _pages.CONFIG = self.config

        self.pages_folder = str(pages_folder)
        self.use_pages = (pages_folder != "pages") if use_pages is None else use_pages
        self.routing_callback_inputs = routing_callback_inputs or {}

        # keep title as a class property for backwards compatibility
        self.title = title

        # list of dependencies - this one is used by the back end for dispatching
        self.callback_map = {}
        # same deps as a list to catch duplicate outputs, and to send to the front end
        self._callback_list = []

        # list of inline scripts
        self._inline_scripts = []

        # index_string has special setter so can't go in config
        self._index_string = ""
        self.index_string = index_string
        self._favicon = None

        # default renderer string
        self.renderer = f"var renderer = new DashRenderer({hooks_to_js_object(hooks)});"

        # static files from the packages
        self.css = Css(serve_locally)
        self.scripts = Scripts(serve_locally, eager_loading)

        self.registered_paths = collections.defaultdict(set)

        # urls
        self.routes = []

        self._layout = None
        self._layout_is_function = False
        self.validation_layout = None
        self._on_error = on_error
        self._extra_components = []
        self._use_async = use_async

        self._setup_dev_tools()
        self._hot_reload = AttributeDict(
            hash=None,
            hard=False,
            lock=threading.RLock(),
            watch_thread=None,
            changed_assets=[],
        )

        self._assets_files = []
        self._long_callback_count = 0
        if long_callback_manager:
            warnings.warn(
                DeprecationWarning(
                    "`long_callback_manager` is deprecated and will be remove in Dash 3.0, "
                    "use `background_callback_manager` instead."
                )
            )
        self._background_manager = background_callback_manager or long_callback_manager

        self.logger = logging.getLogger(__name__)

        if not self.logger.handlers and add_log_handler:
            self.logger.addHandler(logging.StreamHandler(stream=sys.stdout))

        if plugins is not None and isinstance(
            plugins, patch_collections_abc("Iterable")
        ):
            for plugin in plugins:
                plugin.plug(self)

        # tracks internally if a function already handled at least one request.
        self._got_first_request = {"pages": False, "setup_server": False}

        if self.server is not None:
            self.init_app()

        self.logger.setLevel(logging.INFO)

        if self.__class__.__name__ == "JupyterDash":
            warnings.warn(
                "JupyterDash is deprecated, use Dash instead.\n"
                "See https://dash.plotly.com/dash-in-jupyter for more details."
            )
        self.setup_startup_routes()

    def init_app(self, app=None, **kwargs):
        """Initialize the parts of Dash that require a flask app."""

        config = self.config

        config.update(kwargs)
        config.set_read_only(
            [
                "url_base_pathname",
                "routes_pathname_prefix",
                "requests_pathname_prefix",
            ],
            "Read-only: can only be set in the Dash constructor or during init_app()",
        )

        if app is not None:
            self.server = app

        bp_prefix = config.routes_pathname_prefix.replace("/", "_").replace(".", "_")
        assets_blueprint_name = f"{bp_prefix}dash_assets"

        self.server.register_blueprint(
            flask.Blueprint(
                assets_blueprint_name,
                config.name,
                static_folder=self.config.assets_folder,
                static_url_path=config.routes_pathname_prefix
                + self.config.assets_url_path.lstrip("/"),
            )
        )

        if config.compress:
            try:
                # pylint: disable=import-outside-toplevel
                from flask_compress import Compress

                # gzip
                Compress(self.server)

                _flask_compress_version = parse_version(
                    _get_distribution_version("flask_compress")
                )

                if not hasattr(
                    self.server.config, "COMPRESS_ALGORITHM"
                ) and _flask_compress_version >= parse_version("1.6.0"):
                    # flask-compress==1.6.0 changed default to ['br', 'gzip']
                    # and non-overridable default compression with Brotli is
                    # causing performance issues
                    self.server.config["COMPRESS_ALGORITHM"] = ["gzip"]
            except ImportError as error:
                raise ImportError(
                    "To use the compress option, you need to install dash[compress]"
                ) from error

        @self.server.errorhandler(PreventUpdate)
        def _handle_error(_):
            """Handle a halted callback and return an empty 204 response."""
            return "", 204

        self.server.before_request(self._setup_server)

        # add a handler for components suites errors to return 404
        self.server.errorhandler(InvalidResourceError)(self._invalid_resources_handler)

        self._setup_routes()

        _get_app.APP = self
        self.enable_pages()

        self._setup_plotlyjs()

    def _add_url(self, name, view_func, methods=("GET",)):
        full_name = self.config.routes_pathname_prefix + name

        self.server.add_url_rule(
            full_name, view_func=view_func, endpoint=full_name, methods=list(methods)
        )

        # record the url in Dash.routes so that it can be accessed later
        # e.g. for adding authentication with flask_login
        self.routes.append(full_name)

    def _setup_routes(self):
        self._add_url(
            "_dash-component-suites/<string:package_name>/<path:fingerprinted_path>",
            self.serve_component_suites,
        )
        self._add_url("_dash-layout", self.serve_layout)
        self._add_url("_dash-dependencies", self.dependencies)
        if self._use_async:
            self._add_url("_dash-update-component", self.async_dispatch, ["POST"])
        else:
            self._add_url("_dash-update-component", self.dispatch, ["POST"])
        self._add_url("_reload-hash", self.serve_reload_hash)
        self._add_url("_favicon.ico", self._serve_default_favicon)
        self._add_url("", self.index)

        if jupyter_dash.active:
            self._add_url(
                "_alive_" + jupyter_dash.alive_token, jupyter_dash.serve_alive
            )

        # catch-all for front-end routes, used by dcc.Location
        self._add_url("<path:path>", self.index)

    def _setup_plotlyjs(self):
        # pylint: disable=import-outside-toplevel
        from plotly.offline import get_plotlyjs_version

        url = f"https://cdn.plot.ly/plotly-{get_plotlyjs_version()}.min.js"

        # pylint: disable=protected-access
        dcc._js_dist.extend(
            [
                {
                    "relative_package_path": "package_data/plotly.min.js",
                    "external_url": url,
                    "namespace": "plotly",
                    "async": "eager",
                }
            ]
        )
        self._plotlyjs_url = url

    @property
    def layout(self):
        return self._layout

    def _layout_value(self):
        layout = self._layout() if self._layout_is_function else self._layout

        # Add any extra components
        if self._extra_components:
            layout = html.Div(children=[layout] + self._extra_components)

        return layout

    @layout.setter
    def layout(self, value):
        _validate.validate_layout_type(value)
        self._layout_is_function = callable(value)
        self._layout = value

        # for using flask.has_request_context() to deliver a full layout for
        # validation inside a layout function - track if a user might be doing this.
        if (
            self._layout_is_function
            and not self.validation_layout
            and not self.config.suppress_callback_exceptions
        ):

            layout_value = self._layout_value()
            _validate.validate_layout(value, layout_value)
            self.validation_layout = layout_value

    @property
    def index_string(self):
        return self._index_string

    @index_string.setter
    def index_string(self, value):
        checks = (_re_index_entry, _re_index_config, _re_index_scripts)
        _validate.validate_index("index string", checks, value)
        self._index_string = value

    def serve_layout(self):
        layout = self._layout_value()

        # TODO - Set browser cache limit - pass hash into frontend
        return flask.Response(
            to_json(layout),
            mimetype="application/json",
        )

    def _config(self):
        # pieces of config needed by the front end
        config = {
            "url_base_pathname": self.config.url_base_pathname,
            "requests_pathname_prefix": self.config.requests_pathname_prefix,
            "ui": self._dev_tools.ui,
            "props_check": self._dev_tools.props_check,
            "show_undo_redo": self.config.show_undo_redo,
            "suppress_callback_exceptions": self.config.suppress_callback_exceptions,
            "update_title": self.config.update_title,
            "children_props": ComponentRegistry.children_props,
            "serve_locally": self.config.serve_locally,
        }
        if not self.config.serve_locally:
            config["plotlyjs_url"] = self._plotlyjs_url
        if self._dev_tools.hot_reload:
            config["hot_reload"] = {
                # convert from seconds to msec as used by js `setInterval`
                "interval": int(self._dev_tools.hot_reload_interval * 1000),
                "max_retry": self._dev_tools.hot_reload_max_retry,
            }
        if self.validation_layout and not self.config.suppress_callback_exceptions:
            validation_layout = self.validation_layout

            # Add extra components
            if self._extra_components:
                validation_layout = html.Div(
                    children=[validation_layout] + self._extra_components
                )

            config["validation_layout"] = validation_layout

        return config

    def serve_reload_hash(self):
        _reload = self._hot_reload
        with _reload.lock:
            hard = _reload.hard
            changed = _reload.changed_assets
            _hash = _reload.hash
            _reload.hard = False
            _reload.changed_assets = []

        return flask.jsonify(
            {
                "reloadHash": _hash,
                "hard": hard,
                "packages": list(self.registered_paths.keys()),
                "files": list(changed),
            }
        )

    def get_dist(self, libraries):
        dists = []
        for dist_type in ("_js_dist", "_css_dist"):
            resources = ComponentRegistry.get_resources(dist_type, libraries)
            srcs = self._collect_and_register_resources(resources, False)
            for src in srcs:
                dists.append(dict(type=dist_type, url=src))
        return dists

    def _collect_and_register_resources(self, resources, include_async=True):
        # now needs the app context.
        # template in the necessary component suite JS bundles
        # add the version number of the package as a query parameter
        # for cache busting
        def _relative_url_path(relative_package_path="", namespace=""):
            if any(
                relative_package_path.startswith(x + "/")
                for x in ["dcc", "html", "dash_table"]
            ):
                relative_package_path = relative_package_path.replace("dash.", "")
                version = importlib.import_module(
                    f"{namespace}.{os.path.split(relative_package_path)[0]}"
                ).__version__
            else:
                version = importlib.import_module(namespace).__version__

            module_path = os.path.join(
                os.path.dirname(sys.modules[namespace].__file__), relative_package_path
            )

            modified = int(os.stat(module_path).st_mtime)

            fingerprint = build_fingerprint(relative_package_path, version, modified)
            return f"{self.config.requests_pathname_prefix}_dash-component-suites/{namespace}/{fingerprint}"

        srcs = []
        for resource in resources:
            is_dynamic_resource = resource.get("dynamic", False)
            is_async = resource.get("async") is not None
            excluded = not include_async and is_async

            if "relative_package_path" in resource:
                paths = resource["relative_package_path"]
                paths = [paths] if isinstance(paths, str) else paths

                for rel_path in paths:
                    if any(x in rel_path for x in ["dcc", "html", "dash_table"]):
                        rel_path = rel_path.replace("dash.", "")

                    self.registered_paths[resource["namespace"]].add(rel_path)

                    if not is_dynamic_resource and not excluded:
                        srcs.append(
                            _relative_url_path(
                                relative_package_path=rel_path,
                                namespace=resource["namespace"],
                            )
                        )
            elif "external_url" in resource:
                if not is_dynamic_resource and not excluded:
                    if isinstance(resource["external_url"], str):
                        srcs.append(resource["external_url"])
                    else:
                        srcs += resource["external_url"]
            elif "absolute_path" in resource:
                raise Exception("Serving files from absolute_path isn't supported yet")
            elif "asset_path" in resource:
                static_url = self.get_asset_url(resource["asset_path"])
                # Import .mjs files with type=module script tag
                if static_url.endswith(".mjs"):
                    srcs.append(
                        {
                            "src": static_url
                            + f"?m={resource['ts']}",  # Add a cache-busting query param
                            "type": "module",
                        }
                    )
                else:
                    srcs.append(
                        static_url + f"?m={resource['ts']}"
                    )  # Add a cache-busting query param

        return srcs

    def _generate_css_dist_html(self):
        external_links = self.config.external_stylesheets
        links = self._collect_and_register_resources(self.css.get_all_css())

        return "\n".join(
            [
                format_tag("link", link, opened=True)
                if isinstance(link, dict)
                else f'<link rel="stylesheet" href="{link}">'
                for link in (external_links + links)
            ]
        )

    def _generate_scripts_html(self):
        # Dash renderer has dependencies like React which need to be rendered
        # before every other script. However, the dash renderer bundle
        # itself needs to be rendered after all of the component's
        # scripts have rendered.
        # The rest of the scripts can just be loaded after React but before
        # dash renderer.
        # pylint: disable=protected-access

        mode = "dev" if self._dev_tools["props_check"] is True else "prod"

        deps = [
            {
                key: value[mode] if isinstance(value, dict) else value
                for key, value in js_dist_dependency.items()
            }
            for js_dist_dependency in _dash_renderer._js_dist_dependencies
        ]
        dev = self._dev_tools.serve_dev_bundles
        srcs = (
            self._collect_and_register_resources(
                self.scripts._resources._filter_resources(deps, dev_bundles=dev)
            )
            + self.config.external_scripts
            + self._collect_and_register_resources(
                self.scripts.get_all_scripts(dev_bundles=dev)
                + self.scripts._resources._filter_resources(
                    _dash_renderer._js_dist, dev_bundles=dev
                )
                + self.scripts._resources._filter_resources(
                    dcc._js_dist, dev_bundles=dev
                )
                + self.scripts._resources._filter_resources(
                    html._js_dist, dev_bundles=dev
                )
                + self.scripts._resources._filter_resources(
                    dash_table._js_dist, dev_bundles=dev
                )
            )
        )

        self._inline_scripts.extend(_callback.GLOBAL_INLINE_SCRIPTS)
        _callback.GLOBAL_INLINE_SCRIPTS.clear()

        return "\n".join(
            [
                format_tag("script", src)
                if isinstance(src, dict)
                else f'<script src="{src}"></script>'
                for src in srcs
            ]
            + [f"<script>{src}</script>" for src in self._inline_scripts]
        )

    def _generate_config_html(self):
        return f'<script id="_dash-config" type="application/json">{to_json(self._config())}</script>'

    def _generate_renderer(self):
        return f'<script id="_dash-renderer" type="application/javascript">{self.renderer}</script>'

    def _generate_meta(self):
        meta_tags = []
        has_ie_compat = any(
            x.get("http-equiv", "") == "X-UA-Compatible" for x in self.config.meta_tags
        )
        has_charset = any("charset" in x for x in self.config.meta_tags)
        has_viewport = any(x.get("name") == "viewport" for x in self.config.meta_tags)

        if not has_ie_compat:
            meta_tags.append({"http-equiv": "X-UA-Compatible", "content": "IE=edge"})
        if not has_charset:
            meta_tags.append({"charset": "UTF-8"})
        if not has_viewport:
            meta_tags.append(
                {"name": "viewport", "content": "width=device-width, initial-scale=1"}
            )

        return meta_tags + self.config.meta_tags

    # Serve the JS bundles for each package
    def serve_component_suites(self, package_name, fingerprinted_path):
        path_in_pkg, has_fingerprint = check_fingerprint(fingerprinted_path)

        _validate.validate_js_path(self.registered_paths, package_name, path_in_pkg)

        extension = "." + path_in_pkg.split(".")[-1]
        mimetype = mimetypes.types_map.get(extension, "application/octet-stream")

        package = sys.modules[package_name]
        self.logger.debug(
            "serving -- package: %s[%s] resource: %s => location: %s",
            package_name,
            package.__version__,
            path_in_pkg,
            package.__path__,
        )

        response = flask.Response(
            pkgutil.get_data(package_name, path_in_pkg), mimetype=mimetype
        )

        if has_fingerprint:
            # Fingerprinted resources are good forever (1 year)
            # No need for ETag as the fingerprint changes with each build
            response.cache_control.max_age = 31536000  # 1 year
        else:
            # Non-fingerprinted resources are given an ETag that
            # will be used / check on future requests
            response.add_etag()
            tag = response.get_etag()[0]

            request_etag = flask.request.headers.get("If-None-Match")

            if f'"{tag}"' == request_etag:
                response = flask.Response(None, status=304)

        return response

    def index(self, *args, **kwargs):  # pylint: disable=unused-argument
        scripts = self._generate_scripts_html()
        css = self._generate_css_dist_html()
        config = self._generate_config_html()
        metas = self._generate_meta()
        renderer = self._generate_renderer()

        # use self.title instead of app.config.title for backwards compatibility
        title = self.title

        if self.use_pages and self.config.include_pages_meta:
            metas = _page_meta_tags(self) + metas

        if self._favicon:
            favicon_mod_time = os.path.getmtime(
                os.path.join(self.config.assets_folder, self._favicon)
            )
            favicon_url = f"{self.get_asset_url(self._favicon)}?m={favicon_mod_time}"
        else:
            prefix = self.config.requests_pathname_prefix
            favicon_url = f"{prefix}_favicon.ico?v={__version__}"

        favicon = format_tag(
            "link",
            {"rel": "icon", "type": "image/x-icon", "href": favicon_url},
            opened=True,
        )

        tags = "\n      ".join(
            format_tag("meta", x, opened=True, sanitize=True) for x in metas
        )

        index = self.interpolate_index(
            metas=tags,
            title=title,
            css=css,
            config=config,
            scripts=scripts,
            app_entry=_app_entry,
            favicon=favicon,
            renderer=renderer,
        )

        checks = (
            _re_index_entry_id,
            _re_index_config_id,
            _re_index_scripts_id,
            _re_renderer_scripts_id,
        )
        _validate.validate_index("index", checks, index)
        return index

    def interpolate_index(
        self,
        metas="",
        title="",
        css="",
        config="",
        scripts="",
        app_entry="",
        favicon="",
        renderer="",
    ):
        """Called to create the initial HTML string that is loaded on page.
        Override this method to provide you own custom HTML.

        :Example:

            class MyDash(dash.Dash):
                def interpolate_index(self, **kwargs):
                    return '''<!DOCTYPE html>
                    <html>
                        <head>
                            <title>My App</title>
                        </head>
                        <body>
                            <div id="custom-header">My custom header</div>
                            {app_entry}
                            {config}
                            {scripts}
                            {renderer}
                            <div id="custom-footer">My custom footer</div>
                        </body>
                    </html>'''.format(app_entry=kwargs.get('app_entry'),
                                      config=kwargs.get('config'),
                                      scripts=kwargs.get('scripts'),
                                      renderer=kwargs.get('renderer'))

        :param metas: Collected & formatted meta tags.
        :param title: The title of the app.
        :param css: Collected & formatted css dependencies as <link> tags.
        :param config: Configs needed by dash-renderer.
        :param scripts: Collected & formatted scripts tags.
        :param renderer: A script tag that instantiates the DashRenderer.
        :param app_entry: Where the app will render.
        :param favicon: A favicon <link> tag if found in assets folder.
        :return: The interpolated HTML string for the index.
        """
        return interpolate_str(
            self.index_string,
            metas=metas,
            title=title,
            css=css,
            config=config,
            scripts=scripts,
            favicon=favicon,
            renderer=renderer,
            app_entry=app_entry,
        )

    def dependencies(self):
        return flask.Response(
            to_json(self._callback_list),
            content_type="application/json",
        )

    def clientside_callback(self, clientside_function, *args, **kwargs):
        """Create a callback that updates the output by calling a clientside
        (JavaScript) function instead of a Python function.

        Unlike `@app.callback`, `clientside_callback` is not a decorator:
        it takes either a
        `dash.dependencies.ClientsideFunction(namespace, function_name)`
        argument that describes which JavaScript function to call
        (Dash will look for the JavaScript function at
        `window.dash_clientside[namespace][function_name]`), or it may take
        a string argument that contains the clientside function source.

        For example, when using a `dash.dependencies.ClientsideFunction`:
        ```
        app.clientside_callback(
            ClientsideFunction('my_clientside_library', 'my_function'),
            Output('my-div' 'children'),
            [Input('my-input', 'value'),
             Input('another-input', 'value')]
        )
        ```

        With this signature, Dash's front-end will call
        `window.dash_clientside.my_clientside_library.my_function` with the
        current values of the `value` properties of the components `my-input`
        and `another-input` whenever those values change.

        Include a JavaScript file by including it your `assets/` folder. The
        file can be named anything but you'll need to assign the function's
        namespace to the `window.dash_clientside` namespace. For example,
        this file might look:
        ```
        window.dash_clientside = window.dash_clientside || {};
        window.dash_clientside.my_clientside_library = {
            my_function: function(input_value_1, input_value_2) {
                return (
                    parseFloat(input_value_1, 10) +
                    parseFloat(input_value_2, 10)
                );
            }
        }
        ```

        Alternatively, you can pass the JavaScript source directly to
        `clientside_callback`. In this case, the same example would look like:
        ```
        app.clientside_callback(
            '''
            function(input_value_1, input_value_2) {
                return (
                    parseFloat(input_value_1, 10) +
                    parseFloat(input_value_2, 10)
                );
            }
            ''',
            Output('my-div' 'children'),
            [Input('my-input', 'value'),
             Input('another-input', 'value')]
        )
        ```

        The last, optional argument `prevent_initial_call` causes the callback
        not to fire when its outputs are first added to the page. Defaults to
        `False` unless `prevent_initial_callbacks=True` at the app level.
        """
        return _callback.register_clientside_callback(
            self._callback_list,
            self.callback_map,
            self.config.prevent_initial_callbacks,
            self._inline_scripts,
            clientside_function,
            *args,
            **kwargs,
        )

    def callback(self, *_args, **_kwargs):
        """
        Normally used as a decorator, `@app.callback` provides a server-side
        callback relating the values of one or more `Output` items to one or
        more `Input` items which will trigger the callback when they change,
        and optionally `State` items which provide additional information but
        do not trigger the callback directly.

        The last, optional argument `prevent_initial_call` causes the callback
        not to fire when its outputs are first added to the page. Defaults to
        `False` unless `prevent_initial_callbacks=True` at the app level.


        """
        return _callback.callback(
            *_args,
            config_prevent_initial_callbacks=self.config.prevent_initial_callbacks,
            callback_list=self._callback_list,
            callback_map=self.callback_map,
            **_kwargs,
        )

    def long_callback(
        self,
        *_args,
        manager=None,
        interval=1000,
        running=None,
        cancel=None,
        progress=None,
        progress_default=None,
        cache_args_to_ignore=None,
        **_kwargs,
    ):
        """
        Deprecated: long callbacks are now supported natively with regular callbacks,
        use `background=True` with `dash.callback` or `app.callback` instead.
        """
        return _callback.callback(
            *_args,
            background=True,
            manager=manager,
            interval=interval,
            progress=progress,
            progress_default=progress_default,
            running=running,
            cancel=cancel,
            cache_args_to_ignore=cache_args_to_ignore,
            callback_map=self.callback_map,
            callback_list=self._callback_list,
            config_prevent_initial_callbacks=self.config.prevent_initial_callbacks,
            **_kwargs,
        )

    # pylint: disable=R0915
    def _initialize_context(self, body):
        """Initialize the global context for the request."""
        g = AttributeDict({})
        g.inputs_list = body.get("inputs", [])
        g.states_list = body.get("state", [])
        g.outputs_list = body.get("outputs", [])
        g.input_values = inputs_to_dict(g.inputs_list)
        g.state_values = inputs_to_dict(g.states_list)
        g.triggered_inputs = [
            {"prop_id": x, "value": g.input_values.get(x)}
            for x in body.get("changedPropIds", [])
        ]
        g.dash_response = flask.Response(mimetype="application/json")
        g.cookies = dict(**flask.request.cookies)
        g.headers = dict(**flask.request.headers)
        g.path = flask.request.full_path
        g.remote = flask.request.remote_addr
        g.origin = flask.request.origin
        g.updated_props = {}
        return g

    def _prepare_callback(self, g, body):
        """Prepare callback-related data."""
        output = body["output"]
        try:
            cb = self.callback_map[output]
            func = cb["callback"]
            g.background_callback_manager = (
                cb.get("manager") or self._background_manager
            )
            g.ignore_register_page = cb.get("long", False)

            # Add args_grouping
            inputs_state_indices = cb["inputs_state_indices"]
            inputs_state = convert_to_AttributeDict(g.inputs_list + g.states_list)

            if cb.get("no_output"):
                g.outputs_list = []
            elif not g.outputs_list:
                # Legacy support for older renderers
                split_callback_id(output)

            # Update args_grouping attributes
            for s in inputs_state:
                # check for pattern matching: list of inputs or state
                if isinstance(s, list):
                    for pattern_match_g in s:
                        update_args_group(
                            pattern_match_g, body.get("changedPropIds", [])
                        )
                update_args_group(s, body.get("changedPropIds", []))

            g.args_grouping, g.using_args_grouping = self._prepare_grouping(
                inputs_state, inputs_state_indices
            )
            g.outputs_grouping, g.using_outputs_grouping = self._prepare_grouping(
                g.outputs_list, cb.get("outputs_indices", [])
            )
        except KeyError as e:
            raise KeyError(f"Callback function not found for output '{output}'.") from e
        return func

    def _prepare_grouping(self, data_list, indices):
        """Prepare grouping logic for inputs or outputs."""
        if not isinstance(data_list, list):
            flat_data = [data_list]
        else:
            flat_data = data_list

        if len(flat_data) > 0:
            grouping = map_grouping(lambda ind: flat_data[ind], indices)
            using_grouping = not isinstance(indices, int) and indices != list(
                range(grouping_len(indices))
            )
        else:
            grouping, using_grouping = [], False

        return grouping, using_grouping

    def _execute_callback(self, func, args, outputs_list, g):
        """Execute the callback with the prepared arguments."""
        # noinspection PyArgumentList
        partial_func = functools.partial(
            func,
            *args,
            outputs_list=outputs_list,
            long_callback_manager=g.background_callback_manager,
            callback_context=g,
            app=self,
            app_on_error=self._on_error,
            app_use_async=self._use_async,
        )
        return partial_func

    async def async_dispatch(self):
        body = flask.request.get_json()
        g = self._initialize_context(body)
        func = self._prepare_callback(g, body)
        args = inputs_to_vals(g.inputs_list + g.states_list)

        ctx = copy_context()
        partial_func = self._execute_callback(func, args, g.outputs_list, g)
        if asyncio.iscoroutine(func):
            response_data = await ctx.run(partial_func)
        else:
            response_data = ctx.run(partial_func)

        if asyncio.iscoroutine(response_data):
            response_data = await response_data

        g.dash_response.set_data(response_data)
        return g.dash_response

    def dispatch(self):
        body = flask.request.get_json()
        g = self._initialize_context(body)
        func = self._prepare_callback(g, body)
        args = inputs_to_vals(g.inputs_list + g.states_list)

        ctx = copy_context()
        partial_func = self._execute_callback(func, args, g.outputs_list, g)
        response_data = ctx.run(partial_func)

        if asyncio.iscoroutine(response_data):
            raise Exception(
                "You are trying to use a coroutine without dash[async]. "
                "Please install the dependencies via `pip install dash[async]` and ensure "
                "that `use_async=False` is not being passed to the app."
            )

        g.dash_response.set_data(response_data)
        return g.dash_response

    def _setup_server(self):
        if self._got_first_request["setup_server"]:
            return
        self._got_first_request["setup_server"] = True

        # Apply _force_eager_loading overrides from modules
        eager_loading = self.config.eager_loading
        for module_name in ComponentRegistry.registry:
            module = sys.modules[module_name]
            eager = getattr(module, "_force_eager_loading", False)
            eager_loading = eager_loading or eager

        # Update eager_loading settings
        self.scripts.config.eager_loading = eager_loading

        if self.config.include_assets_files:
            self._walk_assets_directory()

        if not self.layout and self.use_pages:
            self.layout = page_container

        _validate.validate_layout(self.layout, self._layout_value())

        self._generate_scripts_html()
        self._generate_css_dist_html()

        # Copy over global callback data structures assigned with `dash.callback`
        for k in list(_callback.GLOBAL_CALLBACK_MAP):
            if k in self.callback_map:
                raise DuplicateCallback(
                    f"The callback `{k}` provided with `dash.callback` was already "
                    "assigned with `app.callback`."
                )

            self.callback_map[k] = _callback.GLOBAL_CALLBACK_MAP.pop(k)

        self._callback_list.extend(_callback.GLOBAL_CALLBACK_LIST)
        _callback.GLOBAL_CALLBACK_LIST.clear()

        _validate.validate_long_callbacks(self.callback_map)

        cancels = {}

        for callback in self.callback_map.values():
            long = callback.get("long")
            if not long:
                continue
            if "cancel_inputs" in long:
                cancel = long.pop("cancel_inputs")
                for c in cancel:
                    cancels[c] = long.get("manager")

        if cancels:
            for cancel_input, manager in cancels.items():
                # pylint: disable=cell-var-from-loop
                @self.callback(
                    Output(cancel_input.component_id, "id"),
                    cancel_input,
                    prevent_initial_call=True,
                    manager=manager,
                )
                def cancel_call(*_):
                    job_ids = flask.request.args.getlist("cancelJob")
                    executor = _callback.context_value.get().background_callback_manager
                    if job_ids:
                        for job_id in job_ids:
                            executor.terminate_job(job_id)
                    return no_update

    def _add_assets_resource(self, url_path, file_path):
        res = {"asset_path": url_path, "filepath": file_path}
        if self.config.assets_external_path:
            res["external_url"] = self.get_asset_url(url_path.lstrip("/"))
        self._assets_files.append(file_path)
        return res

    def _walk_assets_directory(self):
        walk_dir = self.config.assets_folder
        slash_splitter = re.compile(r"[\\/]+")
        ignore_str = self.config.assets_ignore
        ignore_filter = re.compile(ignore_str) if ignore_str else None

        for current, _, files in sorted(os.walk(walk_dir)):
            if current == walk_dir:
                base = ""
            else:
                s = current.replace(walk_dir, "").lstrip("\\").lstrip("/")
                splitted = slash_splitter.split(s)
                if len(splitted) > 1:
                    base = "/".join(slash_splitter.split(s))
                else:
                    base = splitted[0]

            if ignore_filter:
                files_gen = (x for x in files if not ignore_filter.search(x))
            else:
                files_gen = files

            for f in sorted(files_gen):
                path = "/".join([base, f]) if base else f

                full = os.path.join(current, f)

                if f.endswith("js"):
                    self.scripts.append_script(self._add_assets_resource(path, full))
                elif f.endswith("css"):
                    self.css.append_css(self._add_assets_resource(path, full))
                elif f == "favicon.ico":
                    self._favicon = path

    @staticmethod
    def _invalid_resources_handler(err):
        return err.args[0], 404

    @staticmethod
    def _serve_default_favicon():
        return flask.Response(
            pkgutil.get_data("dash", "favicon.ico"), content_type="image/x-icon"
        )

    def csp_hashes(self, hash_algorithm="sha256"):
        """Calculates CSP hashes (sha + base64) of all inline scripts, such that
        one of the biggest benefits of CSP (disallowing general inline scripts)
        can be utilized together with Dash clientside callbacks (inline scripts).

        Calculate these hashes after all inline callbacks are defined,
        and add them to your CSP headers before starting the server, for example
        with the flask-talisman package from PyPI:

        flask_talisman.Talisman(app.server, content_security_policy={
            "default-src": "'self'",
            "script-src": ["'self'"] + app.csp_hashes()
        })

        :param hash_algorithm: One of the recognized CSP hash algorithms ('sha256', 'sha384', 'sha512').
        :return: List of CSP hash strings of all inline scripts.
        """

        HASH_ALGORITHMS = ["sha256", "sha384", "sha512"]
        if hash_algorithm not in HASH_ALGORITHMS:
            raise ValueError(
                "Possible CSP hash algorithms: " + ", ".join(HASH_ALGORITHMS)
            )

        method = getattr(hashlib, hash_algorithm)

        def _hash(script):
            return base64.b64encode(method(script.encode("utf-8")).digest()).decode(
                "utf-8"
            )

        self._inline_scripts.extend(_callback.GLOBAL_INLINE_SCRIPTS)
        _callback.GLOBAL_INLINE_SCRIPTS.clear()

        return [
            f"'{hash_algorithm}-{_hash(script)}'"
            for script in (self._inline_scripts + [self.renderer])
        ]

    def get_asset_url(self, path):
        """
        Return the URL for the provided `path` in the assets directory.

        If `assets_external_path` is set, `get_asset_url` returns
        `assets_external_path` + `assets_url_path` + `path`, where
        `path` is the path passed to `get_asset_url`.

        Otherwise, `get_asset_url` returns
        `requests_pathname_prefix` + `assets_url_path` + `path`, where
        `path` is the path passed to `get_asset_url`.

        Use `get_asset_url` in an app to access assets at the correct location
        in different environments. In a deployed app on Dash Enterprise,
        `requests_pathname_prefix` is the app name. For an app called "my-app",
        `app.get_asset_url("image.png")` would return:

        ```
        /my-app/assets/image.png
        ```

        While the same app running locally, without
        `requests_pathname_prefix` set, would return:

        ```
        /assets/image.png
        ```
        """
        return _get_paths.app_get_asset_url(self.config, path)

    def get_relative_path(self, path):
        """
        Return a path with `requests_pathname_prefix` prefixed before it.
        Use this function when specifying local URL paths that will work
        in environments regardless of what `requests_pathname_prefix` is.
        In some deployment environments, like Dash Enterprise,
        `requests_pathname_prefix` is set to the application name,
        e.g. `my-dash-app`.
        When working locally, `requests_pathname_prefix` might be unset and
        so a relative URL like `/page-2` can just be `/page-2`.
        However, when the app is deployed to a URL like `/my-dash-app`, then
        `app.get_relative_path('/page-2')` will return `/my-dash-app/page-2`.
        This can be used as an alternative to `get_asset_url` as well with
        `app.get_relative_path('/assets/logo.png')`

        Use this function with `app.strip_relative_path` in callbacks that
        deal with `dcc.Location` `pathname` routing.
        That is, your usage may look like:
        ```
        app.layout = html.Div([
            dcc.Location(id='url'),
            html.Div(id='content')
        ])
        @app.callback(Output('content', 'children'), [Input('url', 'pathname')])
        def display_content(path):
            page_name = app.strip_relative_path(path)
            if not page_name:  # None or ''
                return html.Div([
                    dcc.Link(href=app.get_relative_path('/page-1')),
                    dcc.Link(href=app.get_relative_path('/page-2')),
                ])
            elif page_name == 'page-1':
                return chapters.page_1
            if page_name == "page-2":
                return chapters.page_2
        ```
        """
        return _get_paths.app_get_relative_path(
            self.config.requests_pathname_prefix, path
        )

    def strip_relative_path(self, path):
        """
        Return a path with `requests_pathname_prefix` and leading and trailing
        slashes stripped from it. Also, if None is passed in, None is returned.
        Use this function with `get_relative_path` in callbacks that deal
        with `dcc.Location` `pathname` routing.
        That is, your usage may look like:
        ```
        app.layout = html.Div([
            dcc.Location(id='url'),
            html.Div(id='content')
        ])
        @app.callback(Output('content', 'children'), [Input('url', 'pathname')])
        def display_content(path):
            page_name = app.strip_relative_path(path)
            if not page_name:  # None or ''
                return html.Div([
                    dcc.Link(href=app.get_relative_path('/page-1')),
                    dcc.Link(href=app.get_relative_path('/page-2')),
                ])
            elif page_name == 'page-1':
                return chapters.page_1
            if page_name == "page-2":
                return chapters.page_2
        ```
        Note that `chapters.page_1` will be served if the user visits `/page-1`
        _or_ `/page-1/` since `strip_relative_path` removes the trailing slash.

        Also note that `strip_relative_path` is compatible with
        `get_relative_path` in environments where `requests_pathname_prefix` set.
        In some deployment environments, like Dash Enterprise,
        `requests_pathname_prefix` is set to the application name, e.g. `my-dash-app`.
        When working locally, `requests_pathname_prefix` might be unset and
        so a relative URL like `/page-2` can just be `/page-2`.
        However, when the app is deployed to a URL like `/my-dash-app`, then
        `app.get_relative_path('/page-2')` will return `/my-dash-app/page-2`

        The `pathname` property of `dcc.Location` will return '`/my-dash-app/page-2`'
        to the callback.
        In this case, `app.strip_relative_path('/my-dash-app/page-2')`
        will return `'page-2'`

        For nested URLs, slashes are still included:
        `app.strip_relative_path('/page-1/sub-page-1/')` will return
        `page-1/sub-page-1`
        ```
        """
        return _get_paths.app_strip_relative_path(
            self.config.requests_pathname_prefix, path
        )

    @staticmethod
    def add_startup_route(name, view_func, methods):
        """
        Add a route to the app to be initialized at the end of Dash initialization.
        Use this if the package requires a route to be added to the app, and you will not need to worry about at what point to add it.

        :param name: The name of the route. eg "my-new-url/path".
        :param view_func: The function to call when the route is requested. The function should return a JSON serializable object.
        :param methods: The HTTP methods that the route should respond to. eg ["GET", "POST"] or either one.
        """
        if not isinstance(name, str) or name.startswith("/"):
            raise ValueError("name must be a string and should not start with '/'")

        if not callable(view_func):
            raise ValueError("view_func must be callable")

        valid_methods = {"POST", "GET"}
        if not set(methods).issubset(valid_methods):
            raise ValueError(f"methods should only contain {valid_methods}")

        if any(route[0] == name for route in Dash.STARTUP_ROUTES):
            raise ValueError(f"Route name '{name}' is already in use.")

        Dash.STARTUP_ROUTES.append((name, view_func, methods))

    def setup_startup_routes(self):
        """
        Initialize the startup routes stored in STARTUP_ROUTES.
        """
        for _name, _view_func, _methods in self.STARTUP_ROUTES:
            self._add_url(f"_dash_startup_route/{_name}", _view_func, _methods)
        self.STARTUP_ROUTES = []

    def _setup_dev_tools(self, **kwargs):
        debug = kwargs.get("debug", False)
        dev_tools = self._dev_tools = AttributeDict()

        for attr in (
            "ui",
            "props_check",
            "serve_dev_bundles",
            "hot_reload",
            "silence_routes_logging",
            "prune_errors",
        ):
            dev_tools[attr] = get_combined_config(
                attr, kwargs.get(attr, None), default=debug
            )

        for attr, _type, default in (
            ("hot_reload_interval", float, 3),
            ("hot_reload_watch_interval", float, 0.5),
            ("hot_reload_max_retry", int, 8),
        ):
            dev_tools[attr] = _type(
                get_combined_config(attr, kwargs.get(attr, None), default=default)
            )

        return dev_tools

    def enable_dev_tools(
        self,
        debug=None,
        dev_tools_ui=None,
        dev_tools_props_check=None,
        dev_tools_serve_dev_bundles=None,
        dev_tools_hot_reload=None,
        dev_tools_hot_reload_interval=None,
        dev_tools_hot_reload_watch_interval=None,
        dev_tools_hot_reload_max_retry=None,
        dev_tools_silence_routes_logging=None,
        dev_tools_prune_errors=None,
    ):
        """Activate the dev tools, called by `run`. If your application
        is served by wsgi and you want to activate the dev tools, you can call
        this method out of `__main__`.

        All parameters can be set by environment variables as listed.
        Values provided here take precedence over environment variables.

        Available dev_tools environment variables:

            - DASH_DEBUG
            - DASH_UI
            - DASH_PROPS_CHECK
            - DASH_SERVE_DEV_BUNDLES
            - DASH_HOT_RELOAD
            - DASH_HOT_RELOAD_INTERVAL
            - DASH_HOT_RELOAD_WATCH_INTERVAL
            - DASH_HOT_RELOAD_MAX_RETRY
            - DASH_SILENCE_ROUTES_LOGGING
            - DASH_PRUNE_ERRORS

        :param debug: Enable/disable all the dev tools unless overridden by the
            arguments or environment variables. Default is ``True`` when
            ``enable_dev_tools`` is called directly, and ``False`` when called
            via ``run``. env: ``DASH_DEBUG``
        :type debug: bool

        :param dev_tools_ui: Show the dev tools UI. env: ``DASH_UI``
        :type dev_tools_ui: bool

        :param dev_tools_props_check: Validate the types and values of Dash
            component props. env: ``DASH_PROPS_CHECK``
        :type dev_tools_props_check: bool

        :param dev_tools_serve_dev_bundles: Serve the dev bundles. Production
            bundles do not necessarily include all the dev tools code.
            env: ``DASH_SERVE_DEV_BUNDLES``
        :type dev_tools_serve_dev_bundles: bool

        :param dev_tools_hot_reload: Activate hot reloading when app, assets,
            and component files change. env: ``DASH_HOT_RELOAD``
        :type dev_tools_hot_reload: bool

        :param dev_tools_hot_reload_interval: Interval in seconds for the
            client to request the reload hash. Default 3.
            env: ``DASH_HOT_RELOAD_INTERVAL``
        :type dev_tools_hot_reload_interval: float

        :param dev_tools_hot_reload_watch_interval: Interval in seconds for the
            server to check asset and component folders for changes.
            Default 0.5. env: ``DASH_HOT_RELOAD_WATCH_INTERVAL``
        :type dev_tools_hot_reload_watch_interval: float

        :param dev_tools_hot_reload_max_retry: Maximum number of failed reload
            hash requests before failing and displaying a pop up. Default 8.
            env: ``DASH_HOT_RELOAD_MAX_RETRY``
        :type dev_tools_hot_reload_max_retry: int

        :param dev_tools_silence_routes_logging: Silence the `werkzeug` logger,
            will remove all routes logging. Enabled with debugging by default
            because hot reload hash checks generate a lot of requests.
            env: ``DASH_SILENCE_ROUTES_LOGGING``
        :type dev_tools_silence_routes_logging: bool

        :param dev_tools_prune_errors: Reduce tracebacks to just user code,
            stripping out Flask and Dash pieces. Only available with debugging.
            `True` by default, set to `False` to see the complete traceback.
            env: ``DASH_PRUNE_ERRORS``
        :type dev_tools_prune_errors: bool

        :return: debug
        """
        if debug is None:
            debug = get_combined_config("debug", None, True)

        dev_tools = self._setup_dev_tools(
            debug=debug,
            ui=dev_tools_ui,
            props_check=dev_tools_props_check,
            serve_dev_bundles=dev_tools_serve_dev_bundles,
            hot_reload=dev_tools_hot_reload,
            hot_reload_interval=dev_tools_hot_reload_interval,
            hot_reload_watch_interval=dev_tools_hot_reload_watch_interval,
            hot_reload_max_retry=dev_tools_hot_reload_max_retry,
            silence_routes_logging=dev_tools_silence_routes_logging,
            prune_errors=dev_tools_prune_errors,
        )

        if dev_tools.silence_routes_logging:
            logging.getLogger("werkzeug").setLevel(logging.ERROR)

        if dev_tools.hot_reload:
            _reload = self._hot_reload
            _reload.hash = generate_hash()

            # find_loader should return None on __main__ but doesn't
            # on some Python versions https://bugs.python.org/issue14710
            packages = [
                pkgutil.find_loader(x)
                for x in list(ComponentRegistry.registry)
                if x != "__main__"
            ]

            # # additional condition to account for AssertionRewritingHook object
            # # loader when running pytest

            if "_pytest" in sys.modules:
                from _pytest.assertion.rewrite import (  # pylint: disable=import-outside-toplevel
                    AssertionRewritingHook,
                )

                for index, package in enumerate(packages):
                    if isinstance(package, AssertionRewritingHook):
                        dash_spec = importlib.util.find_spec("dash")
                        dash_test_path = dash_spec.submodule_search_locations[0]
                        setattr(dash_spec, "path", dash_test_path)
                        packages[index] = dash_spec

            component_packages_dist = [
                dash_test_path
                if isinstance(package, ModuleSpec)
                else os.path.dirname(package.path)
                if hasattr(package, "path")
                else os.path.dirname(
                    package._path[0]  # pylint: disable=protected-access
                )
                if hasattr(package, "_path")
                else package.filename
                for package in packages
            ]

            for i, package in enumerate(packages):
                if hasattr(package, "path") and "dash/dash" in os.path.dirname(
                    package.path
                ):
                    component_packages_dist[i : i + 1] = [
                        os.path.join(os.path.dirname(package.path), x)
                        for x in ["dcc", "html", "dash_table"]
                    ]

            _reload.watch_thread = threading.Thread(
                target=lambda: _watch.watch(
                    [self.config.assets_folder] + component_packages_dist,
                    self._on_assets_change,
                    sleep_time=dev_tools.hot_reload_watch_interval,
                )
            )
            _reload.watch_thread.daemon = True
            _reload.watch_thread.start()

        if debug:
            if jupyter_dash.active:
                jupyter_dash.configure_callback_exception_handling(
                    self, dev_tools.prune_errors
                )
            elif dev_tools.prune_errors:
                secret = gen_salt(20)

                @self.server.errorhandler(Exception)
                def _wrap_errors(error):
                    # find the callback invocation, if the error is from a callback
                    # and skip the traceback up to that point
                    # if the error didn't come from inside a callback, we won't
                    # skip anything.
                    tb = _get_traceback(secret, error)
                    return tb, 500

        if debug and dev_tools.ui:

            def _before_request():
                flask.g.timing_information = {  # pylint: disable=assigning-non-slot
                    "__dash_server": {"dur": time.time(), "desc": None}
                }

            def _after_request(response):
                timing_information = flask.g.get("timing_information", None)
                if timing_information is None:
                    return response

                dash_total = timing_information.get("__dash_server", None)
                if dash_total is not None:
                    dash_total["dur"] = round((time.time() - dash_total["dur"]) * 1000)

                for name, info in timing_information.items():
                    value = name
                    if info.get("desc") is not None:
                        value += f';desc="{info["desc"]}"'

                    if info.get("dur") is not None:
                        value += f";dur={info['dur']}"

                    response.headers.add("Server-Timing", value)

                return response

            self.server.before_request(_before_request)

            self.server.after_request(_after_request)

        if (
            debug
            and dev_tools.serve_dev_bundles
            and not self.scripts.config.serve_locally
        ):
            # Dev bundles only works locally.
            self.scripts.config.serve_locally = True
            print(
                "WARNING: dev bundles requested with serve_locally=False.\n"
                "This is not supported, switching to serve_locally=True"
            )

        return debug

    # noinspection PyProtectedMember
    def _on_assets_change(self, filename, modified, deleted):
        _reload = self._hot_reload
        with _reload.lock:
            _reload.hard = True
            _reload.hash = generate_hash()

            if self.config.assets_folder in filename:
                asset_path = (
                    os.path.relpath(
                        filename,
                        os.path.commonprefix([self.config.assets_folder, filename]),
                    )
                    .replace("\\", "/")
                    .lstrip("/")
                )

                _reload.changed_assets.append(
                    {
                        "url": self.get_asset_url(asset_path),
                        "modified": int(modified),
                        "is_css": filename.endswith("css"),
                    }
                )

                if filename not in self._assets_files and not deleted:
                    res = self._add_assets_resource(asset_path, filename)
                    if filename.endswith("js"):
                        self.scripts.append_script(res)
                    elif filename.endswith("css"):
                        self.css.append_css(res)

                if deleted:
                    if filename in self._assets_files:
                        self._assets_files.remove(filename)

                    def delete_resource(resources):
                        to_delete = None
                        for r in resources:
                            if r.get("asset_path") == asset_path:
                                to_delete = r
                                break
                        if to_delete:
                            resources.remove(to_delete)

                    if filename.endswith("js"):
                        # pylint: disable=protected-access
                        delete_resource(self.scripts._resources._resources)
                    elif filename.endswith("css"):
                        # pylint: disable=protected-access
                        delete_resource(self.css._resources._resources)

    # pylint: disable=too-many-branches
    def run(
        self,
        host: Optional[str] = None,
        port: Optional[Union[str, int]] = None,
        proxy: Optional[str] = None,
        debug: Optional[bool] = None,
        jupyter_mode: Optional[JupyterDisplayMode] = None,
        jupyter_width: str = "100%",
        jupyter_height: int = 650,
        jupyter_server_url: Optional[str] = None,
        dev_tools_ui: Optional[bool] = None,
        dev_tools_props_check: Optional[bool] = None,
        dev_tools_serve_dev_bundles: Optional[bool] = None,
        dev_tools_hot_reload: Optional[bool] = None,
        dev_tools_hot_reload_interval: Optional[int] = None,
        dev_tools_hot_reload_watch_interval: Optional[int] = None,
        dev_tools_hot_reload_max_retry: Optional[int] = None,
        dev_tools_silence_routes_logging: Optional[bool] = None,
        dev_tools_prune_errors: Optional[bool] = None,
        **flask_run_options,
    ):
        """Start the flask server in local mode, you should not run this on a
        production server, use gunicorn/waitress instead.

        If a parameter can be set by an environment variable, that is listed
        too. Values provided here take precedence over environment variables.

        :param host: Host IP used to serve the application, default to "127.0.0.1"
            env: ``HOST``
        :type host: string

        :param port: Port used to serve the application, default to "8050"
            env: ``PORT``
        :type port: int

        :param proxy: If this application will be served to a different URL
            via a proxy configured outside of Python, you can list it here
            as a string of the form ``"{input}::{output}"``, for example:
            ``"http://0.0.0.0:8050::https://my.domain.com"``
            so that the startup message will display an accurate URL.
            env: ``DASH_PROXY``
        :type proxy: string

        :param debug: Set Flask debug mode and enable dev tools.
            env: ``DASH_DEBUG``
        :type debug: bool

        :param debug: Enable/disable all the dev tools unless overridden by the
            arguments or environment variables. Default is ``True`` when
            ``enable_dev_tools`` is called directly, and ``False`` when called
            via ``run``. env: ``DASH_DEBUG``
        :type debug: bool

        :param dev_tools_ui: Show the dev tools UI. env: ``DASH_UI``
        :type dev_tools_ui: bool

        :param dev_tools_props_check: Validate the types and values of Dash
            component props. env: ``DASH_PROPS_CHECK``
        :type dev_tools_props_check: bool

        :param dev_tools_serve_dev_bundles: Serve the dev bundles. Production
            bundles do not necessarily include all the dev tools code.
            env: ``DASH_SERVE_DEV_BUNDLES``
        :type dev_tools_serve_dev_bundles: bool

        :param dev_tools_hot_reload: Activate hot reloading when app, assets,
            and component files change. env: ``DASH_HOT_RELOAD``
        :type dev_tools_hot_reload: bool

        :param dev_tools_hot_reload_interval: Interval in seconds for the
            client to request the reload hash. Default 3.
            env: ``DASH_HOT_RELOAD_INTERVAL``
        :type dev_tools_hot_reload_interval: float

        :param dev_tools_hot_reload_watch_interval: Interval in seconds for the
            server to check asset and component folders for changes.
            Default 0.5. env: ``DASH_HOT_RELOAD_WATCH_INTERVAL``
        :type dev_tools_hot_reload_watch_interval: float

        :param dev_tools_hot_reload_max_retry: Maximum number of failed reload
            hash requests before failing and displaying a pop up. Default 8.
            env: ``DASH_HOT_RELOAD_MAX_RETRY``
        :type dev_tools_hot_reload_max_retry: int

        :param dev_tools_silence_routes_logging: Silence the `werkzeug` logger,
            will remove all routes logging. Enabled with debugging by default
            because hot reload hash checks generate a lot of requests.
            env: ``DASH_SILENCE_ROUTES_LOGGING``
        :type dev_tools_silence_routes_logging: bool

        :param dev_tools_prune_errors: Reduce tracebacks to just user code,
            stripping out Flask and Dash pieces. Only available with debugging.
            `True` by default, set to `False` to see the complete traceback.
            env: ``DASH_PRUNE_ERRORS``
        :type dev_tools_prune_errors: bool

        :param jupyter_mode: How to display the application when running
            inside a jupyter notebook.

        :param jupyter_width: Determine the width of the output cell
            when displaying inline in jupyter notebooks.
        :type jupyter_width: str

        :param jupyter_height: Height of app when displayed using
            jupyter_mode="inline"
        :type jupyter_height: int

        :param jupyter_server_url: Custom server url to display
            the app in jupyter notebook.

        :param flask_run_options: Given to `Flask.run`

        :return:
        """
        if debug is None:
            debug = get_combined_config("debug", None, False)

        debug = self.enable_dev_tools(
            debug,
            dev_tools_ui,
            dev_tools_props_check,
            dev_tools_serve_dev_bundles,
            dev_tools_hot_reload,
            dev_tools_hot_reload_interval,
            dev_tools_hot_reload_watch_interval,
            dev_tools_hot_reload_max_retry,
            dev_tools_silence_routes_logging,
            dev_tools_prune_errors,
        )

        # Evaluate the env variables at runtime

        if "CONDA_PREFIX" in os.environ:
            # Some conda systems has issue with setting the host environment
            # to an invalid hostname.
            # Related issue: https://github.com/plotly/dash/issues/3069
            host = host or "127.0.0.1"
        else:
            host = host or os.getenv("HOST", "127.0.0.1")
        port = port or os.getenv("PORT", "8050")
        proxy = proxy or os.getenv("DASH_PROXY")

        # Verify port value
        try:
            port = int(port)
            assert port in range(1, 65536)
        except Exception as e:
            e.args = (f"Expecting an integer from 1 to 65535, found port={repr(port)}",)
            raise

        # so we only see the "Running on" message once with hot reloading
        # https://stackoverflow.com/a/57231282/9188800
        if os.getenv("WERKZEUG_RUN_MAIN") != "true":
            ssl_context = flask_run_options.get("ssl_context")
            protocol = "https" if ssl_context else "http"
            path = self.config.requests_pathname_prefix

            if proxy:
                served_url, proxied_url = map(urlparse, proxy.split("::"))

                def verify_url_part(served_part, url_part, part_name):
                    if served_part != url_part:
                        raise ProxyError(
                            f"""
                            {part_name}: {url_part} is incompatible with the proxy:
                                {proxy}
                            To see your app at {proxied_url.geturl()},
                            you must use {part_name}: {served_part}
                            """
                        )

                verify_url_part(served_url.scheme, protocol, "protocol")
                verify_url_part(served_url.hostname, host, "host")
                verify_url_part(served_url.port, port, "port")

                display_url = (
                    proxied_url.scheme,
                    proxied_url.hostname,
                    f":{proxied_url.port}" if proxied_url.port else "",
                    path,
                )
            else:
                display_url = (protocol, host, f":{port}", path)

            if not jupyter_dash or not jupyter_dash.in_ipython:
                self.logger.info("Dash is running on %s://%s%s%s\n", *display_url)

        if self.config.extra_hot_reload_paths:
            extra_files = flask_run_options["extra_files"] = []
            for path in self.config.extra_hot_reload_paths:
                if os.path.isdir(path):
                    for dirpath, _, filenames in os.walk(path):
                        for fn in filenames:
                            extra_files.append(os.path.join(dirpath, fn))
                elif os.path.isfile(path):
                    extra_files.append(path)

        if jupyter_dash.active:
            jupyter_dash.run_app(
                self,
                mode=jupyter_mode,
                width=jupyter_width,
                height=jupyter_height,
                host=host,
                port=port,
                server_url=jupyter_server_url,
            )
        else:
            self.server.run(host=host, port=port, debug=debug, **flask_run_options)

    def enable_pages(self):
        if not self.use_pages:
            return
        if self.pages_folder:
            _import_layouts_from_pages(self.config.pages_folder)

        @self.server.before_request
        def router():
            if self._got_first_request["pages"]:
                return
            self._got_first_request["pages"] = True

            inputs = {
                "pathname_": Input(_ID_LOCATION, "pathname"),
                "search_": Input(_ID_LOCATION, "search"),
            }
            inputs.update(self.routing_callback_inputs)

            if self._use_async:

                @self.callback(
                    Output(_ID_CONTENT, "children"),
                    Output(_ID_STORE, "data"),
                    inputs=inputs,
                    prevent_initial_call=True,
                )
                async def update(pathname_, search_, **states):
                    """
                    Updates dash.page_container layout on page navigation.
                    Updates the stored page title which will trigger the clientside callback to update the app title
                    """

                    query_parameters = _parse_query_string(search_)
                    page, path_variables = _path_to_page(
                        self.strip_relative_path(pathname_)
                    )

                    # get layout
                    if page == {}:
                        for module, page in _pages.PAGE_REGISTRY.items():
                            if module.split(".")[-1] == "not_found_404":
                                layout = page["layout"]
                                title = page["title"]
                                break
                        else:
                            layout = html.H1("404 - Page not found")
                            title = self.title
                    else:
                        layout = page.get("layout", "")
                        title = page["title"]

                    if callable(layout):
                        layout = await execute_async_function(
                            layout,
                            **{**(path_variables or {}), **query_parameters, **states},
                        )
                    if callable(title):
                        title = await execute_async_function(
                            title, **(path_variables or {})
                        )

                    return layout, {"title": title}

                _validate.check_for_duplicate_pathnames(_pages.PAGE_REGISTRY)
                _validate.validate_registry(_pages.PAGE_REGISTRY)

                # Set validation_layout
                if not self.config.suppress_callback_exceptions:
                    self.validation_layout = html.Div(
                        [
                            asyncio.run(execute_async_function(page["layout"]))
                            if callable(page["layout"])
                            else page["layout"]
                            for page in _pages.PAGE_REGISTRY.values()
                        ]
                        + [
                            # pylint: disable=not-callable
                            self.layout()
                            if callable(self.layout)
                            else self.layout
                        ]
                    )
                if _ID_CONTENT not in self.validation_layout:
                    raise Exception("`dash.page_container` not found in the layout")
            else:

                @self.callback(
                    Output(_ID_CONTENT, "children"),
                    Output(_ID_STORE, "data"),
                    inputs=inputs,
                    prevent_initial_call=True,
                )
                def update(pathname_, search_, **states):
                    """
                    Updates dash.page_container layout on page navigation.
                    Updates the stored page title which will trigger the clientside callback to update the app title
                    """

                    query_parameters = _parse_query_string(search_)
                    page, path_variables = _path_to_page(
                        self.strip_relative_path(pathname_)
                    )

                    # get layout
                    if page == {}:
                        for module, page in _pages.PAGE_REGISTRY.items():
                            if module.split(".")[-1] == "not_found_404":
                                layout = page["layout"]
                                title = page["title"]
                                break
                        else:
                            layout = html.H1("404 - Page not found")
                            title = self.title
                    else:
                        layout = page.get("layout", "")
                        title = page["title"]

                    if callable(layout):
                        layout = layout(
                            **{**(path_variables or {}), **query_parameters, **states}
                        )
                    if callable(title):
                        title = title(**(path_variables or {}))

                    return layout, {"title": title}

                _validate.check_for_duplicate_pathnames(_pages.PAGE_REGISTRY)
                _validate.validate_registry(_pages.PAGE_REGISTRY)

                # Set validation_layout
                if not self.config.suppress_callback_exceptions:
                    self.validation_layout = html.Div(
                        [
                            page["layout"]()
                            if callable(page["layout"])
                            else page["layout"]
                            for page in _pages.PAGE_REGISTRY.values()
                        ]
                        + [
                            # pylint: disable=not-callable
                            self.layout()
                            if callable(self.layout)
                            else self.layout
                        ]
                    )
                if _ID_CONTENT not in self.validation_layout:
                    raise Exception("`dash.page_container` not found in the layout")

            # Update the page title on page navigation
            self.clientside_callback(
                """
                function(data) {{
                    document.title = data.title
                }}
                """,
                Output(_ID_DUMMY, "children"),
                Input(_ID_STORE, "data"),
            )

    def run_server(self, *args, **kwargs):
        """`run_server` is a deprecated alias of `run` and may be removed in a
        future version. We recommend using `app.run` instead.

        See `app.run` for usage information.
        """
        warnings.warn(
            DeprecationWarning(
                "Dash.run_server is deprecated and will be removed in Dash 3.0"
            )
        )
        self.run(*args, **kwargs)
