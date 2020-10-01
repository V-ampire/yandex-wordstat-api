from faker import Faker
import pytest
from requests.exceptions import HTTPError
from wordstat import Wordstat


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


def test_fail_process_response(requests_mock):
    expected_params = {
        'method': 'test-method'
    }
    requests_mock.post(api.API_URL, status_code=404)
    with pytest.raises(HTTPError):
        api._process_request(expected_params)


def test_process_response_error():
    pass


def test_process_response_unexpected_response():
    pass


def test_process_response_success():
    pass
