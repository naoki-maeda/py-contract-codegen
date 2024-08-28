from pathlib import Path

import pytest
from jinja2 import TemplateNotFound
from py_contract_codegen.modules.code_generator import ContractCodeGenerator

TEMPLATE_DIR = Path(__file__).resolve().parent.parent.parent / "template"


def test_py_contract_codegen_with_valid_abi():
    abi_content = """
    [
        {
            "type": "function",
            "name": "balanceOf",
            "constant": true,
            "inputs": [{"name": "_account", "type": "address"}],
            "outputs": [{"name": "", "type": "uint256"}],
            "payable": false,
            "stateMutability": "view"
        }
    ]
    """
    generator = ContractCodeGenerator(
        abi_content=abi_content,
        template_path=TEMPLATE_DIR,
        contract_class_name="MyContract",
    )

    generated_code = generator.generate()

    assert "class MyContract" in generated_code
    assert "def balanceOf(self, _account: ChecksumAddress) -> int:" in generated_code
    assert "return self.contract.functions.balanceOf(_account).call()" in generated_code


def test_py_contract_codegen_with_invalid_template_path():
    abi_content = """
    [
        {
            "type": "function",
            "name": "balanceOf",
            "constant": true,
            "inputs": [{"name": "_account", "type": "address"}],
            "outputs": [{"name": "", "type": "uint256"}],
            "payable": false,
            "stateMutability": "view"
        }
    ]
    """
    invalid_template_path = Path("invalid/path/to/templates")

    with pytest.raises(TemplateNotFound):
        ContractCodeGenerator(
            abi_content=abi_content,
            template_path=invalid_template_path,
            contract_class_name="MyContract",
        )


def test_py_contract_codegen_with_invalid_abi():
    invalid_abi_content = "invalid json content"

    with pytest.raises(Exception):
        generator = ContractCodeGenerator(
            abi_content=invalid_abi_content,
            template_path=TEMPLATE_DIR,
            contract_class_name="MyContract",
        )
        generator.generate()


def test_py_contract_codegen_with_default_class_name():
    abi_content = """
    [
        {
            "type": "function",
            "name": "balanceOf",
            "constant": true,
            "inputs": [{"name": "_account", "type": "address"}],
            "outputs": [{"name": "", "type": "uint256"}],
            "payable": false,
            "stateMutability": "view"
        }
    ]
    """
    generator = ContractCodeGenerator(
        abi_content=abi_content, template_path=TEMPLATE_DIR
    )

    generated_code = generator.generate()

    assert "class GeneratedContract" in generated_code
    assert "return self.contract.functions.balanceOf(_account).call()" in generated_code
