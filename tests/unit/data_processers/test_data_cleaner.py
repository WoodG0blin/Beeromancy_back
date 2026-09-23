import pytest

from beeromancy_back.data_processers import (
    get_clean_characteristic,
    get_clean_name,
    get_clean_string,
)


@pytest.mark.parametrize("input_string, expected_output", [
    ("  Hello World!  ", "hello world!"),
    ("This is a test string.", "this is a test string."),
    ("   Multiple   spaces   ", "multiple spaces"),
    ("String with\xa0non-breaking space", "string with non-breaking space"),
    ("String with\u200bzero-width space", "string withzero-width space"),
    ("String with\ufeffbyte order mark", "string withbyte order mark"),
    ("String with control characters\x01\x02\x03", "string with control characters"),
])
def test_get_clean_string(input_string, expected_output):
    assert get_clean_string(input_string) == expected_output


@pytest.mark.parametrize("raw_name, expected_output", [
    ("product name", "product name|0|г"), #testing no split case
    ("product name, 500 г", "product name|500|г"), #testing base case
    ("product name, 1.5 кг", "product name|1.5|кг"), #testing decimal weight
    ("product name, Extra Info, 500 г", "product name|500|г"), #testing extra info case
    ("product name, 500 г,", "product name|500|г"), #testing excess comma case
    ("product name,,, 500 г,", "product name|500|г"), #testing excess comma case
    ("product name (with details), 500 г", "product name|500|г"), #testing parentheses removal
    ("Солод product name, 500 г", "product name|500|г"), #testing removal of 'Солод'
    ("Дрожжи product name, 500 г", "product name|500|г"), #testing removal of 'Дрожжи'
    ("Хмель product name, 500 г", "product name|500|г"), #testing removal of 'Хмель'
    ("", "|0|г"), #testing empty string case
])
def test_get_clear_name(raw_name, expected_output):
    assert get_clean_name(raw_name) == expected_output


@pytest.mark.parametrize("raw, expected", [
    ("2,5-4", "2.5-4.0"),
    ("300.21", "300.2"),
    ("70", "70.0"),
    ("2,2 -2,6", "2.2-2.6"),
    ("2% -3.5 %", "2.0-3.5 %"),
    ("2ebc", "2.0 ebc"),
    ("","")
])
def test_clear_characteristics(raw, expected):
    assert get_clean_characteristic(raw) == expected
