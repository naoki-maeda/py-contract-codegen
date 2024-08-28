from enum import Enum, auto


class TargetLib(str, Enum):
    web3_v7 = "web3_v7"
    web3_v6 = "web3_v6"


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
