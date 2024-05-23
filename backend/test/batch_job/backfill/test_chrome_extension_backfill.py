import os

import pytest

from batch_jobs.backfill.chrome_extensions.chrome_extension_list import parse_manifest_file


@pytest.fixture
def sample_manifest_path():
    # Path to the sample manifest file relative to the test file's location
    return os.path.join(os.path.dirname(__file__), 'testdata/aaaaahnmcjcoomdncaekjkjedgagpnln.json')


def test_parse_manifest_file(sample_manifest_path):
    data = parse_manifest_file(sample_manifest_path)
    expected_data = {
        'name': 'Contextual Search for YouTube',
        'version': '1.0.0.14',
        'category_slug': 'productivity/tools',
        'rating': 4.769230769230769,
        'rating_count': 13,
        'user_count': 908,
        'release_date': '2022-07-31T10:26:25.000Z',
        'size': '13.0KiB',
        'languages': ['English'],
        'description': "Allows the user search YouTube for a term by highlighting text and selecting 'Search YouTube for...' from the right click menu.",
        'publisher_account': 'Gryff',
        'update_url': 'https://clients2.google.com/service/update2/crx',
        'manifest_version': 3,
        'background': {'service_worker': 'searchyoutube.js'},
        'icons': {'16': 'SmallIcon.png', '48': 'MediumIcon.png'},
        'permissions': ['contextMenus']
    }
    assert data == expected_data


@pytest.fixture
def user_count_fancy_manifest_path():
    # Path to the sample manifest file relative to the test file's location
    return os.path.join(os.path.dirname(__file__), 'testdata/jpodanhbbpcdfgpafdjhkojjbagbcmno.json')


def test_user_count_fancy_manifest_path(user_count_fancy_manifest_path):
    data = parse_manifest_file(user_count_fancy_manifest_path)
    expected_data = {
        'slug': 'usetiful-digital-adoption',
        'name': 'Usetiful - Digital Adoption Platform',
        'description': 'Interactive product tours, smart tips and checklists for digital products.',
        'version': '1.37',
        'release_date': 'April 24, 2023',
        'publisher': 'dev',
        'category': 'Productivity',
        'category_slug': 'ext/7-productivity',
        'rating': 5.0,
        'rating_count': 10.0,
        'user_count': 4000.0,
        'publisher_site': 'https://www.usetiful.com/',
        'extension_website': 'https://www.usetiful.com/',
        'support_website': 'https://blog.usetiful.com/',
        'update_url': 'https://clients2.google.com/service/update2/crx',
        'manifest_version': 3,
        'background': {'service_worker': 'background.js'},
        'action': {'default_popup': 'popup.html', 'default_icon': 'icon-disabled.png'},
        'web_accessible_resources': [{'resources': [
            'panel.css', 'element.png', 'logo-mini.png', 'check.png', 'warning.png', 'edit.png',
            'hide.png', 'show.png', 'close.png', 'play.png', 'stop.png', 'restart.png', 'select-element.png',
            'unselect-element.png', 'navigation-mode.svg', 'manual-action.svg', 'info.svg', 'waiting-on-element.svg',
            'alert.svg', 'modal.svg', 'pointer.svg', 'slideout.svg', 'redirect.svg', 'triggerEvent.svg',
            'pageAction.svg', 'delay.svg', 'fonts/*.woff2', 'usetiful.js', 'usetiful-plugin.js', 'scripts/*.js'
        ], 'matches': ['<all_urls>']}],
        'content_scripts': [{'matches': ['http://*/*', 'https://*/*', '<all_urls>'], 'css': ['content.css'], 'run_at': 'document_start', 'js': ['content.js']}],
        'permissions': ['activeTab', 'storage'],
        'icons': {'16': 'icon16.png', '48': 'icon48.png', '128': 'icon128.png'}
    }
    assert data == expected_data


@pytest.fixture
def no_json_data_at_all_manifest_path():
    # Path to the sample manifest file relative to the test file's location
    return os.path.join(os.path.dirname(__file__), 'testdata/bhfgplecbnnaompcdbljfminapdjfbgn.json')


def test_no_json_data_at_all_manifest_path(no_json_data_at_all_manifest_path):
    data = parse_manifest_file(no_json_data_at_all_manifest_path)
    expected_data = {
        'slug': 'technikkramnet',
        'name': 'technikkram.net',
        'publisher': 'technikkram.net',
        'rating': 5.0,
        'rating_count': 1.0,
        'user_count': 4.0,
    }
    assert data == expected_data


@pytest.fixture
def json_kinda_comment_manifest_path():
    # Path to the sample manifest file relative to the test file's location
    return os.path.join(os.path.dirname(__file__), 'testdata/bhfgplecbnnaompcdbljfminapdjfbgn-comment.json')


def test_json_kinda_comment_manifest_path(json_kinda_comment_manifest_path):
    parse_manifest_file(json_kinda_comment_manifest_path)


@pytest.fixture
# This file has "---" beyond the normal YAML/JSON sections in "publisher: best-of-media---chrome-app"
def json_parsing_problem_manifest_path():
    # Path to the sample manifest file relative to the test file's location
    return os.path.join(os.path.dirname(__file__), 'testdata/mgcjmndhglkgjijpkogikbimefoiceno.json')


def test_json_parsing_problem_manifest_path(json_parsing_problem_manifest_path):
    parse_manifest_file(json_parsing_problem_manifest_path)


@pytest.fixture
def json_parsing_problem_too_many_dashes_manifest_path():
    # Path to the sample manifest file relative to the test file's location
    return os.path.join(os.path.dirname(__file__), 'testdata/efafbmknkaeomlcamfjihkonnbcmgefe.json')


def test_json_parsing_problem_too_many_dashes_manifest_path(json_parsing_problem_too_many_dashes_manifest_path):
    parse_manifest_file(json_parsing_problem_too_many_dashes_manifest_path)
