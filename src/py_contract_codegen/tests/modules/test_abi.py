import json
import re

import pytest

from py_contract_codegen.modules.abi import (
    ABIParser,
    ABITypeConverter,
    replace_keywords,
)
from py_contract_codegen.modules.enums import StateMutability
from py_contract_codegen.modules.exceptions import (
    InvalidABIStructureError,
    InvalidJSONError,
    UnknownABITypeError,
)


@pytest.mark.parametrize(
    "input_string, expected",
    [
        ('"true"', "True"),
        ('"false"', "False"),
        ('"null"', "None"),
    ],
)
def test_replace_keywords(input_string, expected):
    match = re.match(r'"(true|false|null)"', input_string)
    assert replace_keywords(match) == expected


@pytest.mark.parametrize(
    "abi_type,expected_python_type",
    [
        ("address", "ChecksumAddress"),
        ("bool", "bool"),
        ("uint256", "int"),
        ("int128", "int"),
        ("fixed", "float"),
        ("ufixed", "float"),
        ("bytes", "bytes"),
        ("bytes32", "bytes"),
        ("string", "str"),
        ("uint8[]", "list[int]"),
        ("address[5]", "list[ChecksumAddress]"),
        ("(uint256,address)", "tuple[int, ChecksumAddress]"),
        (
            "((uint256,bool)[],address)",
            "tuple[list[tuple[int, bool]], ChecksumAddress]",
        ),
        ("function", "bytes"),
        (
            "(address,uint256,uint256[],(uint256,uint256)[])",
            "tuple[ChecksumAddress, int, list[int], list[tuple[int, int]]]",
        ),
        ("any", "Any"),
    ],
)
def test_get_python_type(abi_type: str, expected_python_type: str):
    assert ABITypeConverter.get_python_type(abi_type) == expected_python_type


def test_get_python_type_parse_error():
    assert ABITypeConverter.get_python_type("invalid python type") == "Any"


def test_convert_type_abi_error():
    with pytest.raises(ValueError):
        ABITypeConverter._convert_type("invalid python type")


def test_abi_data_with_valid_function_abi():
    abi_json = [
        {
            "type": "function",
            "name": "balanceOf",
            "constant": True,
            "inputs": [{"name": "_account", "type": "address"}],
            "outputs": [{"name": "", "type": "uint256"}],
            "payable": False,
            "stateMutability": "view",
        }
    ]

    abi_data = ABIParser(abi=abi_json)

    assert len(abi_data.functions) == 1
    assert abi_data.functions[0]["name"] == "balanceOf"
    assert abi_data.functions[0]["stateMutability"] == StateMutability.view
    assert abi_data.functions[0]["converted_inputs"][0]["name"] == "_account"
    assert (
        abi_data.functions[0]["converted_inputs"][0]["python_type"] == "ChecksumAddress"
    )
    assert abi_data.functions[0]["converted_outputs"][0]["python_type"] == "int"


def test_abi_data_with_valid_str_function_abi():
    abi_json = json.dumps(
        [
            {
                "type": "function",
                "name": "balanceOf",
                "constant": True,
                "inputs": [{"name": "_account", "type": "address"}],
                "outputs": [{"name": "", "type": "uint256"}],
                "payable": False,
                "stateMutability": "view",
            }
        ]
    )

    abi_data = ABIParser(abi=abi_json)

    assert len(abi_data.functions) == 1
    assert abi_data.functions[0]["name"] == "balanceOf"
    assert abi_data.functions[0]["stateMutability"] == StateMutability.view
    assert abi_data.functions[0]["converted_inputs"][0]["name"] == "_account"
    assert (
        abi_data.functions[0]["converted_inputs"][0]["python_type"] == "ChecksumAddress"
    )
    assert abi_data.functions[0]["converted_outputs"][0]["python_type"] == "int"


def test_abi_data_with_invalid_json():
    invalid_json = '{"type": "function", "name": "balanceOf" "inputs": [{"name": "_account", "type": "address"}]}'

    with pytest.raises(InvalidJSONError):
        ABIParser(abi=invalid_json)


def test_abi_data_with_invalid_structure():
    invalid_structure = json.dumps({"type": "function", "name": "balanceOf"})

    with pytest.raises(InvalidABIStructureError):
        ABIParser(abi=invalid_structure)


def test_abi_data_with_unknown_abi_type():
    unknown_abi_type_json = json.dumps(
        [
            {
                "type": "unknownType",
                "name": "unknownFunction",
                "inputs": [{"name": "_account", "type": "address"}],
            }
        ]
    )

    with pytest.raises(UnknownABITypeError):
        ABIParser(abi=unknown_abi_type_json)


def test_abi_data_with_constructor():
    abi_json = json.dumps(
        [
            {
                "type": "constructor",
                "inputs": [{"name": "_account", "type": "address"}],
                "stateMutability": "nonpayable",
            }
        ]
    )

    abi_data = ABIParser(abi=abi_json)

    assert abi_data.constructor is not None
    assert abi_data.constructor["converted_inputs"][0]["name"] == "_account"
    assert (
        abi_data.constructor["converted_inputs"][0]["python_type"] == "ChecksumAddress"
    )
    assert abi_data.constructor["stateMutability"] == StateMutability.nonpayable


def test_abi_data_with_event():
    abi_json = json.dumps(
        [
            {
                "type": "event",
                "name": "Transfer",
                "inputs": [
                    {"name": "from", "type": "address", "indexed": True},
                    {"name": "to", "type": "address", "indexed": True},
                    {"name": "value", "type": "uint256", "indexed": False},
                ],
                "anonymous": False,
            }
        ]
    )

    abi_data = ABIParser(abi=abi_json)

    assert len(abi_data.events) == 1
    event = abi_data.events[0]
    assert event["name"] == "Transfer"
    assert event["converted_inputs"][0]["name"] == "from"
    assert event["converted_inputs"][0]["python_type"] == "ChecksumAddress"
    assert event["converted_inputs"][1]["name"] == "to"
    assert event["converted_inputs"][1]["python_type"] == "ChecksumAddress"
    assert event["converted_inputs"][2]["name"] == "value"
    assert event["converted_inputs"][2]["python_type"] == "int"


def test_abi_data_with_fallback():
    abi_json = json.dumps([{"type": "fallback", "stateMutability": "payable"}])

    abi_data = ABIParser(abi=abi_json)

    assert abi_data.fallback is not None
    assert abi_data.fallback["stateMutability"] == StateMutability.payable


def test_abi_data_with_receive():
    abi_json = json.dumps([{"type": "receive", "stateMutability": "payable"}])

    abi_data = ABIParser(abi=abi_json)

    assert abi_data.receive is not None
    assert abi_data.receive["stateMutability"] == StateMutability.payable


def test_abi_data_with_function_no_inputs():
    abi_json = json.dumps(
        [
            {
                "type": "function",
                "name": "totalSupply",
                "inputs": [],
                "outputs": [{"type": "uint256"}],
                "stateMutability": "view",
            }
        ]
    )

    abi_data = ABIParser(abi=abi_json)

    assert len(abi_data.functions) == 1
    assert abi_data.functions[0]["name"] == "totalSupply"
    assert abi_data.functions[0]["converted_inputs"] == []
    assert len(abi_data.functions[0]["converted_outputs"]) == 1
    assert abi_data.functions[0]["converted_outputs"][0]["python_type"] == "int"


def test_abi_data_with_function_unnamed_inputs():
    abi_json = json.dumps(
        [
            {
                "type": "function",
                "name": "transfer",
                "inputs": [{"type": "address"}, {"type": "uint256"}],
                "outputs": [{"type": "bool"}],
                "stateMutability": "nonpayable",
            }
        ]
    )

    abi_data = ABIParser(abi=abi_json)

    assert len(abi_data.functions) == 1
    assert abi_data.functions[0]["name"] == "transfer"
    assert len(abi_data.functions[0]["converted_inputs"]) == 2
    assert abi_data.functions[0]["converted_inputs"][0]["name"] == "input_1"
    assert (
        abi_data.functions[0]["converted_inputs"][0]["python_type"] == "ChecksumAddress"
    )
    assert abi_data.functions[0]["converted_inputs"][1]["name"] == "input_2"
    assert abi_data.functions[0]["converted_inputs"][1]["python_type"] == "int"


def test_abi_data_with_event_unnamed_inputs():
    abi_json = json.dumps(
        [
            {
                "type": "event",
                "name": "Transfer",
                "inputs": [
                    {"type": "address", "indexed": True},
                    {"type": "address", "indexed": True},
                    {"type": "uint256", "indexed": False},
                ],
                "anonymous": False,
            }
        ]
    )

    abi_data = ABIParser(abi=abi_json)

    assert len(abi_data.events) == 1
    event = abi_data.events[0]
    assert event["name"] == "Transfer"
    assert len(event["converted_inputs"]) == 3
    assert event["converted_inputs"][0]["name"] == "arg_1"
    assert event["converted_inputs"][0]["python_type"] == "ChecksumAddress"
    assert event["converted_inputs"][1]["name"] == "arg_2"
    assert event["converted_inputs"][1]["python_type"] == "ChecksumAddress"
    assert event["converted_inputs"][2]["name"] == "arg_3"
    assert event["converted_inputs"][2]["python_type"] == "int"


def test_abi_data_with_function_no_outputs():
    abi_json = json.dumps(
        [
            {
                "type": "function",
                "name": "burn",
                "inputs": [{"type": "uint256", "name": "amount"}],
                "outputs": [],
                "stateMutability": "nonpayable",
            }
        ]
    )

    abi_data = ABIParser(abi=abi_json)

    assert len(abi_data.functions) == 1
    assert abi_data.functions[0]["name"] == "burn"
    assert len(abi_data.functions[0]["converted_inputs"]) == 1
    assert abi_data.functions[0]["converted_inputs"][0]["name"] == "amount"
    assert abi_data.functions[0]["converted_inputs"][0]["python_type"] == "int"
    assert abi_data.functions[0]["converted_outputs"] == []


def test_abi_data_with_function_view():
    abi_json = json.dumps(
        [
            {
                "constant": True,
                "inputs": [],
                "name": "name",
                "outputs": [{"name": "", "type": "string"}],
                "payable": False,
                "stateMutability": "view",
                "type": "function",
            }
        ]
    )

    abi_data = ABIParser(abi=abi_json)

    assert len(abi_data.functions) == 1
    assert abi_data.functions[0]["name"] == "name"
    assert len(abi_data.functions[0]["converted_inputs"]) == 0
    assert len(abi_data.functions[0]["converted_outputs"]) == 1
    assert abi_data.functions[0]["converted_outputs"][0]["name"] == "output_1"
    assert abi_data.functions[0]["converted_outputs"][0]["python_type"] == "str"
    assert abi_data.functions[0]["stateMutability"] == "view"
