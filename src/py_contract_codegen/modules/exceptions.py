class ABIParserError(Exception):
    """Base exception for ABI parser errors."""


class InvalidJSONError(ABIParserError):
    """Raised when the ABI content is not valid JSON."""


class InvalidABIStructureError(ABIParserError):
    """Raised when the ABI structure is invalid."""


class UnknownABITypeError(ABIParserError):
    """Raised when an unknown ABI type is encountered."""


class EtherscanAPIError(Exception):
    """Raised when the etherscan API errors."""
