import ast
import pandas as pd
import time
from image_processing import blob_extraction, robust_positions
from digital_signature import key_gen
from digital_signature import verifySignature
from fuzzy_extractor import generation, reproduction, secure_sketch, reconstruction
from utils.utils_ import SignedRecord, SendRecord, classP, RecordToClient, RecordToSignClient


def enrollment(csr_id: str, attempt: str, case: str, txt_enr: str, nonces: str):
    """
    :param attempt: path to read the set of images
    :param case:
    :param txt_enr: file to write the info related to the enrolled data
    :param ssk_file_enr:
    :return: omega_robust, sketch
    """
    time_proc0 = time.time()
    omegas, image_size, blob_diameter, N = blob_extraction(attempt, txt_enr)
    time_proc = time.time() - time_proc0

    time_robust0 = time.time()
    omega_robust = robust_positions(omegas, txt_enr)
    time_robust = time.time() - time_robust0

    time_sketch0 = time.time()
    sketch = secure_sketch(omega_robust, blob_diameter, N)
    time_sketch = time.time() - time_sketch0

    time_gen1 = time.time()
    P, R = generation(omega_robust, sketch)
    time_gen = time.time() - time_gen1

    theP = classP(P[0], P[1], P[2])
    P_str = str(vars(theP))

    time_Kgen1 = time.time()
    pubkey, skey = key_gen(R)
    time_Kgen = time.time() - time_Kgen1

    message = SignedRecord(csr_id, P_str, pubkey.to_string(), nonces)
    message_bytes = str(vars(message)).encode()

    time_sign1 = time.time()
    sign = skey.sign(message_bytes)  # bytes
    time_sign = time.time() - time_sign1

    send_message = SendRecord(attempt, csr_id, P_str, pubkey.to_string(), nonces, sign)
    send_message_bytes = str(vars(send_message)).encode()

    return send_message_bytes, time_proc, time_robust, time_sketch, time_gen, time_Kgen, time_sign


def authentication(csr_id: str, record: bytes, attempt: str, case: str, txt_auth: str):
    """
    :param attempt:
    :param case:
    :param txt_auth:
    :param ssk_file_enr:
    :param ssk_file_auth:
    :return:
    """
    global time_proc, time_robust, time_rep, time_Kgen, time_comp
    server_keys = []
    try:
        with open('./keys/key_server.txt') as f:
            server_keys = f.readlines()
    except FileNotFoundError:
        print('Server keys not generated.\nPlease run python/server_keys.py')
        exit()

    pk_server = bytes.fromhex(server_keys[0])

    dec_record = record.decode()

    received_record = RecordToClient(**ast.literal_eval(dec_record))
    in_csr_id = received_record.csr_id
    in_rec_P = received_record.P
    in_pk = received_record.pub_key
    in_sign = received_record.signature

    m_signed = RecordToSignClient(in_csr_id, in_rec_P, in_pk)
    m_signed_bytes = str(vars(m_signed)).encode()

    time_ver1 = time.time()
    valid_signature = verifySignature(pk_server, in_sign, m_signed_bytes)
    time_ver = time.time() - time_ver1

    if valid_signature:
        time_proc1 = time.time()
        omegas, image_size, blob_diameter, N = blob_extraction(attempt, txt_auth)
        time_proc = time.time() - time_proc1

        time_robust0 = time.time()
        omega_robust = robust_positions(omegas, txt_auth)
        time_robust = time.time() - time_robust0

        received_P = classP(**ast.literal_eval(in_rec_P))
        ske = received_P.sketch
        data = [list(map(int, (i.split(',')))) for i in ske]
        sketch = pd.DataFrame(data, columns=['x', 'y'])
        h = received_P.hash
        r = received_P.r

        time_rep, time_Kgen, time_comp = 0, 0, 0
        try:
            time_rep1 = time.time()
            omega_rec = reconstruction(omega_robust, sketch, blob_diameter)
            R = reproduction(omega_rec, sketch, h, r.encode())
            time_rep = time.time() - time_rep1

            if R == "{0:d}".format(int(0.0)):
                print('[system] ERROR: Not valid P')
                pubkey = None
            else:
                time_Kgen1 = time.time()
                pubkey, privkey = key_gen(R)
                time_Kgen = time.time() - time_Kgen1
                pubkey = pubkey.to_string()

                time_comp1 = time.time()
                if (in_pk == str(pubkey)):
                    print('[system] AUTHENTICATED')
                    time_comp = time.time() - time_comp1
                    return 1, time_ver, time_proc,  time_robust, time_rep, time_Kgen, time_comp
                else:
                    time_comp = time.time() - time_comp1
                    print('[system] ERROR: Not valid verification key')
                    return 0, time_ver, time_proc,  time_robust, time_rep, time_Kgen, time_comp
        except KeyError:

            return 0, time_ver, time_proc, time_robust, time_rep, time_Kgen, time_comp
    else:
        print('[system] The server signature is not valid.')

    return 0, time_ver, time_proc, time_robust, time_rep, time_Kgen, time_comp
