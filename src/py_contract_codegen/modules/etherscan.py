import os

import httpx
from py_contract_codegen.modules.enums import Network
from py_contract_codegen.modules.exceptions import EtherscanAPIError

ETHERSCAN_BASE_URL = "https://api.etherscan.io/api"

def get_url_by_network(network: Network) -> str:
    match network:
        case Network.mainnet:
            return "https://api.etherscan.io/api"
        case Network.sepolia:
            return "https://api-sepolia.etherscan.io/api"
        case _:
            raise ValueError("Invalid Etherscan network")


def get_abi(contract_address: str, network: Network = Network.mainnet) -> str:
    """
    Get ABI from etherscan API ABI file.
    """
    base_url = get_url_by_network(network)
    url = f"{base_url}?module=contract&action=getabi&address={contract_address}&apikey={network.value}"
    etherscan_api_key = os.getenv("ETHERSCAN_API_KEY")
    assert (
        etherscan_api_key is not None
    ), "`ETHERSCAN_API_KEY` environment variable is not set"
    url = f"{ETHERSCAN_BASE_URL}?module=contract&action=getabi&address={contract_address}&apikey={etherscan_api_key}"
    response = httpx.get(url)
    if response.status_code != 200:
        raise EtherscanAPIError(
            f"Invalid status code: {response.status_code} text: {response.text}"
        )
    response_json = response.json()
    if response_json.get("status") != "1" or response_json.get("message") != "OK":
        raise EtherscanAPIError(
            f"Failed to fetch ABI from etherscan response: {response.text}"
        )
    return response.json()["result"]
