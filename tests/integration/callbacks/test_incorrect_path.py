import os
import json
from multiprocessing import Value
from dash import Dash, Input, Output, dcc, html, MATCH, ALL, State
import dash.testing.wait as wait

def test_cb004_incorrect_path(dash_duo):
    """Modify the DOM tree by adding new components in the callbacks."""

    # some components don't exist in the initial render
    app = Dash(__name__, suppress_callback_exceptions=True)
    app.layout = html.Div(
        [
            dcc.Input(id={'type':'input', 'index':0}, value="initial value", className="persisted-0")
        ],
        id="output"
    )

    call_count = Value("i", 0)

    @app.callback(Output("output", "children"), [Input({"type":"input", "index": ALL}, "value")])
    def pad_output(input):
        import pdb
        pdb.set_trace()
        call_count.value += 1
        return html.Div(
            [
                dcc.Input(id={'type':'input', 'index': call_count.value}, value="sub input initial value", className=f'persisted-{call_count.value}'),
                html.Div(id="test", children=f'this is my output'),
                html.Div(id=f"sub-output-{call_count.value}", children=f'{input[0]}'),
            ]
        )

    # @app.callback(Output("sub-output-1", "children"), [Input("input", "value")])
    # def update_input(value):
    #     import pdb
    #     pdb.set_trace()

    dash_duo.start_server(app)

    dash_duo.wait_for_text_to_equal("#sub-output-1", "initial value")

    assert call_count.value == 1, "called once at initial stage"

    paths = dash_duo.redux_state_paths
    # assert paths["objs"] == {}
    # assert paths["strs"] == {
    #     "input": ["props", "children", 0],
    #     "output": ["props", "children", 1],
    #     "sub-input-1": [
    #         "props",
    #         "children",
    #         1,
    #         "props",
    #         "children",
    #         "props",
    #         "children",
    #         0,
    #     ],
    #     "sub-output-1": [
    #         "props",
    #         "children",
    #         1,
    #         "props",
    #         "children",
    #         "props",
    #         "children",
    #         1,
    #     ],
    # }, "the paths should include these new output IDs"

    # editing the input should modify the sub output
    import pdb
    pdb.set_trace()
    dash_duo.find_element('.persisted-1').send_keys("deadbeef")

    import pdb
    pdb.set_trace()
    dash_duo.wait_for_text_to_equal("#sub-output-1", "sub input initial valuedeadbeef")

    import pdb
    pdb.set_trace()
    dash_duo.find_element('.persisted-2').send_keys("deadbeef")

    import pdb
    pdb.set_trace()
    dash_duo.wait_for_text_to_equal("#sub-output-2", "sub input initial valuedeadbeef")

    import pdb
    pdb.set_trace()
    dash_duo.find_element('.persisted-3').send_keys("deadbeef")
    dash_duo.wait_for_text_to_equal("#sub-output-3", "sub input initial valuedeadbeefdeadbeef")

    import pdb
    pdb.set_trace()
    dash_duo.find_element('.persisted-4').send_keys("deadbeef")
    dash_duo.wait_for_text_to_equal("#sub-output-4", "sub input initial valuedead")