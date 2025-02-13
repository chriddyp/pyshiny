import dash
import dash.testing.wait as wait

from dash.dash_table import DataTable

from selenium.webdriver.common.keys import Keys

import pytest
import flaky

DATA_SIZE = 50


def get_table_defaults():
    return dict(id="table")


def get_mixed_markdown_table():
    props = get_table_defaults()

    data = [
        {
            "not-markdown-column": "this is not a markdown cell",
            "markdown-column": """```javascript
console.warn("this is a markdown cell")```"""
            if i % 2 == 0
            else """```javascript
console.log("logging things")
console.warn("this is a markdown cell")
```""",
            "also-not-markdown-column": str(i),
            "also-also-not-markdown-column": "this is also also not a markdown cell",
        }
        for i in range(0, DATA_SIZE)
    ]

    columns = [
        dict(id="not-markdown-column", name=["Not Markdown"]),
        dict(id="markdown-column", name=["Markdown"], presentation="markdown"),
        dict(id="also-not-markdown-column", name=["Also Not Markdown"]),
        dict(id="also-also-not-markdown-column", name=["Also Also Not Markdown"]),
    ]

    props["data"] = data
    props["columns"] = columns

    return props


def get_markdown_table():
    props = get_table_defaults()

    data = [
        {
            "markdown-headers": "{} row {}".format("#" * (i % 6), i),
            "markdown-italics": ("*{}*" if i % 2 == 0 else "_{}_").format(i),
            "markdown-links": "[Learn about {0}](http://en.wikipedia.org/wiki/{0})".format(
                i
            ),
            "markdown-lists": """1. Row number {0}
    - subitem {0}
      - subsubitem {0}
    - subitem two {0}
2. Next row {1}""".format(
                i, i + 1
            ),
            "markdown-tables": """Current | Next
--- | ---
{} | {}""".format(
                i, i + 1
            ),
            "markdown-quotes": "> A quote for row number {}".format(i),
            "markdown-inline-code": "This is row `{}` in this table.".format(i),
            "markdown-code-blocks": """```python
def hello_table(i={}):
    print("hello, " + i)""".format(
                i
            ),
            "markdown-images": "![image {} alt text](https://dash.plotly.com/assets/images/logo-plotly.png)".format(
                i
            ),
        }
        for i in range(0, DATA_SIZE)
    ]

    columns = [
        dict(id="markdown-headers", name=["", "Headers"], presentation="markdown"),
        dict(
            id="markdown-italics", name=["Emphasis", "Italics"], presentation="markdown"
        ),
        dict(id="markdown-links", name=["", "Links"], presentation="markdown"),
        dict(id="markdown-lists", name=["", "Lists"], presentation="markdown"),
        dict(id="markdown-tables", name=["", "Tables"], presentation="markdown"),
        dict(id="markdown-quotes", name=["", "Quotes"], presentation="markdown"),
        dict(
            id="markdown-inline-code", name=["", "Inline code"], presentation="markdown"
        ),
        dict(
            id="markdown-code-blocks", name=["", "Code blocks"], presentation="markdown"
        ),
        dict(id="markdown-images", name=["", "Images"], presentation="markdown"),
    ]

    props["data"] = data
    props["columns"] = columns

    return props


def get_app(props):
    app = dash.Dash(__name__)
    app.layout = DataTable(**props)

    return app


@pytest.mark.parametrize("props", [get_markdown_table(), get_mixed_markdown_table()])
def test_navg001_keyboard_through_9_10_cells(test, props):
    test.start_server(get_app(props))

    target = test.table("table")

    target.cell(9, 1).click()
    with test.hold(Keys.SHIFT):
        target.cell(10, 2).click()

    for row in range(9, 11):
        for col in range(1, 3):
            wait.until(lambda: target.cell(row, col).is_selected(), 3)

    assert target.cell(9, 1).is_focused()
    test.send_keys(Keys.ENTER)
    assert target.cell(10, 1).is_focused()
    test.send_keys(Keys.ENTER)
    assert target.cell(9, 2).is_focused()
    test.send_keys(Keys.ENTER)
    assert target.cell(10, 2).is_focused()
    test.send_keys(Keys.ENTER)
    assert target.cell(9, 1).is_focused()
    assert test.get_log_errors() == []


@pytest.mark.parametrize("props", [get_markdown_table(), get_mixed_markdown_table()])
def test_navg002_keyboard_after_ctrl_copy(test, props):
    test.start_server(get_app(props))

    target = test.table("table")

    target.cell(3, 1).click()
    test.copy()
    test.send_keys(Keys.ARROW_DOWN)

    assert target.cell(4, 1).is_focused()
    assert not target.cell(3, 1).is_focused()
    assert test.get_log_errors() == []


@flaky.flaky(max_runs=3)
@pytest.mark.parametrize("props", [get_markdown_table(), get_mixed_markdown_table()])
@pytest.mark.parametrize(
    "key,row,col",
    [
        (Keys.ARROW_DOWN, 1, 0),
        (Keys.ARROW_UP, -1, 0),
        (Keys.ARROW_LEFT, 0, -1),
        (Keys.ARROW_RIGHT, 0, 1),
    ],
)
def test_navg003_keyboard_can_move_down(test, props, key, row, col):
    test.start_server(get_app(props))

    target = test.table("table")
    target.cell(3, 1).click()
    test.send_keys(key)

    assert target.cell(3 + row, 1 + col).is_focused()
    assert not target.cell(3, 1).is_focused()
    assert test.get_log_errors() == []


@pytest.mark.parametrize("props", [get_mixed_markdown_table()])
def test_navg004_keyboard_between_md_and_standard_cells(test, props):
    test.start_server(get_app(props))

    target = test.table("table")
    target.cell(0, 0).click()

    cols = len(props["columns"])

    for i in range(1, cols):
        test.send_keys(Keys.ARROW_RIGHT)
        test.send_keys(Keys.ARROW_DOWN)
        assert target.cell(i, i).is_focused()

    assert test.get_log_errors() == []


@pytest.mark.parametrize("cell_selectable", [True, False])
def test_navg005_unselectable_cells(test, cell_selectable):
    app = dash.Dash(__name__)
    app.layout = DataTable(
        id="table",
        columns=[dict(id="a", name="a"), dict(id="b", name="b")],
        data=[dict(a=0, b=0), dict(a=1, b=2)],
        cell_selectable=cell_selectable,
    )

    test.start_server(app)

    target = test.table("table")
    target.cell(0, "a").click()

    assert target.cell(0, "a").is_selected() == cell_selectable
    assert test.get_log_errors() == []
