from ecdsa.curves import NIST256p
from ecdsa.keys import SigningKey, VerifyingKey
import unittest

class TestPublicKey(unittest.TestCase):
    def __init__(self,pbk1,pbk2):
        self.pbk1 = pbk1
        self.pbk2 = pbk2

    def test_equality_public_keys(self):
        self.assertNotEqual(self.pbk1,self.pbk2)

def key_gen(R):
    # TODO: check the int(R,16)
    # mod with hash(...)/q
    secret = hash(int(R, 16))
    sk = SigningKey.from_secret_exponent(secret,curve=NIST256p)
    pk = sk.verifying_key

    return pk,sk

def verifySignature(pk,signature,m_bytes):
    pk_rec = VerifyingKey.from_string(pk, curve=NIST256p)
    valid_sign = pk_rec.verify(signature,m_bytes)
    
    return valid_sign

