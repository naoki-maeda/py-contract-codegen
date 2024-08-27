import json
from unittest.mock import patch

import pytest
from typer.testing import CliRunner

from py_contract_codegen.cli import app
from py_contract_codegen.modules.enums import Network

runner = CliRunner()


def test_version():
    result = runner.invoke(app, ["version"])
    assert result.exit_code == 0
    assert "Python Contract Code Generator" in result.stdout


@pytest.fixture
def sample_abi():
    return json.dumps(
        [
            {
                "type": "function",
                "name": "transfer",
                "inputs": [
                    {"name": "to", "type": "address"},
                    {"name": "value", "type": "uint256"},
                ],
                "outputs": [{"name": "", "type": "bool"}],
            }
        ]
    )


def test_gen_with_abi_file(tmp_path, sample_abi):
    abi_file = tmp_path / "sample.abi"
    abi_file.write_text(sample_abi)

    result = runner.invoke(app, ["gen", "--abi-path", str(abi_file)])
    assert result.exit_code == 0
    assert "def transfer" in result.stdout


def test_gen_with_abi_stdin(sample_abi):
    result = runner.invoke(app, ["gen", "--abi-stdin"], input=sample_abi)
    assert result.exit_code == 0
    assert "def transfer" in result.stdout


@patch("py_contract_codegen.cli.get_abi")
def test_gen_with_contract_address(mock_get_abi, sample_abi):
    mock_get_abi.return_value = sample_abi

    result = runner.invoke(app, ["gen", "--contract-address", "0x123456789"])
    assert result.exit_code == 0
    assert "def transfer" in result.stdout


@patch("py_contract_codegen.cli.get_abi")
def test_gen_with_network(mock_get_abi, sample_abi):
    mock_get_abi.return_value = sample_abi

    result = runner.invoke(
        app, ["gen", "--contract-address", "0x123456789", "--network", Network.sepolia]
    )
    assert result.exit_code == 0
    assert "def transfer" in result.stdout


def test_gen_with_out_file(tmp_path, sample_abi):
    abi_file = tmp_path / "sample.abi"
    abi_file.write_text(sample_abi)
    out_file = tmp_path / "output.py"

    result = runner.invoke(
        app, ["gen", "--abi-path", str(abi_file), "--out-file", str(out_file)]
    )
    assert result.exit_code == 0
    assert "Generated code saved to" in result.stdout
    assert out_file.exists()


def test_gen_with_class_name(tmp_path, sample_abi):
    abi_file = tmp_path / "sample.abi"
    abi_file.write_text(sample_abi)

    result = runner.invoke(
        app, ["gen", "--abi-path", str(abi_file), "--class-name", "CustomContract"]
    )
    assert result.exit_code == 0
    assert "class CustomContract" in result.stdout


def test_gen_with_no_abi():
    result = runner.invoke(app, ["gen"])
    assert result.exit_code == 1
    assert "No ABI content provided" in result.stdout


@patch("py_contract_codegen.cli.ContractCodeGenerator")
def test_gen_with_exception(mock_generator):
    mock_generator.side_effect = Exception("Test exception")

    result = runner.invoke(app, ["gen", "--abi-stdin"])
    assert result.exit_code == 1
    assert "An error occurred: Test exception" in result.stdout
