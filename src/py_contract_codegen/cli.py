import sys
from pathlib import Path
from typing import Optional

import typer
from typing_extensions import Annotated

from py_contract_codegen.modules.code_generator import (
    DEFAULT_CONTRACT_CLASS_NAME,
    ContractCodeGenerator,
)
from py_contract_codegen.modules.enums import Network, TargetLib
from py_contract_codegen.modules.etherscan import get_abi

TEMPLATE_PATH = Path(__file__).resolve().parent / "template"

app = typer.Typer()


@app.command()
def version():
    """
    Show the version of the code generator.
    """
    typer.echo("Python Contract Code Generator v0.1.0")


@app.command()
def gen(
    abi_path: Optional[Path] = typer.Option(
        None,
        help="Path to ABI file. If not provided, `--abi-stdin` or `--contract-address` must be set",
    ),
    abi_stdin: Optional[bool] = typer.Option(False, help="ABI content from stdin"),
    contract_address: Optional[str] = typer.Option(
        None,
        help="Auto fetch abi from etherscan and generate code. Please set environment variable `ETHERSCAN_API_KEY`",
    ),
    out_file: Optional[Path] = typer.Option(
        None,
        help="Path to save file name the generated code. If not provided, prints to stdout",
    ),
    class_name: Optional[str] = typer.Option(
        DEFAULT_CONTRACT_CLASS_NAME,
        help="Contract Class Name to save the generated code. If not provided, use `GeneratedContract`",
    ),
    target_lib: Annotated[
        TargetLib, typer.Option(help="Target library and version")
    ] = TargetLib.web3_v7,
    network: Annotated[
        Network, typer.Option(help="Ethereum network for fetching ABI")
    ] = Network.mainnet,
):
    """
    Generate Python code from an Ethereum ABI file.
    """
    try:
        abi_content = None
        if abi_path:
            with open(abi_path, "r") as f:
                abi_content = f.read()
        elif abi_stdin:
            abi_content = sys.stdin.read()
        elif contract_address:
            abi_content = get_abi(contract_address, network)
        if abi_content is None:
            raise ValueError("No ABI content provided")
        generator = ContractCodeGenerator(
            abi_content=abi_content,
            template_path=TEMPLATE_PATH,
            contract_class_name=class_name,
            target_lib=target_lib,
        )
        generated_code = generator.generate()

        if out_file:
            with out_file.open("w") as f:
                f.write(generated_code)
            typer.echo(f"Generated code saved to {out_file}")
        else:
            typer.echo(generated_code)

    except Exception as e:
        typer.echo(f"An error occurred: {str(e)}", err=True)
        raise typer.Exit(code=1)
