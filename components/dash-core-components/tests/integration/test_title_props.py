# -*- coding: UTF-8 -*-

from dash.testing import wait
from dash import Dash, Input, Output, dcc, html


def test_ddot001_dropdown_radioitems_checklist_option_title(dash_dcc):
    app = Dash(__name__)

    options = [
        {"label": "New York City", "value": "NYC"},
        {"label": "Montréal", "value": "MTL"},
        {"label": "San Francisco", "value": "SF"},
    ]

    app.layout = html.Div(
        [
            dcc.Input(
                id="title_input",
                type="text",
                placeholder="Enter a title for New York City",
            ),
            dcc.Dropdown(id="dropdown_1", options=options, multi=True, value="NYC"),
            dcc.Dropdown(id="dropdown_2", options=options, multi=False, value="NYC"),
            dcc.Checklist(
                id="checklist_1",
                options=options,
                value=["NYC"],
                labelClassName="Select-value-label",
            ),
            dcc.RadioItems(
                id="radioitems_1",
                options=options,
                value="NYC",
                labelClassName="Select-value-label",
            ),
        ]
    )

    ids = ["dropdown_1", "dropdown_2", "checklist_1", "radioitems_1"]

    for id in ids:

        @app.callback(Output(id, "options"), [Input("title_input", "value")])
        def add_title_to_option(title):
            return [
                {"label": "New York City", "title": title, "value": "NYC"},
                {"label": "Montréal", "value": "MTL"},
                {"label": "San Francisco", "value": "SF"},
            ]

    dash_dcc.start_server(app)

    elements = [
        dash_dcc.wait_for_element("#dropdown_1 .Select-value"),
        dash_dcc.wait_for_element("#dropdown_2 .Select-value"),
        dash_dcc.wait_for_element("#checklist_1 .Select-value-label"),
        dash_dcc.wait_for_element("#radioitems_1 .Select-value-label"),
    ]

    component_title_input = dash_dcc.wait_for_element("#title_input")

    # Empty string title ('') (default for no title)

    for element in elements:
        wait.until(lambda: element.get_attribute("title") == "", 3)

    component_title_input.send_keys("The Big Apple")

    for element in elements:
        wait.until(lambda: element.get_attribute("title") == "The Big Apple", 3)

    dash_dcc.clear_input(component_title_input)

    component_title_input.send_keys("Gotham City?")

    for element in elements:
        wait.until(lambda: element.get_attribute("title") == "Gotham City?", 3)

    dash_dcc.clear_input(component_title_input)

    for element in elements:
        wait.until(lambda: element.get_attribute("title") == "", 3)

    assert dash_dcc.get_logs() == []
