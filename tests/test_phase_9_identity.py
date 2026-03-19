from jessica.identity.identity_contract import DEFAULT_IDENTITY
from jessica.identity.voice_stabilizer import VoiceStabilizer


def test_identity_contract_immutable():
    assert DEFAULT_IDENTITY.name == "Jessica"


def test_voice_stabilizer_prefix():
    stabilizer = VoiceStabilizer()
    output = stabilizer.stabilize("Completed the task successfully.")
    assert output.lower().startswith("i ")
