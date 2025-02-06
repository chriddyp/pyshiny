import os
import json
from multiprocessing import Value
from dash import Dash, Input, Output, dcc, html
import dash.testing.wait as wait


def test_cblp001_radio_buttons_callbacks_generating_children(dash_duo):
    TIMEOUT = 2
    with open(os.path.join(os.path.dirname(__file__), "state_path.json")) as fp:
        EXPECTED_PATHS = json.load(fp)

    percy_enabled = Value("b")

    def snapshot(name):
        percy_enabled.value = os.getenv("PERCY_ENABLE", "") != ""
        dash_duo.percy_snapshot(name=name)
        percy_enabled.value = False

    app = Dash(__name__)
    app.layout = html.Div(
        [
            dcc.RadioItems(
                options=[
                    {"label": "Chapter 1", "value": "chapter1"},
                    {"label": "Chapter 2", "value": "chapter2"},
                    {"label": "Chapter 3", "value": "chapter3"},
                    {"label": "Chapter 4", "value": "chapter4"},
                    {"label": "Chapter 5", "value": "chapter5"},
                ],
                value="chapter1",
                id="toc",
            ),
            html.Div(id="body"),
        ]
    )
    for script in dcc._js_dist:
        app.scripts.append_script(script)

    chapters = {
        "chapter1": html.Div(
            [
                html.H1("Chapter 1", id="chapter1-header"),
                dcc.Dropdown(
                    options=[{"label": i, "value": i} for i in ["NYC", "MTL", "SF"]],
                    value="NYC",
                    id="chapter1-controls",
                ),
                html.Label(id="chapter1-label"),
                dcc.Graph(id="chapter1-graph"),
            ]
        ),
        # Chapter 2 has the some of the same components in the same order
        # as Chapter 1. This means that they won't get remounted
        # unless they set their own keys are differently.
        # Switching back and forth between 1 and 2 implicitly
        # tests how components update when they aren't remounted.
        "chapter2": html.Div(
            [
                html.H1("Chapter 2", id="chapter2-header"),
                dcc.RadioItems(
                    options=[{"label": i, "value": i} for i in ["USA", "Canada"]],
                    value="USA",
                    id="chapter2-controls",
                ),
                html.Label(id="chapter2-label"),
                dcc.Graph(id="chapter2-graph"),
            ]
        ),
        # Chapter 3 has a different layout and so the components
        # should get rewritten
        "chapter3": [
            html.Div(
                html.Div(
                    [
                        html.H3("Chapter 3", id="chapter3-header"),
                        html.Label(id="chapter3-label"),
                        dcc.Graph(id="chapter3-graph"),
                        dcc.RadioItems(
                            options=[
                                {"label": i, "value": i} for i in ["Summer", "Winter"]
                            ],
                            value="Winter",
                            id="chapter3-controls",
                        ),
                    ]
                )
            )
        ],
        # Chapter 4 doesn't have an object to recursively traverse
        "chapter4": "Just a string",
    }

    call_counts = {
        "body": Value("i", 0),
        "chapter1-graph": Value("i", 0),
        "chapter1-label": Value("i", 0),
        "chapter2-graph": Value("i", 0),
        "chapter2-label": Value("i", 0),
        "chapter3-graph": Value("i", 0),
        "chapter3-label": Value("i", 0),
    }

    @app.callback(Output("body", "children"), [Input("toc", "value")])
    def display_chapter(toc_value):
        if not percy_enabled.value:
            call_counts["body"].value += 1
        return chapters[toc_value]

    app.config.suppress_callback_exceptions = True

    def generate_graph_callback(counterId):
        def callback(value):
            if not percy_enabled.value:
                call_counts[counterId].value += 1
            return {
                "data": [
                    {
                        "x": ["Call Counter for: {}".format(counterId)],
                        "y": [call_counts[counterId].value],
                        "type": "bar",
                    }
                ],
                "layout": {
                    "title": value,
                    "width": 500,
                    "height": 400,
                    "margin": {"autoexpand": False},
                },
            }

        return callback

    def generate_label_callback(id_):
        def update_label(value):
            if not percy_enabled.value:
                call_counts[id_].value += 1
            return value

        return update_label

    for chapter in ["chapter1", "chapter2", "chapter3"]:
        app.callback(
            Output("{}-graph".format(chapter), "figure"),
            [Input("{}-controls".format(chapter), "value")],
        )(generate_graph_callback("{}-graph".format(chapter)))

        app.callback(
            Output("{}-label".format(chapter), "children"),
            [Input("{}-controls".format(chapter), "value")],
        )(generate_label_callback("{}-label".format(chapter)))

    dash_duo.start_server(app)

    def check_chapter(chapter):
        dash_duo.wait_for_element("#{}-graph:not(.dash-graph--pending)".format(chapter))

        for key in dash_duo.redux_state_paths["strs"]:
            assert dash_duo.find_elements(
                "#{}".format(key)
            ), "each element should exist in the dom"

        value = (
            chapters[chapter][0]["{}-controls".format(chapter)].value
            if chapter == "chapter3"
            else chapters[chapter]["{}-controls".format(chapter)].value
        )

        # check the actual values
        dash_duo.wait_for_text_to_equal("#{}-label".format(chapter), value)

        wait.until(
            lambda: (
                dash_duo.driver.execute_script(
                    'return document.querySelector("'
                    + "#{}-graph:not(.dash-graph--pending) .js-plotly-plot".format(
                        chapter
                    )
                    + '").layout.title.text'
                )
                == value
            ),
            TIMEOUT,
        )

        assert not dash_duo.redux_state_is_loading, "loadingMap is empty"

    def check_call_counts(chapters, count):
        for chapter in chapters:
            assert call_counts[chapter + "-graph"].value == count
            assert call_counts[chapter + "-label"].value == count

    wait.until(lambda: call_counts["body"].value == 1, TIMEOUT)
    wait.until(lambda: call_counts["chapter1-graph"].value == 1, TIMEOUT)
    wait.until(lambda: call_counts["chapter1-label"].value == 1, TIMEOUT)
    check_call_counts(("chapter2", "chapter3"), 0)

    assert dash_duo.redux_state_paths == EXPECTED_PATHS["chapter1"]
    check_chapter("chapter1")
    snapshot(name="chapter-1")

    dash_duo.find_elements('input[type="radio"]')[1].click()  # switch chapters

    wait.until(lambda: call_counts["body"].value == 2, TIMEOUT)
    wait.until(lambda: call_counts["chapter2-graph"].value == 1, TIMEOUT)
    wait.until(lambda: call_counts["chapter2-label"].value == 1, TIMEOUT)
    check_call_counts(("chapter1",), 1)

    assert dash_duo.redux_state_paths == EXPECTED_PATHS["chapter2"]
    check_chapter("chapter2")
    snapshot(name="chapter-2")

    # switch to 3
    dash_duo.find_elements('input[type="radio"]')[2].click()

    wait.until(lambda: call_counts["body"].value == 3, TIMEOUT)
    wait.until(lambda: call_counts["chapter3-graph"].value == 1, TIMEOUT)
    wait.until(lambda: call_counts["chapter3-label"].value == 1, TIMEOUT)
    check_call_counts(("chapter2", "chapter1"), 1)

    assert dash_duo.redux_state_paths == EXPECTED_PATHS["chapter3"]
    check_chapter("chapter3")
    snapshot(name="chapter-3")

    dash_duo.find_elements('input[type="radio"]')[3].click()  # switch to 4
    dash_duo.wait_for_text_to_equal("#body", "Just a string")
    snapshot(name="chapter-4")

    paths = dash_duo.redux_state_paths
    assert paths["objs"] == {}
    for key in paths["strs"]:
        assert dash_duo.find_elements(
            "#{}".format(key)
        ), "each element should exist in the dom"

    assert paths["strs"] == {
        "toc": ["props", "children", 0],
        "body": ["props", "children", 1],
    }

    dash_duo.find_elements('input[type="radio"]')[0].click()

    wait.until(
        lambda: dash_duo.redux_state_paths == EXPECTED_PATHS["chapter1"], TIMEOUT
    )
    check_chapter("chapter1")
    snapshot(name="chapter-1-again")
