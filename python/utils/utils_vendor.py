import ast
import time
from utils.utils_ import SignedCSRIDnonce
from digital_signature import verifySignature


def take_csr(received_message, n_ED):
    """
    Upon receive of the signed csr_id from the server we 
    verify if the csr_id has been signed by the server
    """
    server_keys = []
    try:
        with open('./keys/key_server.txt') as f:
            server_keys = f.readlines()
    except FileNotFoundError:
        print('Server keys not generated.\nPlease run python/server_keys.py')
        exit()

    pk_server = bytes.fromhex(server_keys[0])
    dec_received_message = received_message.decode()

    rec_received_message = SignedCSRIDnonce(**ast.literal_eval(dec_received_message))
    csr_id = rec_received_message.csr_id.decode()
    nonces = rec_received_message.nonces
    signature = rec_received_message.signature

    m_signed = csr_id + nonces
    time_ver0 = time.time()
    valid_signature = verifySignature(pk_server, signature, m_signed.encode())
    time_ver = round(time.time() - time_ver0, 4)
    if valid_signature:
        if n_ED == nonces[:len(n_ED)]:
            return csr_id, nonces, time_ver
        else:
            print(n_ED)
            print(nonces[:77])
            print('[system] The received nonce is not valid.')
    else:
        print('[system] The server signature is not valid.')

    return None
