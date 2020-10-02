from faker import Faker
import pytest
from requests.exceptions import HTTPError
from wordstat.api import Wordstat, WordstatAPIError


ACCESS_TOKEN = 'test-token'

fake = Faker()

api = Wordstat(ACCESS_TOKEN)


def test_success_process_request(requests_mock):
    expected_data = fake.pydict(value_types=[str])
    expected_params = {
        'method': 'test-method'
    }
    requests_mock.post(api.API_URL, json=expected_data)
    result = api._process_request(expected_params)
    assert result == expected_data
    assert requests_mock.request_history[0].json()['locale'] == 'ru'
    assert requests_mock.request_history[0].json()['token'] == ACCESS_TOKEN
    assert requests_mock.request_history[0].json()['method'] == expected_params['method']


def test_fail_process_request(requests_mock):
    expected_params = {
        'method': 'test-method'
    }
    requests_mock.post(api.API_URL, status_code=404)
    with pytest.raises(HTTPError):
        api._process_request(expected_params)


def test_process_response_error():
    error_response = {
        "error_detail":"Метод HTTP запроса должен быть POST",
        "error_str":"Неверный метод запроса",
        "error_code":512
    }
    with pytest.raises(WordstatAPIError) as excinfo:
        api._process_response(error_response)
    assert str(error_response) in str(excinfo.value)


def test_process_response_unexpected_response():
    invalid_response = {
        'invalid_key': 'invalid_data'
    }
    with pytest.raises(WordstatAPIError):
        api._process_response(invalid_response)


def test_process_response_success():
    response = {
        'data': 1
    }
    assert api._process_response(response) == response['data']


def test_create_report_success(requests_mock):
    expected_phrases = fake.pylist(value_types=[str])
    expected_geo_ids = fake.pylist(value_types=[int])
    expected_report_id = 1
    expected_response = {
        'data': expected_report_id
    }
    requests_mock.post(api.API_URL, json=expected_response)
    result = api.create_report(expected_phrases, expected_geo_ids)
    request_data = requests_mock.request_history[0].json()
    assert result == expected_report_id
    assert request_data['method'] == 'CreateNewWordstatReport'
    assert request_data['param'] == {
        "Phrases": expected_phrases,
        "GeoID": expected_geo_ids,
    }


