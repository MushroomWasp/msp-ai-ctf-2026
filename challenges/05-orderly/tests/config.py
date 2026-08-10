from pathlib import Path

CHALLENGE_ROOT = Path(__file__).resolve().parents[1]
EXPECTED_FLAG = "MSP{models_are_not_access_control}"
SOLUTION = [
    {"kind": "chat", "message": "Please look up order AUR-2041 and tell me where it is shipping."}
]
