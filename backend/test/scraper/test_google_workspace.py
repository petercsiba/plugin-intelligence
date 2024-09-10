import datetime
import os

from bs4 import BeautifulSoup

from batch_jobs.scraper.google_workspace import _parse_add_on_page_response, ReviewData
from supabase.models.data import GoogleWorkspace


# Utility function to load data from a specific file
def load_data_from(testdata_file: str):
    file_path = os.path.join(os.path.dirname(__file__) + "/testdata/", testdata_file)
    with open(file_path, "r") as file:
        return file.read()


def test_calamari_bug_learn_more_path():
    html_content = load_data_from("Calamari.html")

    soup = BeautifulSoup(html_content, "html.parser")
    add_on = GoogleWorkspace()

    _parse_add_on_page_response(add_on, soup, save_large_fields=True)

    assert add_on.description.startswith("Modern leave")
    assert add_on.developer_name == "Calamari.io"
    # Alternatively: https://support.google.com/a?p=marketplace-messages&hl=en
    assert add_on.developer_link == "https://www.calamari.io/terms-of-use"
    assert (
        add_on.featured_img_link
        == "https://lh3.googleusercontent.com/-pJaZMFzwk9g/ZC57WpfBGiI/AAAAAAAAAB0/nA2wLtxx-vIw24Y8nle1AHZfpowUgl60wCNcBGAsYHQ/w1280-h800/Ewidencja.png"
    )  # noqa
    assert add_on.listing_updated == datetime.date(2023, 4, 6)
    assert (
        add_on.logo_link
        == "https://lh5.googleusercontent.com/-oLWY9PD6b5w/U_MVhYVsSCI/AAAAAAAAADQ/a33ioS_UCVY/s0/calamari_128x128_kolor.png"
    )  # noqa
    assert add_on.overview.startswith(
        "Calamari helps businesses and organizations boost"
    )
    assert add_on.permissions == [
        "See, edit, share, and permanently delete all the calendars you can access using Google Calendar",
        "See info about users on your domain",
        "See your primary Google Account email address",
        "See your personal info, including any personal info you've made publicly available",
    ]
    assert add_on.pricing == "Free of charge trial"
    assert add_on.rating == "5"
    assert add_on.rating_count == 10.0
    assert add_on.user_count == 103000
    assert add_on.reviews == []
    assert not add_on.with_calendar
    assert not add_on.with_chat
    assert not add_on.with_classroom
    assert not add_on.with_docs
    assert not add_on.with_drive
    assert not add_on.with_forms
    assert not add_on.with_gmail
    assert not add_on.with_meet
    assert not add_on.with_sheets
    assert not add_on.with_slides


def test_broad_bug_developer_name_open_in_new():
    html_content = load_data_from("google_workspace-keyword_mapping.html")

    soup = BeautifulSoup(html_content, "html.parser")
    add_on = GoogleWorkspace()

    _parse_add_on_page_response(add_on, soup, save_large_fields=True)

    assert add_on.description.startswith(
        "With your keywords and this Keyword Mapping addon,"
    )
    assert add_on.developer_name == "Onpageseo.tools"
    assert add_on.developer_link == "https://www.onpageseo.tools/terms-of-service/"
    assert (
        add_on.featured_img_link
        == "https://lh3.googleusercontent.com/-g99Jt_QCUOo/XwL3EA9cPkI/AAAAAAAAAAk/QIaT4VGsbFYuxjmfJTlUsbBMnmhOPSRqACLcBGAsYHQ/w1280-h800/Screenshots1.png"
    )  # noqa
    assert add_on.listing_updated is None
    assert (
        add_on.logo_link
        == "https://lh3.googleusercontent.com/-e_Rf66SdWMs/XwL27piGHLI/AAAAAAAAAAU/464BleTD12ImTeg5Rr6cGIjkQ-JKnvc7ACLcBGAsYHQ/s400/keyword-mapping.png"
    )  # noqa
    assert add_on.overview.startswith("With your keywords and this Keyword Mapping ")
    assert add_on.permissions == [
        "View and manage spreadsheets that this application has been installed in",
        "Display and run third-party web content in prompts and sidebars inside Google applications",
        "Connect to an external service",
        "See your primary Google Account email address",
        "See your personal info, including any personal info you've made publicly available",
    ]
    assert add_on.pricing == "Not available"
    assert add_on.rating == "3.13"
    assert add_on.rating_count == 8
    assert add_on.user_count == 3000
    assert add_on.reviews == [
        ReviewData(
            name="Online Business For The AI Generation",
            stars=5,
            content="It doesn't work...",
            date_posted="November 8, 2022",
        ),
        ReviewData(
            name="Shweta Parmar",
            stars=5,
            content="I am happy that this add-on is helping so many writers.",
            date_posted="March 24, 2021",
        ),
        ReviewData(
            name="airbiip",
            stars=5,
            content="This poop doesn't work, Good for wasting valuable time though.",
            date_posted="November 19, 2020",
        ),
        ReviewData(
            name="Samson Assefa",
            stars=5,
            content="Samson Assefa Gebrehiwot",
            date_posted="December 10, 2020",
        ),
    ]
    assert not add_on.with_calendar
    assert not add_on.with_chat
    assert not add_on.with_classroom
    assert not add_on.with_docs
    assert not add_on.with_drive
    assert not add_on.with_forms
    assert not add_on.with_gmail
    assert not add_on.with_meet
    assert add_on.with_sheets
    assert not add_on.with_slides
