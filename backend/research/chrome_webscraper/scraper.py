# TODO: We should just move it into plugin-intelligence (or even the new webscraping project).
# Remember that while web scraping can be a powerful tool,
# it's important to always respect the terms of service of the website you're scraping,
# as well as the laws and regulations applicable to your area.
# NOTE: There are some open-source Docker files for this
# https://github.com/joyzoursky/docker-python-chromedriver/blob/master/py-alpine/3.10-alpine-selenium/Dockerfile
import pprint

from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from chrome_webscraper.extract_profile import extract_profile_data, text_from_html
from common.config import POSTGRES_LOGIN_URL_FROM_ENV
from common.gpt_client import open_ai_client_with_db_cache
from supawee.client import connect_to_postgres

pp = pprint.PrettyPrinter(indent=2)

# Create a new instance of the Google Chrome driver
chrome_options = Options()
# five seconds def enough for local, might be worth to get a huge ass machine for production
CHROME_OPTIONS_DEFAULT_WAIT_TIME = 5
chrome_options.add_argument("--no-sandbox")
# For Docker (or when annoying on local)
# chrome_options.add_argument("--headless")
chrome_options.add_argument("--disable-gpu")
chrome_options.add_argument("--disable-dev-shm-usage")
chrome_options.add_argument("--window-size=1920,1080")

# Create the Chrome driver
driver = webdriver.Chrome(
    executable_path="/usr/local/bin/chromedriver",
    service_log_path="chromedriver.log",
    options=chrome_options,
)


def get_first_linkedin_search_result(google_query):
    print(f"navigating to google to search for {google_query}")
    # Go to Google's search page
    driver.get("https://www.google.com")

    # Find the search box, clear it, type in a search and submit it
    search_box = driver.find_element_by_name("q")
    search_box.clear()
    # search_box.send_keys('Peter Csiba Software Engineer LinkedIn')
    search_box.send_keys(google_query)
    search_box.submit()

    try:
        # Wait until the first search result is loaded
        wait = WebDriverWait(driver, int(CHROME_OPTIONS_DEFAULT_WAIT_TIME))
        wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "div.g a")))

        # Find the first LinkedIn link
        # Please note that automating LinkedIn is against their policy and can lead to account suspension.
        linkedin_urls = [
            result.get_attribute("href")
            for result in driver.find_elements_by_css_selector("div.g a")
            if result is not None and "linkedin.com" in result.get_attribute("href")
        ]
        print(f"found {len(linkedin_urls)} linkedin_urls: {linkedin_urls}")

        return linkedin_urls[0] if linkedin_urls else None
    except TimeoutException:
        print("Timed out waiting for page to load")
    finally:
        # Close the browser
        driver.quit()


def human_solve_security_check(xpath='//h1[text()="Let\'s do a quick security check"]'):
    # First, let's try to find the security check:
    security_check = None
    try:
        security_check = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, xpath))
        )
    except Exception:
        # If exception is raised, it means the security check is not present.
        print("no security check was found")
        pass

    # If security check is found, ask human to solve the CAPTCHA:
    if security_check:
        print("Please solve the CAPTCHA...")
        try:
            # This waits until the security check is no longer present on the page
            WebDriverWait(
                driver, 600
            ).until(  # wait up to 10 minutes for human to solve
                EC.invisibility_of_element_located(
                    (By.XPATH, '//h1[text()="Let\'s do a quick security check"]')
                )
            )
            print("CAPTCHA solved. Continuing...")
        except Exception:
            print("CAPTCHA not solved in time. Exiting...")


def scrape_linkedin_profile(profile_url):
    print(f"attempting to scrape profile {profile_url}")
    driver.get(profile_url)
    wait = WebDriverWait(driver, int(CHROME_OPTIONS_DEFAULT_WAIT_TIME))
    try:
        human_solve_security_check()

        # Different ways tried to overcome the dismiss modal.
        # Wait for the dismissal button to appear and then click it
        # dismiss_button = wait.until(
        #     EC.element_to_be_clickable((By.CSS_SELECTOR, ".modal__dismiss"))
        # )
        # dismiss_button = WebDriverWait(driver, 10).until(
        #     EC.element_to_be_clickable((By.XPATH, '//button[@aria-label="Dismiss"]'))
        # )
        # dismiss_button.click()

        # Instead of waiting for the expected dismiss button, lets just wait for page load and escape it out.
        WebDriverWait(driver, 30).until(
            lambda d: d.execute_script("return document.readyState") == "complete"
        )
        driver.find_element_by_tag_name("body").send_keys(Keys.ESCAPE)

        # Wait until the LinkedIn profile page is fully rendered
        # Here we're waiting for the presence of the element that contains the profile name
        wait.until(
            EC.presence_of_element_located((By.CSS_SELECTOR, ".top-card-layout__title"))
        )
    except TimeoutException:
        # NOT ideal, but there is a good chance most of the relevant content is there as the behavior ain't 100%.
        print("Timed out waiting for dismissal button to load")

    # Now we are on the profile page and can parse it with BeautifulSoup
    soup = BeautifulSoup(driver.page_source, "html.parser")

    # Save the content to a local file
    filename = "output.html"
    with open(filename, "w") as f:
        # profile_data = parse_profile_data(soup)
        # print(f"profile_data: {profile_data}")
        text_content = text_from_html(soup)

        content = str(soup.prettify())
        f.write(content)
        print(f"stored {len(content)}B into {filename} from url {profile_url}")

    return text_content


profile_test_urls = [
    "https://www.linkedin.com/in/mkuzmiakova/",
    "https://www.linkedin.com/in/katarina-kmetova/",
    "https://www.linkedin.com/in/jurajmasar/",
    "https://www.linkedin.com/in/henryckso/",
    "https://www.linkedin.com/in/linda-huc%C3%ADkov%C3%A1-33617889/",
    "https://www.linkedin.com/in/pvanya/",
    "https://www.linkedin.com/in/ladislav-%C3%B6ll%C5%91s/",
    "https://www.linkedin.com/in/stepan-simsa/",
    "https://www.linkedin.com/in/amendoza32/",
    "https://www.linkedin.com/in/ntucker/",
    "https://www.linkedin.com/in/peter-csiba-42445967",
]

with connect_to_postgres(POSTGRES_LOGIN_URL_FROM_ENV):
    open_ai_client = open_ai_client_with_db_cache(force_no_print_prompt=False)

    for profile_url in profile_test_urls:
        # profile_url = get_first_linkedin_search_result("Peter Csiba")
        text_content = scrape_linkedin_profile(profile_url)

        profile_data = extract_profile_data(open_ai_client, text_content)
        pp.pprint(profile_data)


driver.close()
