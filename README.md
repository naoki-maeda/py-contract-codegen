# py-contract-codegen

`py-contract-codegen` is a command-line tool for generating Python code from Ethereum ABI.

### Installation

```sh
pip install py-contract-codegen
```

### Commands

1. `gen`: Generate Python code from an Ethereum ABI file.
2. `version`: Show the version of the code generator.

### `gen` Command

The `gen` command is used to generate Python code from an Ethereum ABI.

```
py-contract-codegen gen [OPTIONS]
```

#### Options

```
╭─ Options ─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╮
│ --abi-path                              PATH               Path to ABI file. If not provided, `--abi-stdin` or `--contract-address` must be set [default: None]                       │
│ --abi-stdin           --no-abi-stdin                       ABI content from stdin [default: no-abi-stdin]                                                                             │
│ --contract-address                      TEXT               Auto fetch abi from etherscan and generate code. Please set environment variable `ETHERSCAN_API_KEY` [default: None]       │
│ --out-file                              PATH               Path to save file name the generated code. If not provided, prints to stdout [default: None]                               │
│ --class-name                            TEXT               Contract Class Name to save the generated code. If not provided, use `GeneratedContract` [default: GeneratedContract]      │
│ --target-lib                            [web3_v7|web3_v6]  Target library and version [default: web3_v7]                                                                              │
│ --network                               [mainnet|sepolia]  Ethereum network for fetching ABI [default: mainnet]                                                                       │
│ --help                                                     Show this message and exit.                                                                                                │
╰───────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
```

### Command Examples

#### Gen from ABI file

```sh
py-contract-codegen gen --abi-path {ABI_FILE_PATH} --out-file generated_contract.py
```

### Gen from stdin

```sh
cat {ABI_FILE_PATH} | py-contract-codegen gen --abi-stdin --out-file generated_contract.py
```

### Gen from Contract Address

It automatically generates code by fetching the ABI through [Etherscan](https://etherscan.io/) API.

The contract's source code needs to be verified on Etherscan.

Please set environment variable `ETHERSCAN_API_KEY`.

```sh
py-contract-codegen gen --contract-address {CONTRACT_ADDRESS} --out-file generated_contract.py
```

### Examples

To use the generated contract, you need to install [web3.py](https://github.com/ethereum/web3.py).

[Here's an example](https://github.com/naoki-maeda/py-contract-codegen/tree/main/src/py_contract_codegen/generated) of a generated contract:

### ERC20

```py
from web3 import Web3
from eth_account import Account

w3 = Web3(provider=Web3.HTTPProvider("{YOUR_PROVIDER_URL}"))
private_key = "{YOUR_PRIVATE_KEY}"
contract_address = w3.to_checksum_address("{YOUR_CONTRACT_ADDRESS}")
to_address = w3.to_checksum_address("{YOUR_TO_ADDRESS}")

contract = GeneratedContract(contract_address=contract_address, web3=w3)
account = Account.from_key(private_key)

# balanceOf
balance = contract.balanceOf(to_address)

# transfer
transfer = contract.transfer(to_address, 1)
nonce = w3.eth.get_transaction_count(account.address)
build_tx = transfer.build_transaction({"from": account.address, "nonce": nonce})
signed_tx = account.sign_transaction(build_tx)
tx_hash = web3.eth.send_raw_transaction(signed_tx.rawTransaction)
web3.eth.wait_for_transaction_receipt(tx_hash)
```

### License

MIT
