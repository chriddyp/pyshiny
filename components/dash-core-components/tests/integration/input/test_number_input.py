import time
import sys
from selenium.webdriver.common.keys import Keys


def test_inni001_invalid_numbers(ninput_app, dash_dcc):
    dash_dcc.start_server(ninput_app)
    for invalid_number in ("10e10000", "e+++eeeeeE-", "12-.3"):
        for debounce in ("false", "true"):
            elem = dash_dcc.find_element(f"#input_{debounce}")
            assert not elem.get_attribute("value"), "input should have no initial value"

            # onblur
            elem.send_keys(invalid_number)
            elem.send_keys(Keys.TAB)

            dash_dcc.wait_for_text_to_equal(f"#div_{debounce}", "")

            # Enter keypress
            dash_dcc.clear_input(elem)
            elem.send_keys(invalid_number)
            elem.send_keys(Keys.ENTER)

            dash_dcc.wait_for_text_to_equal(f"#div_{debounce}", "")

            dash_dcc.clear_input(elem)

    assert dash_dcc.get_logs() == []


def test_inni002_invalid_numbers_ui(dash_dcc, ninput_app):
    dash_dcc.start_server(ninput_app)
    elem = dash_dcc.find_element("#input_false")

    elem.send_keys("5e-325")  # smaller than Number.MIN_VALUE
    assert dash_dcc.wait_for_text_to_equal("#div_false", "0")

    dash_dcc.clear_input(elem)
    elem.send_keys("0.0.0")
    elem.send_keys(Keys.TAB)

    assert dash_dcc.find_element("#div_false").text != "0.0"
    time.sleep(0.5)
    dash_dcc.percy_snapshot("inni002 - input invalid number")

    assert dash_dcc.get_logs() == []


def test_inni003_invalid_numbers_range(dash_dcc, input_range_app):
    dash_dcc.start_server(input_range_app)  # range [10, 10000] step=3

    elem_range = dash_dcc.find_element("#range")
    elem_range.send_keys("1999")
    assert dash_dcc.find_element("#out").text == "1999"

    for invalid_number in ("0.0", "12", "10e10"):
        elem_range.send_keys(invalid_number)
        dash_dcc.wait_for_text_to_equal("#out", ""), "invalid value should return none"
        dash_dcc.clear_input(elem_range)

    elem_range.send_keys("-13")
    dash_dcc.wait_for_text_to_equal("#out", ""), "invalid value should return none"

    time.sleep(0.5)
    dash_dcc.percy_snapshot("inni003 - number out of range")

    assert dash_dcc.get_logs() == []


def test_inni010_valid_numbers(dash_dcc, ninput_app):
    dash_dcc.start_server(ninput_app)
    for num, op in (
        ("1.0", lambda x: int(float(x))),  # limitation of js/json
        ("10e10", lambda x: int(float(x))),
        ("-1.0001", float),
        (str(sys.float_info.max), float),
        (str(sys.float_info.min), float),
    ):
        elem = dash_dcc.find_element("#input_false")
        elem.send_keys(num)
        assert dash_dcc.wait_for_text_to_equal(
            "#div_false", str(op(num))
        ), "the valid number should be converted to expected form in callback"
        dash_dcc.clear_input(elem)

    assert dash_dcc.get_logs() == []


def test_currency_format(dash_dcc, ninput_app):
    dash_dcc.start_server(ninput_app)
    elem = dash_dcc.find_element("#input_currency")

    elem.send_keys("1234.56")
    elem.send_keys(Keys.TAB)

    assert dash_dcc.wait_for_text_to_equal(
        "#div_currency", "$1234.56"
    ), "the input value should be formatted with a currency symbol"

    dash_dcc.clear_input(elem)

    elem.send_keys("1000")
    elem.send_keys(Keys.TAB)

    assert dash_dcc.wait_for_text_to_equal(
        "#div_currency", "$1000.00"
    ), "the input value should be formatted with a currency symbol"

    assert dash_dcc.get_logs() == []
