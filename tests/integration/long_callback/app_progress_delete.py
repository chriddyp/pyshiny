from dash import Dash, Input, Output, State, html, clientside_callback, no_update
import time

from tests.integration.long_callback.utils import get_long_callback_manager

long_callback_manager = get_long_callback_manager()
handle = long_callback_manager.handle

app = Dash(__name__, long_callback_manager=long_callback_manager)

app.layout = html.Div(
    [
        html.Button("Start", id="start"),
        html.Div(id="output"),
        html.Div(id="progress-output"),
        html.Div(0, id="progress-counter"),
    ]
)
app.test_lock = lock = long_callback_manager.test_lock

clientside_callback(
    "function(_, previous) { return parseInt(previous) + 1;}",
    Output("progress-counter", "children"),
    Input("progress-output", "children"),
    State("progress-counter", "children"),
    prevent_initial_call=True,
)


@app.callback(
    Output("output", "children"),
    Input("start", "n_clicks"),
    progress=Output("progress-output", "children"),
    interval=200,
    background=True,
    prevent_initial_call=True,
)
def on_bg_progress(set_progress, _):
    with lock:
        set_progress("start")
        time.sleep(0.5)
        set_progress("stop")
        time.sleep(0.5)
        set_progress(no_update)
    return "done"


if __name__ == "__main__":
    app.run_server(debug=True)
