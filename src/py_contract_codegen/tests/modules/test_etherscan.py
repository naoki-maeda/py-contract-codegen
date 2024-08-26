import pytest
from unittest.mock import patch
import httpx
from py_contract_codegen.modules.enums import Network
from py_contract_codegen.modules.exceptions import EtherscanAPIError
from py_contract_codegen.modules.etherscan import get_url_by_network, get_abi


def test_get_url_by_network():
    assert get_url_by_network(Network.mainnet) == "https://api.etherscan.io/api"
    assert get_url_by_network(Network.sepolia) == "https://api-sepolia.etherscan.io/api"
    with pytest.raises(ValueError):
        get_url_by_network("invalid_network")


@pytest.mark.parametrize(
    "network, expected_url",
    [
        (Network.mainnet, "https://api.etherscan.io/api"),
        (Network.sepolia, "https://api-sepolia.etherscan.io/api"),
    ],
)
def test_get_url_by_network_parametrized(network, expected_url):
    assert get_url_by_network(network) == expected_url


@patch("httpx.get")
def test_get_abi_success(mock_get):
    mock_response = httpx.Response(
        200, json={"status": "1", "message": "OK", "result": "test_abi"}
    )
    mock_get.return_value = mock_response

    result = get_abi("0x123456789", Network.mainnet)
    assert result == "test_abi"

    expected_url = "https://api.etherscan.io/api?module=contract&action=getabi&address=0x123456789&apikey=test_api_key"
    mock_get.assert_called_once_with(expected_url)


@patch("httpx.get")
def test_get_abi_http_error(mock_get):
    mock_response = httpx.Response(400, text="Bad Request")
    mock_get.return_value = mock_response

    with pytest.raises(
        EtherscanAPIError, match="Invalid status code: 400 text: Bad Request"
    ):
        get_abi("0x123456789", Network.mainnet)


@patch("httpx.get")
def test_get_abi_api_error(mock_get):
    mock_response = httpx.Response(
        200, json={"status": "0", "message": "NOTOK", "result": "Error!"}
    )
    mock_get.return_value = mock_response

    with pytest.raises(EtherscanAPIError, match="Failed to fetch ABI from etherscan"):
        get_abi("0x123456789", Network.mainnet)
