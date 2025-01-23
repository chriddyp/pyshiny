# pylint: disable=missing-docstring
import os
import sys
import time
import logging
import warnings
import percy
import requests

from selenium import webdriver
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains

from selenium.common.exceptions import (
    WebDriverException,
    TimeoutException,
    MoveTargetOutOfBoundsException,
)

from dash.testing.wait import (
    text_to_equal,
    style_to_equal,
    class_to_equal,
    contains_text,
    contains_class,
    until,
)
from dash.testing.dash_page import DashPageMixin
from dash.testing.errors import DashAppLoadingError, BrowserError, TestingTimeoutError
from dash.testing.consts import SELENIUM_GRID_DEFAULT


logger = logging.getLogger(__name__)


class Browser(DashPageMixin):
    # pylint: disable=too-many-arguments
    def __init__(
        self,
        browser,
        remote=False,
        remote_url=None,
        headless=False,
        options=None,
        download_path="",
        percy_run=True,
        percy_finalize=True,
        percy_assets_root="",
        wait_timeout=10,
        pause=False,
        driver=None,
    ):
        self._browser = browser.lower()
        self._remote_url = remote_url
        self._remote = (
            True if remote_url and remote_url != SELENIUM_GRID_DEFAULT else remote
        )
        self._headless = headless
        self._options = options
        self._download_path = download_path
        self._wait_timeout = wait_timeout
        self._percy_finalize = percy_finalize
        self._percy_run = percy_run
        self._pause = pause

        if driver:
            self._driver = driver
        else:
            self._driver = until(self.get_webdriver, timeout=1)
        self._driver.implicitly_wait(2)

        self._wd_wait = WebDriverWait(self.driver, wait_timeout)
        self._last_ts = 0
        self._url = None

        self._window_idx = 0  # switch browser tabs

        if self._percy_run:
            self.percy_runner = percy.Runner(
                loader=percy.ResourceLoader(
                    webdriver=self.driver,
                    base_url="/assets",
                    root_dir=percy_assets_root,
                )
            )
            self.percy_runner.initialize_build()

        logger.debug("initialize browser with arguments")
        logger.debug("  headless => %s", self._headless)
        logger.debug("  download_path => %s", self._download_path)
        logger.debug("  percy asset root => %s", os.path.abspath(percy_assets_root))

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, traceback):
        try:
            self.driver.quit()
            if self._percy_run and self._percy_finalize:
                logger.info("percy runner finalize build now")
                self.percy_runner.finalize_build()
            else:
                logger.info("percy finalize relies on CI job")
        except WebDriverException:
            logger.exception("webdriver quit was not successful")
        except percy.errors.Error:
            logger.exception("percy runner failed to finalize properly")

    def visit_and_snapshot(
        self,
        resource_path,
        hook_id,
        wait_for_callbacks=True,
        convert_canvases=False,
        assert_check=True,
        stay_on_page=False,
        widths=None,
    ):
        try:
            path = resource_path.lstrip("/")
            if path != resource_path:
                logger.warning("we stripped the left '/' in resource_path")
            self.driver.get(f"{self.server_url.rstrip('/')}/{path}")

            # wait for the hook_id to present and all callbacks get fired
            self.wait_for_element_by_id(hook_id)
            self.percy_snapshot(
                path,
                wait_for_callbacks=wait_for_callbacks,
                convert_canvases=convert_canvases,
                widths=widths,
            )
            if assert_check:
                assert not self.find_elements(
                    "div.dash-debug-alert"
                ), "devtools should not raise an error alert"
            if not stay_on_page:
                self.driver.back()
        except WebDriverException as e:
            logger.exception("snapshot at resource %s error", path)
            raise e

    def percy_snapshot(
        self, name="", wait_for_callbacks=False, convert_canvases=False, widths=None
    ):
        """percy_snapshot - visual test api shortcut to `percy_runner.snapshot`.
        It also combines the snapshot `name` with the Python version,
        args:
        - name: combined with the python version to give the final snapshot name
        - wait_for_callbacks: default False, whether to wait for Dash callbacks,
            after an extra second to ensure that any relevant callbacks have
            been initiated
        - convert_canvases: default False, whether to convert all canvas elements
            in the DOM into static images for percy to see. They will be restored
            after the snapshot is complete.
        - widths: a list of pixel widths for percy to render the page with. Note
            that this does not change the browser in which the DOM is constructed,
            so the width will only affect CSS, not JS-driven layout.
            Defaults to [1280]
        """
        if widths is None:
            widths = [1280]

        logger.info("taking snapshot name => %s", name)
        try:
            if wait_for_callbacks:
                # the extra one second sleep adds safe margin in the context
                # of wait_for_callbacks
                time.sleep(1)
                until(self._wait_for_callbacks, timeout=40, poll=0.3)
        except TestingTimeoutError:
            # API will log the error but this TimeoutError should not block
            # the test execution to continue and it will still do a snapshot
            # as diff reference for the build run.
            logger.error(
                "wait_for_callbacks failed => status of invalid rqs %s",
                self.redux_state_rqs,
            )

        if convert_canvases:
            self.driver.execute_script(
                """
                const stash = window._canvasStash = [];
                Array.from(document.querySelectorAll('canvas')).forEach(c => {
                    const i = document.createElement('img');
                    i.src = c.toDataURL();
                    i.width = c.width;
                    i.height = c.height;
                    i.setAttribute('style', c.getAttribute('style'));
                    i.className = c.className;
                    i.setAttribute('data-canvasnum', stash.length);
                    stash.push(c);
                    c.parentElement.insertBefore(i, c);
                    c.parentElement.removeChild(c);
                });
            """
            )

        try:
            self.percy_runner.snapshot(name=name, widths=widths)
        except requests.HTTPError as err:
            # Ignore retries.
            if err.request.status_code != 400:
                raise err

        if convert_canvases:
            self.driver.execute_script(
                """
                const stash = window._canvasStash;
                Array.from(
                    document.querySelectorAll('img[data-canvasnum]')
                ).forEach(i => {
                    const c = stash[+i.getAttribute('data-canvasnum')];
                    i.parentElement.insertBefore(c, i);
                    i.parentElement.removeChild(i);
                });
                delete window._canvasStash;
            """
            )

    def take_snapshot(self, name):
        """Hook method to take snapshot when a selenium test fails. The
        snapshot is placed under.

            - `/tmp/dash_artifacts` in linux
            - `%TEMP` in windows
        with a filename combining test case name and the
        running selenium session id
        """
        target = "/tmp/dash_artifacts" if not self._is_windows() else os.getenv("TEMP")
        if not os.path.exists(target):
            try:
                os.mkdir(target)
            except OSError:
                logger.exception("cannot make artifacts")

        self.driver.save_screenshot(f"{target}/{name}_{self.session_id}.png")

    def find_element(self, selector, attribute="CSS_SELECTOR"):
        """find_element returns the first found element by the attribute `selector`
        shortcut to `driver.find_element(By.CSS_SELECTOR, ...)`.
        args:
        - attribute: the attribute type to search for, aligns with the Selenium
            API's `By` class. default "CSS_SELECTOR"
            valid values: "CSS_SELECTOR", "ID", "NAME", "TAG_NAME",
            "CLASS_NAME", "LINK_TEXT", "PARTIAL_LINK_TEXT", "XPATH"
        """
        return self.driver.find_element(getattr(By, attribute.upper()), selector)

    def find_elements(self, selector, attribute="CSS_SELECTOR"):
        """find_elements returns a list of all elements matching the attribute
        `selector`. Shortcut to `driver.find_elements(By.CSS_SELECTOR, ...)`.
        args:
        - attribute: the attribute type to search for, aligns with the Selenium
            API's `By` class. default "CSS_SELECTOR"
            valid values: "CSS_SELECTOR", "ID", "NAME", "TAG_NAME",
            "CLASS_NAME", "LINK_TEXT", "PARTIAL_LINK_TEXT", "XPATH"
        """
        return self.driver.find_elements(getattr(By, attribute.upper()), selector)

    def _get_element(self, elem_or_selector):
        if isinstance(elem_or_selector, str):
            return self.find_element(elem_or_selector)
        return elem_or_selector

    def _wait_for(self, method, timeout, msg):
        """Abstract generic pattern for explicit WebDriverWait."""
        try:
            _wait = (
                self._wd_wait
                if timeout is None
                else WebDriverWait(self.driver, timeout)
            )
            logger.debug(
                "method, timeout, poll => %s %s %s",
                method,
                _wait._timeout,  # pylint: disable=protected-access
                _wait._poll,  # pylint: disable=protected-access
            )

            return _wait.until(method)
        except Exception as err:
            if callable(msg):
                message = msg(self.driver)
            else:
                message = msg
            raise TimeoutException(message) from err

    def wait_for_element(self, selector, timeout=None):
        """wait_for_element is shortcut to `wait_for_element_by_css_selector`
        timeout if not set, equals to the fixture's `wait_timeout`."""
        return self.wait_for_element_by_css_selector(selector, timeout)

    def wait_for_element_by_css_selector(self, selector, timeout=None):
        """Explicit wait until the element is present, timeout if not set,
        equals to the fixture's `wait_timeout` shortcut to `WebDriverWait` with
        `EC.presence_of_element_located`."""
        return self._wait_for(
            EC.presence_of_element_located(
                (By.CSS_SELECTOR, selector),
            ),
            timeout,
            f"timeout {timeout or self._wait_timeout}s => waiting for selector {selector}",
        )

    def wait_for_no_elements(self, selector, timeout=None):
        """Explicit wait until an element is NOT found. timeout defaults to
        the fixture's `wait_timeout`."""
        until(
            # if we use get_elements it waits a long time to see if they appear
            # so this one calls out directly to execute_script
            lambda: self.driver.execute_script(
                f"return document.querySelectorAll('{selector}').length"
            )
            == 0,
            timeout or self._wait_timeout,
        )

    def wait_for_element_by_id(self, element_id, timeout=None):
        """Explicit wait until the element is present, timeout if not set,
        equals to the fixture's `wait_timeout` shortcut to `WebDriverWait` with
        `EC.presence_of_element_located`."""
        return self._wait_for(
            EC.presence_of_element_located(
                (By.ID, element_id),
            ),
            timeout,
            f"timeout {timeout or self._wait_timeout}s => waiting for element id {element_id}",
        )

    def wait_for_class_to_equal(self, selector, classname, timeout=None):
        """Explicit wait until the element's class has expected `value` timeout
        if not set, equals to the fixture's `wait_timeout` shortcut to
        `WebDriverWait` with customized `class_to_equal` condition."""
        return self._wait_for(
            method=class_to_equal(selector, classname),
            timeout=timeout,
            msg=f"classname => {classname} not found within {timeout or self._wait_timeout}s",
        )

    def wait_for_style_to_equal(self, selector, style, val, timeout=None):
        """Explicit wait until the element's style has expected `value` timeout
        if not set, equals to the fixture's `wait_timeout` shortcut to
        `WebDriverWait` with customized `style_to_equal` condition."""
        return self._wait_for(
            method=style_to_equal(selector, style, val),
            timeout=timeout,
            msg=f"style val => {style} {val} not found within {timeout or self._wait_timeout}s",
        )

    def wait_for_text_to_equal(self, selector, text, timeout=None):
        """Explicit wait until the element's text equals the expected `text`.

        timeout if not set, equals to the fixture's `wait_timeout`
        shortcut to `WebDriverWait` with customized `text_to_equal`
        condition.
        """
        method = text_to_equal(selector, text, timeout or self.wait_timeout)

        return self._wait_for(
            method=method,
            timeout=timeout,
            msg=method.message,
        )

    def wait_for_contains_class(self, selector, classname, timeout=None):
        """Explicit wait until the element's classes contains the expected `classname`.

        timeout if not set, equals to the fixture's `wait_timeout`
        shortcut to `WebDriverWait` with customized `contains_class`
        condition.
        """
        return self._wait_for(
            method=contains_class(selector, classname),
            timeout=timeout,
            msg=f"classname -> {classname} not found inside element within {timeout or self._wait_timeout}s",
        )

    def wait_for_contains_text(self, selector, text, timeout=None):
        """Explicit wait until the element's text contains the expected `text`.

        timeout if not set, equals to the fixture's `wait_timeout`
        shortcut to `WebDriverWait` with customized `contains_text`
        condition.
        """
        method = contains_text(selector, text, timeout or self.wait_timeout)
        return self._wait_for(
            method=method,
            timeout=timeout,
            msg=method.message,
        )

    def wait_for_page(self, url=None, timeout=10):
        """wait_for_page navigates to the url in webdriver wait until the
        renderer is loaded in browser.

        use the `server_url` if url is not provided.
        """
        self.driver.get(self.server_url if url is None else url)
        try:
            self.wait_for_element_by_css_selector(
                self.dash_entry_locator, timeout=timeout
            )
        except TimeoutException as exc:
            logger.exception("dash server is not loaded within %s seconds", timeout)
            logs = "\n".join((str(log) for log in self.get_logs()))
            logger.debug(logs)
            html = self.find_element("body").get_property("innerHTML")
            raise DashAppLoadingError(
                "the expected Dash react entry point cannot be loaded"
                f" in browser\n HTML => {html}\n Console Logs => {logs}\n"
            ) from exc

        if self._pause:
            import pdb  # pylint: disable=import-outside-toplevel

            pdb.set_trace()  # pylint: disable=forgotten-debug-statement

    def select_dcc_dropdown(self, elem_or_selector, value=None, index=None):
        dropdown = self._get_element(elem_or_selector)
        dropdown.click()

        menu = dropdown.find_element(By.CSS_SELECTOR, "div.Select-menu-outer")
        logger.debug("the available options are %s", "|".join(menu.text.split("\n")))

        options = menu.find_elements(By.CSS_SELECTOR, "div.VirtualizedSelectOption")
        if options:
            if isinstance(index, int):
                options[index].click()
                return

            for option in options:
                if option.text == value:
                    option.click()
                    return

        logger.error(
            "cannot find matching option using value=%s or index=%s", value, index
        )

    def toggle_window(self):
        """Switch between the current working window and the new opened one."""
        idx = (self._window_idx + 1) % 2
        self.switch_window(idx=idx)
        self._window_idx += 1

    def switch_window(self, idx=0):
        """Switch to window by window index shortcut to
        `driver.switch_to.window`."""
        if len(self.driver.window_handles) <= idx:
            raise BrowserError("there is no second window in Browser")

        self.driver.switch_to.window(self.driver.window_handles[idx])

    def open_new_tab(self, url=None):
        """Open a new tab in browser url is not set, equals to `server_url`."""
        self.driver.execute_script(
            f'window.open("{url or self.server_url}", "new window")'
        )

    def get_webdriver(self):
        return getattr(self, f"_get_{self._browser}")()

    def _get_wd_options(self):
        options = (
            self._options[0]
            if self._options and isinstance(self._options, list)
            else getattr(webdriver, self._browser).options.Options()
        )

        if self._headless:
            options.headless = True

        return options

    def _get_chrome(self):
        options = self._get_wd_options()

        options.set_capability("loggingPrefs", {"browser": "SEVERE"})
        options.set_capability("goog:loggingPrefs", {"browser": "SEVERE"})

        if "DASH_TEST_CHROMEPATH" in os.environ:
            options.binary_location = os.environ["DASH_TEST_CHROMEPATH"]

        options.add_experimental_option(
            "prefs",
            {
                "download.default_directory": self.download_path,
                "download.prompt_for_download": False,
                "download.directory_upgrade": True,
                "safebrowsing.enabled": False,
                "safebrowsing.disable_download_protection": True,
            },
        )
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-gpu")
        options.add_argument("--remote-debugging-port=9222")

        chrome = (
            webdriver.Remote(command_executor=self._remote_url, options=options)
            if self._remote
            else webdriver.Chrome(options=options)
        )

        # https://bugs.chromium.org/p/chromium/issues/detail?id=696481
        if self._headless:
            # pylint: disable=protected-access
            chrome.command_executor._commands["send_command"] = (
                "POST",
                "/session/$sessionId/chromium/send_command",
            )
            params = {
                "cmd": "Page.setDownloadBehavior",
                "params": {"behavior": "allow", "downloadPath": self.download_path},
            }
            res = chrome.execute("send_command", params)
            logger.debug("enabled headless download returns %s", res)

        chrome.set_window_position(0, 0)
        return chrome

    def _get_firefox(self):
        options = self._get_wd_options()

        options.set_capability("loggingPrefs", {"browser": "SEVERE"})
        options.set_capability("marionette", True)

        options.set_preference("browser.download.dir", self.download_path)
        options.set_preference("browser.download.folderList", 2)
        options.set_preference(
            "browser.helperApps.neverAsk.saveToDisk",
            "application/octet-stream",  # this MIME is generic for binary
        )
        return (
            webdriver.Remote(
                command_executor=self._remote_url,
                options=options,
            )
            if self._remote
            else webdriver.Firefox(options=options)
        )

    @staticmethod
    def _is_windows():
        return sys.platform == "win32"

    def multiple_click(self, elem_or_selector, clicks, delay=None):
        """multiple_click click the element with number of `clicks`."""
        for _ in range(clicks):
            self._get_element(elem_or_selector).click()
            if delay:
                time.sleep(delay)

    def clear_input(self, elem_or_selector):
        """Simulate key press to clear the input."""
        elem = self._get_element(elem_or_selector)
        logger.debug("clear input with %s => %s", elem_or_selector, elem)
        (
            ActionChains(self.driver)
            .move_to_element(elem)
            .pause(0.2)
            .click(elem)
            .send_keys(Keys.END)
            .key_down(Keys.SHIFT)
            .send_keys(Keys.HOME)
            .key_up(Keys.SHIFT)
            .send_keys(Keys.DELETE)
        ).perform()

    def zoom_in_graph_by_ratio(
        self, elem_or_selector, start_fraction=0.5, zoom_box_fraction=0.2, compare=True
    ):
        """Zoom out a graph with a zoom box fraction of component dimension
        default start at middle with a rectangle of 1/5 of the dimension use
        `compare` to control if we check the svg get changed."""
        elem = self._get_element(elem_or_selector)

        prev = elem.get_attribute("innerHTML")
        w, h = elem.size["width"], elem.size["height"]
        try:
            ActionChains(self.driver).move_to_element_with_offset(
                elem, w * start_fraction, h * start_fraction
            ).drag_and_drop_by_offset(
                elem, w * zoom_box_fraction, h * zoom_box_fraction
            ).perform()
        except MoveTargetOutOfBoundsException:
            logger.exception("graph offset outside of the boundary")
        if compare:
            assert prev != elem.get_attribute(
                "innerHTML"
            ), "SVG content should be different after zoom"

    def click_at_coord_fractions(self, elem_or_selector, fx, fy):
        elem = self._get_element(elem_or_selector)

        ActionChains(self.driver).move_to_element_with_offset(
            elem, elem.size["width"] * fx, elem.size["height"] * fy
        ).click().perform()

    def get_logs(self):
        """Return a list of `SEVERE` level logs after last reset time stamps
        (default to 0, resettable by `reset_log_timestamp`.

        Chrome only
        """
        if self._browser == "chrome":
            return [
                entry
                for entry in self.driver.get_log("browser")
                if entry["timestamp"] > self._last_ts
            ]
        warnings.warn("get_logs always return None with webdrivers other than Chrome")
        return None

    def reset_log_timestamp(self):
        """reset_log_timestamp only work with chrome webdriver."""
        if self._browser == "chrome":
            entries = self.driver.get_log("browser")
            if entries:
                self._last_ts = entries[-1]["timestamp"]

    @property
    def driver(self):
        """Expose the selenium webdriver as fixture property."""
        return self._driver

    @property
    def session_id(self):
        return self.driver.session_id

    @property
    def server_url(self):
        return self._url

    @server_url.setter
    def server_url(self, value):
        """Set the server url so the selenium is aware of the local server
        port.

        It also implicitly calls `wait_for_page`.
        """
        self._url = value
        self.wait_for_page()

    @property
    def download_path(self):
        return self._download_path

    @property
    def wait_timeout(self):
        return self._wait_timeout

    @wait_timeout.setter
    def wait_timeout(self, value):
        self._wait_timeout = value
        self._wd_wait = WebDriverWait(self.driver, value)
