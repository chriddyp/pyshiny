import sys

import pytest

from tests.integration.long_callback.utils import setup_long_callback_app


@pytest.mark.skipif(
    sys.version_info < (3, 7), reason="Python 3.6 long callbacks tests hangs up"
)
def test_lcbc014_progress_delete(dash_duo, manager):
    with setup_long_callback_app(manager, "app_progress_delete") as app:
        dash_duo.start_server(app)

        dash_duo.wait_for_text_to_equal("#progress-output", "")
        assert dash_duo.find_element("#progress-counter").text == "0"

        dash_duo.find_element("#start").click()

        dash_duo.wait_for_text_to_equal("#progress-output", "start")
        assert dash_duo.find_element("#progress-counter").text == "1"

        dash_duo.wait_for_text_to_equal("#progress-output", "stop")
        assert dash_duo.find_element("#progress-counter").text == "2"

        dash_duo.wait_for_text_to_equal("#output", "done")
        assert dash_duo.find_element("#progress-counter").text == "2"
