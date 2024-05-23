import datetime
import os

import pytest
from bs4 import BeautifulSoup

from batch_jobs.scraper.google_workspace import _parse_add_on_page_response
from supabase.models.data import GoogleWorkspace


@pytest.fixture
def calamari_bug_learn_more_path():
    # Path to the sample manifest file relative to the test file's location
    return os.path.join(os.path.dirname(__file__), 'testdata/Calamari.html')


def test_calamari_bug_learn_more_path(calamari_bug_learn_more_path):
    with open(calamari_bug_learn_more_path, 'r') as f:
        html_content = f.read()

    soup = BeautifulSoup(html_content, 'html.parser')
    add_on = GoogleWorkspace()

    _parse_add_on_page_response(add_on, soup, save_large_fields=True)

    assert add_on.description.startswith("Modern leave")
    assert add_on.developer_name == "Calamari.io"
    # Alternatively: https://support.google.com/a?p=marketplace-messages&hl=en
    assert add_on.developer_link == "https://www.calamari.io/terms-of-use"
    assert add_on.featured_img_link == "https://lh3.googleusercontent.com/-pJaZMFzwk9g/ZC57WpfBGiI/AAAAAAAAAB0/nA2wLtxx-vIw24Y8nle1AHZfpowUgl60wCNcBGAsYHQ/w1280-h800/Ewidencja.png"  #noqa
    assert add_on.listing_updated == datetime.date(2023, 4, 6)
    assert add_on.logo_link == "https://lh5.googleusercontent.com/-oLWY9PD6b5w/U_MVhYVsSCI/AAAAAAAAADQ/a33ioS_UCVY/s0/calamari_128x128_kolor.png"  #noqa
    assert add_on.overview.startswith("Calamari helps businesses and organizations boost")
    assert add_on.permissions == ['See, edit, share, and permanently delete all the calendars you can access using Google Calendar', 'See info about users on your domain', 'See your primary Google Account email address', "See your personal info, including any personal info you've made publicly available"]
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


