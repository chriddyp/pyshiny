import pytest
from selenium.common.exceptions import WebDriverException
from dash import Dash, Input, Output, dcc, html


ALLOWED_TYPES = (
    "text",
    "number",
    "password",
    "email",
    "range",
    "search",
    "tel",
    "url",
    "hidden",
)


def test_inbs001_all_types(dash_dcc):
    def input_id(type_):
        return f"input_{type_}"

    app = Dash(__name__)
    app.layout = html.Div(
        [
            dcc.Input(id=input_id(_), type=_, placeholder=f"input type {_}")
            for _ in ALLOWED_TYPES
        ]
        + [html.Div(id="output")]
        + [
            dcc.Input(id=input_id(_) + "2", type=_, placeholder=f"input type {_}")
            for _ in ALLOWED_TYPES
        ]
    )

    @app.callback(
        Output("output", "children"),
        [Input(input_id(_), "value") for _ in ALLOWED_TYPES],
    )
    def cb_render(*vals):
        return " | ".join((val for val in vals if val))

    dash_dcc.start_server(app)

    assert (
        dash_dcc.find_element("#input_hidden").get_attribute("type") == "hidden"
    ), "hidden input element should present with hidden type"

    for atype in ALLOWED_TYPES[:-1]:
        dash_dcc.find_element(f"#input_{atype}").send_keys(
            f"test intp001 - input[{atype}]"
        )

    with pytest.raises(WebDriverException):
        dash_dcc.find_element("#input_hidden").send_keys("no interaction")

    dash_dcc.percy_snapshot("inbs001 - dcc callback output rendering")

    assert dash_dcc.get_logs() == []


def test_inbs002_user_class(dash_dcc):
    app = Dash(__name__, assets_folder="../../assets")

    app.layout = html.Div(className="test-input-css", children=[dcc.Input()])

    dash_dcc.start_server(app)

    dash_dcc.wait_for_style_to_equal(
        ".test-input-css input", "borderColor", "rgb(255, 105, 180)"
    )
    dash_dcc.wait_for_style_to_equal(".test-input-css input", "width", "420px")

    assert dash_dcc.get_logs() == []


def test_inbs003_styles_are_scoped(dash_dcc):
    app = Dash(__name__)

    app.index_string = """
    <html>
        <body>
            <input id="ExternalInput" required />
            {%app_entry%}
            {%config%}
            {%scripts%}
            {%renderer%}
        </body>
    </html>
    """

    app.layout = html.Div(
        className="test-input-css",
        children=[dcc.Input(id="DashInput", required=True, className="unittest")],
    )

    dash_dcc.start_server(app)

    external_input = dash_dcc.find_element("#ExternalInput")
    dash_input = dash_dcc.find_element(".unittest")

    external_outline_css = external_input.value_of_css_property("outline")
    dash_outline_css = dash_input.value_of_css_property("outline")

    assert external_outline_css != dash_outline_css

@pytest.mark.parametrize(
    "initial_text, invalid_char, cursor_position_before, expected_text, expected_cursor_position",
    [
        ("abcdddef", "/", 2, "ab/cdddef", 3),
        ("abcdef", "$", 2, "ab$cdef", 3),
        ("abcdef", "$", 3, "abc$def", 4),
        ("abcdef", "A", 4, "abcdAef", 5),  # valid character
    ],
)
def test_inbs004_cursor_position_on_invalid_input(
    dash_dcc,
    initial_text,
    invalid_char,
    cursor_position_before,
    expected_text,
    expected_cursor_position,
):
    app = Dash(__name__)

    app.layout = html.Div(
        [
            dcc.Input(
                id="test-input",
                type="text",
                placeholder="File name",
                className="create_file_input",
                pattern="[a-zA-Z_][a-zA-Z0-9_]*",
            ),
            html.Div(id="output"),
        ]
    )

    dash_dcc.start_server(app)
    input_elem = dash_dcc.find_element("#test-input")

    input_elem.send_keys(initial_text)
    assert (
        input_elem.get_attribute("value") == initial_text
    ), "Initial text should match"

    dash_dcc.driver.execute_script(
        f"""
        var elem = arguments[0];
        elem.setSelectionRange({cursor_position_before}, {cursor_position_before});
        elem.focus();
    """,
        input_elem,
    )

    input_elem.send_keys(invalid_char)

    assert (
        input_elem.get_attribute("value") == expected_text
    ), f"Input should be {expected_text}"

    cursor_position = dash_dcc.driver.execute_script(
        """
        var elem = arguments[0];
        return elem.selectionStart;
    """,
        input_elem,
    )

    assert (
        cursor_position == expected_cursor_position
    ), f"Cursor should be at position {expected_cursor_position}"

    assert dash_dcc.get_logs() == []
