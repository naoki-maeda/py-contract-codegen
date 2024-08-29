import json
import re
from dataclasses import dataclass, field
from keyword import kwlist
from typing import Any, TypedDict

from eth_abi.exceptions import ParseError
from eth_abi.grammar import BasicType, TupleType, normalize, parse
from eth_typing import (
    ABIConstructor,
    ABIError,
    ABIEvent,
    ABIFallback,
    ABIFunction,
    ABIReceive,
)

from py_contract_codegen.modules.enums import ABIType
from py_contract_codegen.modules.exceptions import (
    InvalidABIStructureError,
    InvalidJSONError,
    UnknownABITypeError,
)

REPLACE_PATTERN = re.compile(r"\b(true|false|null)\b")


def replace_keywords(match):
    keyword = match.group(1)
    if keyword == "true":
        return "True"
    elif keyword == "false":
        return "False"
    else:  # null
        return "None"


def format_abi_for_python(abi: list[dict[str, Any]]):
    """
    format ABI to python dict for template
    """
    abi_json = json.dumps(abi, indent=4)
    abi_python = REPLACE_PATTERN.sub(replace_keywords, abi_json)
    return abi_python


class ABITypeConverter:
    """
    EVM ABI types to Python types converter.
    ref: https://docs.soliditylang.org/en/latest/abi-spec.html
    """

    @classmethod
    def get_python_type(cls, abi_type: str) -> str:
        try:
            normalized_type = parse(normalize(abi_type))
            return cls._convert_type(normalized_type)
        except ParseError:
            return "Any"

    @classmethod
    def _convert_type(cls, abi_type: ABIType) -> str:
        if isinstance(abi_type, BasicType):
            return cls._convert_basic_type(abi_type)
        elif isinstance(abi_type, TupleType):
            return cls._convert_tuple_type(abi_type)
        else:
            raise UnknownABITypeError(f"Unknown ABI type: {abi_type}")

    @classmethod
    def _convert_basic_type(cls, basic_type: BasicType) -> str:
        basic_type_str = basic_type.to_type_str()

        match basic_type_str:
            case s if s.endswith("]"):
                array_start = s.index("[")
                element_type_str = s[:array_start]
                element_type = parse(element_type_str)
                python_element_type = cls._convert_type(element_type)
                return f"list[{python_element_type}]"
            case s if s.startswith(("uint", "int")):
                return "int"
            case "address":
                return "ChecksumAddress"
            case "bool":
                return "bool"
            case "string":
                return "str"
            case "bytes24":
                return "bytes"  # `function` type is represented as `bytes`
            case s if s.startswith("bytes"):
                return "bytes"
            case s if s.startswith(("fixed", "ufixed")):
                return "float"
            case _:
                return "Any"

    @classmethod
    def _convert_tuple_type(cls, tuple_type: TupleType) -> str:
        tuple_type_str = tuple_type.to_type_str()

        if tuple_type_str.endswith("[]"):
            element_tuple_type = parse(tuple_type_str[:-2])
            python_element_type = cls._convert_type(element_tuple_type)
            return f"list[{python_element_type}]"

        inner_types = [cls._convert_type(t) for t in tuple_type.components]
        return f"tuple[{', '.join(inner_types)}]"


class ABITypeConvertedComponent(TypedDict):
    name: str
    type: str
    indexed: bool
    python_type: str


class ABITypedFunction(ABIFunction):
    converted_inputs: list[ABITypeConvertedComponent]
    converted_outputs: list[ABITypeConvertedComponent]


class ABITypedEvent(ABIEvent):
    converted_inputs: list[ABITypeConvertedComponent]


class ABITypedConstructor(ABIConstructor):
    converted_inputs: list[ABITypeConvertedComponent]


@dataclass
class ABIParser:
    abi: str
    content: list[dict[str, Any]] = field(default_factory=list)
    formatted_content: str = ""
    functions: list[ABITypedFunction] = field(default_factory=list)
    events: list[ABITypedEvent] = field(default_factory=list)
    constructors: list[ABITypedConstructor] = field(default_factory=list)
    fallbacks: list[ABIFallback] = field(default_factory=list)
    receives: list[ABIReceive] = field(default_factory=list)
    errors: list[ABIError] = field(default_factory=list)

    def __post_init__(self):
        self.validate()
        self.parse()

    def validate(self) -> None:
        if isinstance(self.abi, list):
            self.content = self.abi
        elif isinstance(self.abi, str):
            try:
                self.content = json.loads(self.abi)
            except json.JSONDecodeError as e:
                raise InvalidJSONError(f"Invalid JSON in content: {e}")
        for item in self.content:
            if not isinstance(item, dict):
                raise InvalidABIStructureError("Each ABI item must be a dictionary")
            try:
                ABIType[item["type"]]
            except KeyError:
                raise UnknownABITypeError(f"Unknown ABI type: {item['type']}")
        self.formatted_content = format_abi_for_python(self.content)

    def parse(self) -> None:
        for item in self.content:
            abi_type = ABIType[item["type"]]

            match abi_type:
                case ABIType.function:
                    self.functions.append(self._parse_function(item))
                case ABIType.event:
                    self.events.append(self._parse_event(item))
                case ABIType.constructor:
                    self.constructors.append(self._parse_constructor(item))
                case ABIType.fallback:
                    self.fallbacks.append(self._parse_fallback(item))
                case ABIType.receive:
                    self.receives.append(self._parse_receive(item))
                case ABIType.error:
                    self.errors.append(self._parse_error(item))

    def _parse_params(
        self, params: list[dict[str, Any]], prefix: str = "arg"
    ) -> list[ABITypeConvertedComponent]:
        if not params:
            return []
        converted_params = []
        for i, param in enumerate(params, start=1):
            name = param.get("name")
            # check Python Reserved Keywords
            name = f"{name}_" if name in kwlist else name
            if not name:
                name = f"{prefix}_{i}"
            # NOTE: type `address` is CheckSumAddress for input, but it becomes str for output.
            if param["type"] == "address" and prefix == "output":
                converted_abi_component = ABITypeConvertedComponent(
                    name=name,
                    type=param["type"],
                    indexed=param.get("indexed", False),
                    python_type="str",
                )
            else:
                converted_abi_component = ABITypeConvertedComponent(
                    name=name,
                    type=param["type"],
                    indexed=param.get("indexed", False),
                    python_type=ABITypeConverter.get_python_type(param["type"]),
                )
            converted_params.append(converted_abi_component)
        return converted_params

    def _parse_function(self, func: dict[str, Any]) -> ABITypedFunction:
        return ABITypedFunction(
            name=func["name"],
            type=func["type"],
            inputs=func.get("inputs", []),
            outputs=func.get("outputs", []),
            converted_inputs=self._parse_params(func.get("inputs", []), "input"),
            converted_outputs=self._parse_params(func.get("outputs", []), "output"),
            stateMutability=func.get("stateMutability", "nonpayable"),
        )

    def _parse_event(self, event: dict[str, Any]) -> ABITypedEvent:
        return ABITypedEvent(
            name=event["name"],
            type=event["type"],
            inputs=event.get("inputs", []),
            converted_inputs=self._parse_params(event.get("inputs", []), "arg"),
            anonymous=event.get("anonymous", False),
        )

    def _parse_constructor(self, constructor: dict[str, Any]) -> ABITypedConstructor:
        return ABITypedConstructor(
            type=constructor["type"],
            inputs=constructor.get("inputs", []),
            converted_inputs=self._parse_params(constructor.get("inputs", [])),
            stateMutability=constructor.get("stateMutability", "nonpayable"),
        )

    def _parse_fallback(self, fallback: dict[str, Any]) -> ABIFallback:
        return ABIFallback(
            type=fallback["type"],
            stateMutability=fallback.get("stateMutability", "nonpayable"),
        )

    def _parse_receive(self, receive: dict[str, Any]) -> ABIReceive:
        return ABIReceive(
            type=receive["type"],
            stateMutability=receive.get("stateMutability", "payable"),
        )

    def _parse_error(self, error: dict[str, Any]) -> ABIError:
        return ABIError(
            type=error["type"],
            name=error["name"],
            inputs=error.get("inputs", []),
        )
