import json
import flask
import pytest
from multiprocessing import Value

from dash import Dash, Output, Input, html, dcc
from dash.types import RendererHooks


def test_rdrh001_request_hooks(dash_duo):
    app = Dash(__name__)

    app.index_string = """<!DOCTYPE html>
    <html>
        <head>
            {%metas%}
            <title>{%title%}</title>
            {%favicon%}
            {%css%}
        </head>
        <body>
            <div id="top">Testing custom DashRenderer</div>
            {%app_entry%}
            <footer>
                {%config%}
                {%scripts%}
                <script id="_dash-renderer" type"application/json">
                    const renderer = new DashRenderer({
                        request_pre: (payload) => {
                            var output = document.getElementById('output-pre')
                            var outputPayload = document.getElementById('output-pre-payload')
                            if(output) {
                                output.innerHTML = 'request_pre changed this text!';
                            }
                            if(outputPayload) {
                                outputPayload.innerHTML = JSON.stringify(payload);
                            }
                        },
                        request_post: (payload, response) => {
                            var output = document.getElementById('output-post')
                            var outputPayload = document.getElementById('output-post-payload')
                            var outputResponse = document.getElementById('output-post-response')
                            if(output) {
                                output.innerHTML = 'request_post changed this text!';
                            }
                            if(outputPayload) {
                                outputPayload.innerHTML = JSON.stringify(payload);
                            }
                            if(outputResponse) {
                                outputResponse.innerHTML = JSON.stringify(response);
                            }
                        }
                    })
                </script>
            </footer>
            <div id="bottom">With request hooks</div>
        </body>
    </html>"""

    app.layout = html.Div(
        [
            dcc.Input(id="input", value="initial value"),
            html.Div(
                html.Div(
                    [
                        html.Div(id="output-1"),
                        html.Div(id="output-pre"),
                        html.Div(id="output-pre-payload"),
                        html.Div(id="output-post"),
                        html.Div(id="output-post-payload"),
                        html.Div(id="output-post-response"),
                    ]
                )
            ),
        ]
    )

    @app.callback(Output("output-1", "children"), [Input("input", "value")])
    def update_output(value):
        return value

    dash_duo.start_server(app)

    _in = dash_duo.find_element("#input")
    dash_duo.clear_input(_in)

    _in.send_keys("fire request hooks")

    dash_duo.wait_for_text_to_equal("#output-1", "fire request hooks")
    dash_duo.wait_for_text_to_equal("#output-pre", "request_pre changed this text!")
    dash_duo.wait_for_text_to_equal("#output-post", "request_post changed this text!")

    assert json.loads(dash_duo.find_element("#output-pre-payload").text) == {
        "output": "output-1.children",
        "outputs": {"id": "output-1", "property": "children"},
        "changedPropIds": ["input.value"],
        "parsedChangedPropsIds": ["input.value"],
        "inputs": [{"id": "input", "property": "value", "value": "fire request hooks"}],
    }

    assert json.loads(dash_duo.find_element("#output-post-payload").text) == {
        "output": "output-1.children",
        "outputs": {"id": "output-1", "property": "children"},
        "changedPropIds": ["input.value"],
        "parsedChangedPropsIds": ["input.value"],
        "inputs": [{"id": "input", "property": "value", "value": "fire request hooks"}],
    }

    assert json.loads(dash_duo.find_element("#output-post-response").text) == {
        "output-1": {"children": "fire request hooks"}
    }

    assert dash_duo.find_element("#top").text == "Testing custom DashRenderer"
    assert dash_duo.find_element("#bottom").text == "With request hooks"

    assert dash_duo.get_logs() == []


def test_rdrh002_with_custom_renderer_interpolated(dash_duo):
    renderer = """
        <script id="_dash-renderer" type="application/javascript">
            console.log('firing up a custom renderer!')
            const renderer = new DashRenderer({
                request_pre: () => {
                    var output = document.getElementById('output-pre')
                    if(output) {
                        output.innerHTML = 'request_pre was here!';
                    }
                },
                request_post: () => {
                    var output = document.getElementById('output-post')
                    if(output) {
                        output.innerHTML = 'request_post!!!';
                    }
                }
            })
        </script>
    """

    class CustomDash(Dash):
        def interpolate_index(self, **kwargs):
            return """<!DOCTYPE html>
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
            </html>""".format(
                app_entry=kwargs["app_entry"],
                config=kwargs["config"],
                scripts=kwargs["scripts"],
                renderer=renderer,
            )

    app = CustomDash()

    app.layout = html.Div(
        [
            dcc.Input(id="input", value="initial value"),
            html.Div(
                html.Div(
                    [
                        html.Div(id="output-1"),
                        html.Div(id="output-pre"),
                        html.Div(id="output-post"),
                    ]
                )
            ),
        ]
    )

    @app.callback(Output("output-1", "children"), [Input("input", "value")])
    def update_output(value):
        return value

    dash_duo.start_server(app)

    input1 = dash_duo.find_element("#input")
    dash_duo.clear_input(input1)

    input1.send_keys("fire request hooks")

    dash_duo.wait_for_text_to_equal("#output-1", "fire request hooks")
    assert dash_duo.find_element("#output-pre").text == "request_pre was here!"
    assert dash_duo.find_element("#output-post").text == "request_post!!!"
    assert dash_duo.find_element("#custom-header").text == "My custom header"
    assert dash_duo.find_element("#custom-footer").text == "My custom footer"

    assert dash_duo.get_logs() == []


# @flaky(max_runs=3)
@pytest.mark.parametrize("expiry_code", [401, 400])
def test_rdrh003_refresh_jwt(expiry_code, dash_duo):
    app = Dash(__name__)

    app.index_string = """<!DOCTYPE html>
    <html>
        <head>
            {%metas%}
            <title>{%title%}</title>
            {%favicon%}
            {%css%}
        </head>
        <body>
            <div>Testing custom DashRenderer</div>
            {%app_entry%}
            <footer>
                {%config%}
                {%scripts%}
                <script id="_dash-renderer" type"application/json">
                    const renderer = new DashRenderer({
                        request_refresh_jwt: (old_token) => {
                            console.log("refreshing token", old_token);
                            var new_token = "." + (old_token || "");
                            var output = document.getElementById('output-token')
                            if(output) {
                                output.innerHTML = new_token;
                            }
                            return new_token;
                        }
                    })
                </script>
            </footer>
            <div>With request hooks</div>
        </body>
    </html>"""

    app.layout = html.Div(
        [
            dcc.Input(id="input", value="initial value"),
            html.Div(html.Div([html.Div(id="output-1"), html.Div(id="output-token")])),
        ]
    )

    @app.callback(
        Output("output-1", "children"),
        [Input("input", "value")],
        prevent_initial_call=True,
    )
    def update_output(value):
        jwt_token.value = len(value) + 1
        return value

    jwt_token = Value("i", 0)

    # test with an auth layer that requires a JWT with a certain length
    @app.server.before_request
    def add_auth():
        if flask.request.method != "OPTIONS":
            token = flask.request.headers.environ.get("HTTP_AUTHORIZATION")
            if jwt_token.value and (
                not token or len(token) != jwt_token.value + len("Bearer ")
            ):
                # Read the data to prevent bug with base http server.
                flask.request.get_json(silent=True)
                flask.abort(expiry_code, description="JWT Expired " + str(token))

    dash_duo.start_server(app)

    _in = dash_duo.find_element("#input")
    dash_duo.clear_input(_in)

    dash_duo.wait_for_text_to_equal("#output-1", "")

    _in.send_keys(".")
    dash_duo.wait_for_text_to_equal("#output-1", ".")
    dash_duo.wait_for_text_to_equal("#output-token", ".")

    _in.send_keys(".")
    dash_duo.wait_for_text_to_equal("#output-1", "..")
    dash_duo.wait_for_text_to_equal("#output-token", "..")

    _in.send_keys(".")
    dash_duo.wait_for_text_to_equal("#output-1", "...")
    dash_duo.wait_for_text_to_equal("#output-token", "...")

    assert len(dash_duo.get_logs()) == 3


def test_rdrh004_layout_hooks(dash_duo):
    hooks: RendererHooks = {
        "layout_pre": """
            () => {
                var layoutPre = document.createElement('div');
                layoutPre.setAttribute('id', 'layout-pre');
                layoutPre.innerHTML = 'layout_pre generated this text';
                document.body.appendChild(layoutPre);
            }
        """,
        "layout_post": """
            (response) => {
                response.props.children = "layout_post generated this text";
            }
        """,
    }

    app = Dash(__name__, hooks=hooks)
    app.layout = html.Div(id="layout")

    dash_duo.start_server(app)

    dash_duo.wait_for_text_to_equal("#layout-pre", "layout_pre generated this text")
    dash_duo.wait_for_text_to_equal("#layout", "layout_post generated this text")

    assert dash_duo.get_logs() == []
