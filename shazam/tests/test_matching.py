from matching import SignatureChecking
from signal_processing import SignalProcessor

def test_signature_compare():
    sig1 = ''
    sig2 = ''
    sig3 = 'diff'
    sc1 = SignatureChecking(sig1)
    sc2 = SignatureChecking(sig2)
    sc3 = SignatureChecking(sig3)
    assert sc1.compare(sig2)
    assert sc2.compare(sig1)
    assert not sc3.compare(sig1)

