# -*- coding: UTF-8 -*-
from dash import _validate, Dash, Input, Output, html, dcc
from dash.exceptions import PreventUpdate


def app_with_errors():
    darkly = (
        "https://stackpath.bootstrapcdn.com/bootswatch/4.5.2/darkly/bootstrap.min.css"
    )
    app = Dash(__name__, external_stylesheets=[darkly])

    app.layout = html.Div(
        [
            html.Button(id="python", children="Python exception", n_clicks=0),
            html.Div(id="output"),
        ]
    )

    @app.callback(Output("output", "children"), [Input("python", "n_clicks")])
    def update_output(n_clicks):
        if n_clicks == 1:
            return bad_sub()
        elif n_clicks == 2:
            raise Exception("Special 2 clicks exception")

    def bad_sub():
        return 1 / 0

    return app


def get_error_html(dash_duo, index):
    # error is in an iframe so is annoying to read out - get it from the store
    return dash_duo.driver.execute_script(
        "return store.getState().error.backEnd[{}].error.html;".format(index)
    )


def test_dveh001_python_errors(dash_duo):
    app = app_with_errors()

    dash_duo.start_server(
        app,
        debug=True,
        use_reloader=False,
        use_debugger=True,
        dev_tools_hot_reload=False,
    )

    assert dash_duo.get_logs() == []

    dash_duo.find_element("#python").click()
    dash_duo.wait_for_text_to_equal(dash_duo.devtools_error_count_locator, "1")
    dash_duo.percy_snapshot("devtools - Python exception - closed")

    dash_duo.find_element(".test-devtools-error-toggle").click()
    dash_duo.percy_snapshot("devtools - Python exception - open")

    dash_duo.find_element(".test-devtools-error-toggle").click()
    dash_duo.find_element("#python").click()

    dash_duo.wait_for_text_to_equal(dash_duo.devtools_error_count_locator, "2")
    dash_duo.percy_snapshot("devtools - Python exception - 2 errors")

    dash_duo.find_element(".test-devtools-error-toggle").click()
    dash_duo.percy_snapshot("devtools - Python exception - 2 errors open")

    # the top (first) error is the most recent one - ie from the second click
    error0 = get_error_html(dash_duo, 0)
    # user part of the traceback shown by default
    assert "in update_output" in error0
    assert "Special 2 clicks exception" in error0
    assert "in bad_sub" not in error0
    # dash and flask part of the traceback not included
    assert "%% callback invoked %%" not in error0
    assert "self.wsgi_app" not in error0

    error1 = get_error_html(dash_duo, 1)
    assert "in update_output" in error1
    assert "in bad_sub" in error1
    assert "ZeroDivisionError" in error1
    assert "%% callback invoked %%" not in error1
    assert "self.wsgi_app" not in error1


def test_dveh006_long_python_errors(dash_duo):
    app = app_with_errors()

    dash_duo.start_server(
        app,
        debug=True,
        use_reloader=False,
        use_debugger=True,
        dev_tools_hot_reload=False,
        dev_tools_prune_errors=False,
    )

    dash_duo.find_element("#python").click()
    dash_duo.wait_for_text_to_equal(dash_duo.devtools_error_count_locator, "1")
    dash_duo.find_element("#python").click()
    dash_duo.wait_for_text_to_equal(dash_duo.devtools_error_count_locator, "2")

    dash_duo.find_element(".test-devtools-error-toggle").click()

    error0 = get_error_html(dash_duo, 0)
    assert "in update_output" in error0
    assert "Special 2 clicks exception" in error0
    assert "in bad_sub" not in error0
    # dash and flask part of the traceback ARE included
    # since we set dev_tools_prune_errors=False
    assert "%% callback invoked %%" in error0
    assert "self.wsgi_app" in error0

    error1 = get_error_html(dash_duo, 1)
    assert "in update_output" in error1
    assert "in bad_sub" in error1
    assert "ZeroDivisionError" in error1
    assert "%% callback invoked %%" in error1
    assert "self.wsgi_app" in error1


def test_dveh002_prevent_update_not_in_error_msg(dash_duo):
    # raising PreventUpdate shouldn't display the error message
    app = Dash(__name__)

    app.layout = html.Div(
        [
            html.Button(id="python", children="Prevent update", n_clicks=0),
            html.Div(id="output"),
        ]
    )

    @app.callback(Output("output", "children"), [Input("python", "n_clicks")])
    def update_output(n_clicks):
        if n_clicks == 1:
            raise PreventUpdate
        if n_clicks == 2:
            raise Exception("An actual Python exception")

        return "button clicks: {}".format(n_clicks)

    dash_duo.start_server(
        app,
        debug=True,
        use_reloader=False,
        use_debugger=True,
        dev_tools_hot_reload=False,
    )

    for _ in range(3):
        dash_duo.find_element("#python").click()

    assert (
        dash_duo.find_element("#output").text == "button clicks: 3"
    ), "the click counts correctly in output"

    # two exceptions fired, but only a single exception appeared in the UI:
    # the prevent default was not displayed
    dash_duo.wait_for_text_to_equal(dash_duo.devtools_error_count_locator, "1")


def test_dveh003_validation_errors_in_place(dash_duo):
    app = Dash(__name__)

    app.layout = html.Div(
        [
            html.Button(id="button", children="update-graph", n_clicks=0),
            dcc.Graph(id="output", figure={"data": [{"y": [3, 1, 2]}]}),
        ]
    )

    # animate is a bool property
    @app.callback(Output("output", "animate"), [Input("button", "n_clicks")])
    def update_output(n_clicks):
        if n_clicks == 1:
            return n_clicks

    dash_duo.start_server(
        app,
        debug=True,
        use_reloader=False,
        use_debugger=True,
        dev_tools_hot_reload=False,
    )

    dash_duo.wait_for_element(".js-plotly-plot .main-svg")

    dash_duo.find_element("#button").click()
    dash_duo.wait_for_text_to_equal(dash_duo.devtools_error_count_locator, "1")
    dash_duo.find_element(".test-devtools-error-toggle").click()
    dash_duo.percy_snapshot("devtools - validation exception - open")


def test_dveh004_validation_errors_creation(dash_duo):
    app = Dash(__name__)

    app.layout = html.Div(
        [
            html.Button(id="button", children="update-graph", n_clicks=0),
            html.Div(id="output"),
        ]
    )

    # animate is a bool property
    @app.callback(Output("output", "children"), [Input("button", "n_clicks")])
    def update_output(n_clicks):
        if n_clicks == 1:
            return dcc.Graph(
                id="output", animate=0, figure={"data": [{"y": [3, 1, 2]}]}
            )

    dash_duo.start_server(
        app,
        debug=True,
        use_reloader=False,
        use_debugger=True,
        dev_tools_hot_reload=False,
    )

    dash_duo.wait_for_element("#button").click()
    dash_duo.wait_for_text_to_equal(dash_duo.devtools_error_count_locator, "1")
    dash_duo.find_element(".test-devtools-error-toggle").click()
    dash_duo.percy_snapshot("devtools - validation creation exception - open")


def test_dveh005_multiple_outputs(dash_duo):
    app = Dash(__name__)
    app.layout = html.Div(
        [
            html.Button(
                id="multi-output", children="trigger multi output update", n_clicks=0
            ),
            html.Div(id="multi-1"),
            html.Div(id="multi-2"),
        ]
    )

    @app.callback(
        [Output("multi-1", "children"), Output("multi-2", "children")],
        [Input("multi-output", "n_clicks")],
    )
    def update_outputs(n_clicks):
        if n_clicks == 0:
            return [
                "Output 1 - {} Clicks".format(n_clicks),
                "Output 2 - {} Clicks".format(n_clicks),
            ]
        else:
            n_clicks / 0

    dash_duo.start_server(
        app,
        debug=True,
        use_reloader=False,
        use_debugger=True,
        dev_tools_hot_reload=False,
    )

    dash_duo.find_element("#multi-output").click()
    dash_duo.wait_for_text_to_equal(dash_duo.devtools_error_count_locator, "1")
    dash_duo.find_element(".test-devtools-error-toggle").click()
    dash_duo.percy_snapshot("devtools - multi output Python exception - open")


def test_dveh006_truncate_callback(dash_duo):
    app = Dash(__name__)

    from dataclasses import dataclass
    from typing import List, Dict, Any

    @dataclass
    class GenericItemA:
        attribute_1: int
        attribute_2: str

    @dataclass
    class GenericItemB:
        key: str
        value: List[str]

    @dataclass
    class GenericItemC:
        identifier: int
        description: str

    @dataclass
    class GenericOptions:
        option_key: str
        option_value: Any

    @dataclass
    class GenericDataModel:
        ItemListA: List[GenericItemA]
        SingleItemB: GenericItemB
        NestedItemListC: List[List[GenericItemC]]
        Options: GenericOptions
        Metadata: Dict
        AdditionalInfo: Any

    app.layout = html.P(id="output")

    @app.callback(Output("output", "children"), Input("url", "href"))
    def get_width(_):
        item_list_a = [
            GenericItemA(attribute_1=123, attribute_2="Alpha"),
            GenericItemA(attribute_1=456, attribute_2="Beta")
        ]

        single_item_b = GenericItemB(key="Key1", value=["Item1", "Item2"])

        nested_item_list_c = [
            [GenericItemC(identifier=101, description="Description1")],
            [GenericItemC(identifier=102, description="Description2")]
        ]

        generic_options = GenericOptions(option_key="Option1", option_value="Value1")

        generic_metadata = {"meta_key": "meta_value"}

        additional_info = "Generic information"

        # Creating an instance of GenericDataModel
        generic_data_model = GenericDataModel(
            ItemListA=item_list_a,
            SingleItemB=single_item_b,
            NestedItemListC=nested_item_list_c,
            Options=generic_options,
            Metadata=generic_metadata,
            AdditionalInfo=additional_info
        )

        return generic_data_model

    dash_duo.start_server(
        app,
        debug=True,
        use_reloader=False,
        use_debugger=True,
        dev_tools_hot_reload=False,
    )

    dash_duo.find_element(".dash-debug-menu").click()
    dash_duo.wait_for_text_to_equal(dash_duo.devtools_error_count_locator, "1")

    assert len(get_error_html(dash_duo, 0)) == _validate.TRUNCATE_AT
