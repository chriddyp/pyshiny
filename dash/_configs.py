import os
import flask

# noinspection PyCompatibility
from . import exceptions
from ._utils import AttributeDict


def load_dash_env_vars():
    return AttributeDict(
        {
            var: os.getenv(var, os.getenv(var.lower()))
            for var in (
                "DASH_APP_NAME",
                "DASH_URL_BASE_PATHNAME",
                "DASH_ROUTES_PATHNAME_PREFIX",
                "DASH_REQUESTS_PATHNAME_PREFIX",
                "DASH_SUPPRESS_CALLBACK_EXCEPTIONS",
                "DASH_ASSETS_EXTERNAL_PATH",
                "DASH_INCLUDE_ASSETS_FILES",
                "DASH_COMPONENTS_CACHE_MAX_AGE",
                "DASH_INCLUDE_ASSETS_FILES",
                "DASH_SERVE_DEV_BUNDLES",
                "DASH_DEBUG",
                "DASH_UI",
                "DASH_PROPS_CHECK",
                "DASH_HOT_RELOAD",
                "DASH_HOT_RELOAD_INTERVAL",
                "DASH_HOT_RELOAD_WATCH_INTERVAL",
                "DASH_HOT_RELOAD_MAX_RETRY",
                "DASH_SILENCE_ROUTES_LOGGING",
                "DASH_PRUNE_ERRORS",
                "DASH_COMPRESS",
                "HOST",
                "PORT",
            )
        }
    )


DASH_ENV_VARS = load_dash_env_vars()  # used in tests


def get_combined_config(name, val, default=None):
    """Consolidate the config with priority from high to low provided init
    value > OS environ > default."""

    if val is not None:
        return val

    env = load_dash_env_vars().get(f"DASH_{name.upper()}")
    if env is None:
        return default

    return env.lower() == "true" if env.lower() in {"true", "false"} else env


def pathname_configs(
    url_base_pathname=None, routes_pathname_prefix=None, requests_pathname_prefix=None
):
    _pathname_config_error_message = """
    {} This is ambiguous.
    To fix this, set `routes_pathname_prefix` instead of `url_base_pathname`.

    Note that `requests_pathname_prefix` is the prefix for the AJAX calls that
    originate from the client (the web browser) and `routes_pathname_prefix` is
    the prefix for the API routes on the backend (this flask server).
    `url_base_pathname` will set `requests_pathname_prefix` and
    `routes_pathname_prefix` to the same value.
    If you need these to be different values then you should set
    `requests_pathname_prefix` and `routes_pathname_prefix`,
    not `url_base_pathname`.
    """
    url_base_pathname = get_combined_config("url_base_pathname", url_base_pathname)

    routes_pathname_prefix = get_combined_config(
        "routes_pathname_prefix", routes_pathname_prefix
    )

    requests_pathname_prefix = get_combined_config(
        "requests_pathname_prefix", requests_pathname_prefix
    )

    if url_base_pathname is not None and requests_pathname_prefix is not None:
        raise exceptions.InvalidConfig(
            _pathname_config_error_message.format(
                "You supplied `url_base_pathname` and `requests_pathname_prefix`."
            )
        )

    if url_base_pathname is not None and routes_pathname_prefix is not None:
        raise exceptions.InvalidConfig(
            _pathname_config_error_message.format(
                "You supplied `url_base_pathname` and `routes_pathname_prefix`."
            )
        )

    if url_base_pathname is not None and routes_pathname_prefix is None:
        routes_pathname_prefix = url_base_pathname
    elif routes_pathname_prefix is None:
        routes_pathname_prefix = "/"

    if not routes_pathname_prefix.startswith("/"):
        raise exceptions.InvalidConfig(
            "`routes_pathname_prefix` needs to start with `/`"
        )
    if not routes_pathname_prefix.endswith("/"):
        raise exceptions.InvalidConfig("`routes_pathname_prefix` needs to end with `/`")

    app_name = load_dash_env_vars().DASH_APP_NAME

    if not requests_pathname_prefix and app_name:
        requests_pathname_prefix = "/" + app_name + routes_pathname_prefix
    elif requests_pathname_prefix is None:
        requests_pathname_prefix = routes_pathname_prefix

    if not requests_pathname_prefix.startswith("/"):
        raise exceptions.InvalidConfig(
            "`requests_pathname_prefix` needs to start with `/`"
        )

    return url_base_pathname, routes_pathname_prefix, requests_pathname_prefix


def pages_folder_config(name, pages_folder, use_pages, root_path=None):
    if not pages_folder:
        return None
    is_custom_folder = str(pages_folder) != "pages"
    if root_path is None:
        root_path = flask.helpers.get_root_path(name)
    pages_folder_path = os.path.join(root_path, pages_folder)
    if (use_pages or is_custom_folder) and not os.path.isdir(pages_folder_path):
        error_msg = f"""
        A folder called `{pages_folder}` does not exist in `{pages_folder_path}`. If a folder for pages is not
        required in your application, set `pages_folder=""`. For example:
        `app = Dash(__name__,  pages_folder="")`
        """
        raise exceptions.InvalidConfig(error_msg)
    return pages_folder_path
