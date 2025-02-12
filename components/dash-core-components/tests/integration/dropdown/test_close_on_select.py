import json

from dash import Dash, Input, Output, dcc, html
from selenium.webdriver.common.keys import Keys


def test_ddcos001_multi_stay_open(dash_dcc):
    app = Dash(__name__)
    app.layout = html.Div(
        [
            dcc.Dropdown(
                id="multi-dropdown",
                options=[
                    {"label": "New York City", "value": "NYC"},
                    {"label": "Montreal", "value": "MTL"},
                    {"label": "San Francisco", "value": "SF"},
                ],
                multi=True,
                close_on_select=False,
            ),
            html.Div(id="dropdown-value", style={"height": "10px", "width": "10px"}),
        ]
    )

    @app.callback(
        Output("dropdown-value", "children"),
        [Input("multi-dropdown", "value")],
    )
    def update_value(val):
        return json.dumps([v for v in val])

    dash_dcc.start_server(app)
    dropdown = dash_dcc.find_element("#multi-dropdown")
    dropdown.click()
    outer_menu = dash_dcc.find_element("#multi-dropdown .Select-menu-outer")
    outer_menu.click()
    dash_dcc.wait_for_contains_class("#multi-dropdown .Select", "is-open")
    outer_menu.click()
    dash_dcc.wait_for_contains_class("#multi-dropdown .Select", "is-open")
    dash_dcc.find_element("body").send_keys(Keys.ESCAPE)

    dash_dcc.wait_for_text_to_equal("#dropdown-value", '["MTL", "SF"]')


def test_ddcos002_multi_close(dash_dcc):
    app = Dash(__name__)
    app.layout = html.Div(
        [
            dcc.Dropdown(
                id="multi-dropdown",
                options=[
                    {"label": "New York City", "value": "NYC"},
                    {"label": "Montreal", "value": "MTL"},
                    {"label": "San Francisco", "value": "SF"},
                ],
                multi=True,
                close_on_select=True,
            ),
            html.Div(id="dropdown-value", style={"height": "10px", "width": "10px"}),
        ]
    )

    @app.callback(
        Output("dropdown-value", "children"),
        [Input("multi-dropdown", "value")],
    )
    def update_value(val):
        return json.dumps([v for v in val])

    dash_dcc.start_server(app)
    dropdown = dash_dcc.find_element("#multi-dropdown")
    dropdown.click()
    outer_menu = dash_dcc.find_element("#multi-dropdown .Select-menu-outer")
    outer_menu.click()
    dash_dcc.wait_for_no_elements("#multi-dropdown .Select-menu-outer")
    dash_dcc.find_element("body").send_keys(Keys.ESCAPE)

    dash_dcc.wait_for_text_to_equal("#dropdown-value", '["MTL"]')


def test_ddcos003_single_open(dash_dcc):
    app = Dash(__name__)
    app.layout = html.Div(
        [
            dcc.Dropdown(
                id="multi-dropdown",
                options=[
                    {"label": "New York City", "value": "NYC"},
                    {"label": "Montreal", "value": "MTL"},
                    {"label": "San Francisco", "value": "SF"},
                ],
                close_on_select=True,
            ),
            html.Div(id="dropdown-value", style={"height": "10px", "width": "10px"}),
        ]
    )

    @app.callback(
        Output("dropdown-value", "children"),
        [Input("multi-dropdown", "value")],
    )
    def update_value(val):
        return json.dumps(val)

    dash_dcc.start_server(app)
    dropdown = dash_dcc.find_element("#multi-dropdown")
    dropdown.click()
    outer_menu = dash_dcc.find_element("#multi-dropdown .Select-menu-outer")
    outer_menu.click()
    dash_dcc.wait_for_no_elements("#multi-dropdown .Select-menu-outer")
    dash_dcc.find_element("body").send_keys(Keys.ESCAPE)

    dash_dcc.wait_for_text_to_equal("#dropdown-value", '"MTL"')
