from dataclasses import asdict, dataclass, field
from pathlib import Path

from jinja2 import Environment, FileSystemLoader

from py_contract_codegen.modules.abi import ABIParser
from py_contract_codegen.modules.enums import TargetLib

DEFAULT_CONTRACT_CLASS_NAME = "GeneratedContract"


@dataclass
class ContractCodeGenerator:
    abi_content: str
    template_path: Path
    contract_class_name: str | None = field(default=DEFAULT_CONTRACT_CLASS_NAME)
    target_lib: TargetLib = field(default=TargetLib.web3_v7)

    def __post_init__(self):
        template_loader = FileSystemLoader(self.template_path)
        self.env = Environment(loader=template_loader)
        target_lib = f"contract.{self.target_lib.value}.jinja2"
        self.template = self.env.get_template(target_lib)

    def generate(self) -> str:
        abi_data = ABIParser(abi=self.abi_content)
        context = asdict(abi_data)
        context["contract_class_name"] = self.contract_class_name
        return self.template.render(context)
