from dash import Dash, html


def test_api001_assets_path_ignore(dash_duo):
    app = Dash(
        __name__,
        assets_folder="test_assets_path_ignore_assets",
        assets_path_ignore=["should_be_ignored"],
    )
    app.index_string = """<!DOCTYPE html>
    <html>
        <head>
            {%metas%}
            <title>{%title%}</title>
            {%css%}
        </head>
        <body>
            <div id="normal-test-target"></div>
            <div id="ignored-test-target"></div>
            {%app_entry%}
            <footer>
                {%config%}
                {%scripts%}
                {%renderer%}
            </footer>
        </body>
    </html>"""

    app.layout = html.Div()

    dash_duo.start_server(app)

    assert (
        dash_duo.find_element("#normal-test-target").value_of_css_property(
            "background-color"
        )
        == "rgba(255, 0, 0, 1)"
    )

    assert (
        dash_duo.find_element("#ignored-test-target").value_of_css_property(
            "background-color"
        )
        != "rgba(255, 0, 0, 1)"
    )

    normal_target_content = dash_duo.find_element("#normal-test-target").text
    ignored_target_content = dash_duo.find_element("#ignored-test-target").text

    assert normal_target_content == "loaded"
    assert ignored_target_content != "loaded"
