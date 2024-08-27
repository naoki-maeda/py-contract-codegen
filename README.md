# py-contract-codegen

`py-contract-codegen` is a command-line tool for generating Python code from Ethereum ABI.

### Installation

```sh
pip install py-contract-codegen
```


#### Commands

1. `gen`: Generate Python code from an Ethereum ABI file.
2. `version`: Show the version of the code generator.

### `gen` Command

The `gen` command is used to generate Python code from an Ethereum ABI.

```
py-contract-codegen gen [OPTIONS]
```

#### Options

- `--abi-path PATH`: Path to ABI file. If not provided, `--abi-stdin` or `--contract-address` must be set.
- `--abi-stdin/--no-abi-stdin`: ABI content from stdin (default: no-abi-stdin).
- `--contract-address TEXT`: Auto fetch ABI from Etherscan and generate code. Please set environment variable `ETHERSCAN_API_KEY`.
- `--out-file PATH`: Path to save the generated code file. If not provided, prints to stdout.
- `--class-name TEXT`: Contract Class Name for the generated code. If not provided, uses `GeneratedContract`.
- `--template-name [web3]`: Directory containing custom Jinja2 templates (default: web3).
- `--network [mainnet|sepolia]`: Ethereum network for fetching ABI (default: mainnet).
- `--help`: Show this message and exit.

### Examples

#### From ABI file

```sh
py-contract-codegen gen --abi-path {ABI_FILE_PATH} --out-file generated_contract.py
```

### From stdin

```sh
cat {ABI_FILE_PATH} | py-contract-codegen gen --abi-stdin --out-file generated_contract.py
```

### From Contract Address

It automatically generates code by fetching the ABI through [Etherscan](https://etherscan.io/) API.

Please set environment variable `ETHERSCAN_API_KEY`.

```sh
py-contract-codegen gen --contract-address {CONTRACT_ADDRESS} --out-file generated_contract.py
```

### License

MIT
