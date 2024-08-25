from enum import Enum, auto


class TemplateName(str, Enum):
    web3 = "web3"


class ABIType(Enum):
    function = auto()
    event = auto()
    constructor = auto()
    fallback = auto()
    receive = auto()


class StateMutability(str, Enum):
    pure = "pure"
    view = "view"
    nonpayable = "nonpayable"
    payable = "payable"


class Network(str, Enum):
    mainnet = "mainnet"
    sepolia = "sepolia"
