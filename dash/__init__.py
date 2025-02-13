# pylint: disable=C0413
# __plotly_dash is for the "make sure you don't have a dash.py" check
# must come before any other imports.
__plotly_dash = True
from .dependencies import (  # noqa: F401,E402
    Input,  # noqa: F401,E402
    Output,  # noqa: F401,E402,
    State,  # noqa: F401,E402
    ClientsideFunction,  # noqa: F401,E402
    MATCH,  # noqa: F401,E402
    ALL,  # noqa: F401,E402
    ALLSMALLER,  # noqa: F401,E402
)  # noqa: F401,E402
from . import development  # noqa: F401,E402
from . import exceptions  # noqa: F401,E402
from . import resources  # noqa: F401,E402
from . import dcc  # noqa: F401,E402
from . import html  # noqa: F401,E402
from . import dash_table  # noqa: F401,E402
from .version import __version__  # noqa: F401,E402
from ._callback_context import callback_context, set_props  # noqa: F401,E402
from ._callback import callback, clientside_callback  # noqa: F401,E402
from ._get_app import get_app  # noqa: F401,E402
from ._get_paths import (  # noqa: F401,E402
    get_asset_url,
    get_relative_path,
    strip_relative_path,
)
from .background_callback import (  # noqa: F401,E402
    CeleryManager,
    DiskcacheManager,
)


from ._pages import register_page, PAGE_REGISTRY as page_registry  # noqa: F401,E402
from .dash import (  # noqa: F401,E402
    Dash,
    no_update,
    page_container,
)
from ._patch import Patch  # noqa: F401,E402
from ._jupyter import jupyter_dash  # noqa: F401,E402

from ._hooks import hooks  # noqa: F401,E402

ctx = callback_context


def _jupyter_nbextension_paths():
    return [
        {
            "section": "notebook",
            "src": "nbextension",
            "dest": "dash",
            "require": "dash/main",
        }
    ]


__all__ = [
    "Input",
    "Output",
    "State",
    "clientside_callback",
    "ClientsideFunction",
    "MATCH",
    "ALLSMALLER",
    "ALL",
    "development",
    "exceptions",
    "dcc",
    "html",
    "dash_table",
    "__version__",
    "callback_context",
    "set_props",
    "callback",
    "get_app",
    "get_asset_url",
    "get_relative_path",
    "strip_relative_path",
    "CeleryManager",
    "DiskcacheManager",
    "register_page",
    "page_registry",
    "Dash",
    "no_update",
    "page_container",
    "Patch",
    "jupyter_dash",
    "ctx",
    "hooks",
]
