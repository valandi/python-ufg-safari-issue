import os
import pytest

from webdriver_manager.chrome import ChromeDriverManager
from selenium import webdriver
from applitools.selenium import (
    VisualGridRunner,
    Eyes,
    Target,
    BatchInfo,
    BrowserType,
    DeviceName,
)
from applitools.common import StdoutLogger, logger



@pytest.fixture(scope="module")
def batch_info():
    """
    Use one BatchInfo for all tests inside module
    """
    return BatchInfo("safari 16 reproducer")


@pytest.fixture(name="driver", scope="function")
def driver_setup():
    """
    New browser instance per test and quite.
    """
    # Set chrome driver to headless when running on the CI
    options = webdriver.ChromeOptions()
    options.headless = (os.getenv('CI', 'False') == 'true')

    driver = webdriver.Chrome(ChromeDriverManager().install(), options=options)
    yield driver
    # Close the browser.
    driver.quit()


@pytest.fixture(name="runner", scope="session")
def runner_setup():
    """
    One test runner for all tests. Print test results in the end of execution.
    """
    runner = VisualGridRunner()
    yield runner
    all_test_results = runner.get_all_test_results()
    print(all_test_results)


@pytest.fixture(name="eyes", scope="function")
def eyes_setup(runner, batch_info):
    """
    Basic Eyes setup. It'll abort test if wasn't closed properly.
    """
    eyes = Eyes(runner)
    # Initialize the eyes SDK and set your private API key.
    eyes.api_key = os.environ["APPLITOOLS_API_KEY"]
    eyes.configure.batch = batch_info

    # Add browsers with different viewports
    # Add mobile emulation devices in Portrait mode
    (
        eyes.configure.add_browser(800, 600, BrowserType.CHROME)
            .add_browser(700, 500, BrowserType.FIREFOX)
            .add_browser(1920, 1080, BrowserType.SAFARI_ONE_VERSION_BACK)
            .add_browser(1920, 1080, BrowserType.SAFARI)
    )
    logger.set_logger(StdoutLogger())
    yield eyes
    # If the test was aborted before eyes.close was called, ends the test as aborted.
    eyes.abort_if_not_closed()


def test_ultra_fast(eyes, driver):
    # Navigate to the url we want to test
    driver.get("https://ir.tesla.com/#quarterly-disclosure")

    # Call Open on eyes to initialize a test session
    eyes.open(driver, "Tesla investor relations", "Tesla investor relations")

    # check the login page with fluent api, see more info here
    # https://applitools.com/docs/topics/sdk/the-eyes-sdk-check-fluent-api.html
    eyes.check("", Target.window().fully().with_name("Investor Relations"))

    # Call Close on eyes to let the server know it should display the results
    eyes.close(False)
