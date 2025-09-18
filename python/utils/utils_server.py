import os
import pandas as pd
import ast
import time
import binascii
from digital_signature import verifySignature
from utils.utils_ import SignedRecord, SendRecord, SignedCSRIDnonce, RecordToClient, RecordToSignClient

NONCE_SERVER = '210644719005073877671183486889312693096397064091025351375451711930375496953659526255563761750541064217744541030831433544377227285704512570076943590210700'


def head_csv_db_file(file_name, av_records_file):
    cols = ['csr_id', 'P', 'pk', 'signature']
    df = pd.DataFrame(columns=cols)
    df.to_csv(file_name, index=False, encoding='utf-8')

    col = ['csr', 'csr_id']
    df_av = pd.DataFrame(columns=col)
    df_av.to_csv(av_records_file, index=False, encoding='utf-8')


def create_unique_csr(file_name, sk, nonces):
    csr_id = binascii.b2a_hex(os.urandom(15))
    #  "{0:x}".format(randint(0, 2 ** 256))
    csr_id_str = csr_id.decode("utf-8")
    m_to_sign = csr_id_str + nonces

    df = pd.read_csv(file_name)
    if df.empty:
        time_sign1 = time.time()
        signature = sk.sign(m_to_sign.encode())
        time_sign = time.time() - time_sign1

        record_raw = SignedCSRIDnonce(csr_id, nonces, signature)
        record_bytes = str(vars(record_raw)).encode()
        print(f'[system] generated csr_id {csr_id}')
        return record_bytes, csr_id_str, time_sign

    else:
        while csr_id_str in df.csr_id.to_list():
            csr_id = binascii.b2a_hex(os.urandom(15))
            csr_id_str = csr_id.decode("utf-8")
            m_to_sign = csr_id_str + nonces

    time_sign1 = time.time()
    signature = sk.sign(m_to_sign.encode())
    time_sign = time.time() - time_sign1

    record_raw = SignedCSRIDnonce(csr_id, nonces, signature)
    record_bytes = str(vars(record_raw)).encode()
    print(f'[system] generated csr_id {csr_id}')
    return record_bytes, csr_id_str, time_sign


def addRecord(record, file_name, av_records_file, gen_csr_id, nonces):
    """
    record: received message
    file_name: file containing the DB of the server
    output: 1/0

    This file receives the the record from the vendor, extracts the messages in the needed format,
    executes security checks and informs the server if the record is valid and saved as an entry or not.
    """

    df = pd.read_csv(file_name)
    df_client = pd.read_csv(av_records_file)
    dec_record = record.decode()
    print(repr(dec_record))

    recreate_record = SendRecord(**ast.literal_eval(dec_record))
    csr = recreate_record.csr
    csr_id = recreate_record.csr_id
    rec_P = recreate_record.P
    pk = recreate_record.pub_key
    nonces_rec = recreate_record.nonces
    sign = recreate_record.signature
    time_ver = 0
    time_check1 = time.time()

    if csr_id != gen_csr_id:
        print('[system] !!! NOT THE GENERATED CSR_ID !!!')
        time_check = time.time() - time_check1
        return 0, time_ver, time_check
    if nonces_rec != nonces:
        print('[system] !!! NOT THE CORRECT NONCES !!!')
        time_check = time.time() - time_check1
        return 0, time_ver, time_check

    time_check = time.time() - time_check1
    # extract the signed message in bytes
    signed_message = SignedRecord(csr_id, rec_P, pk, nonces_rec)
    message_bytes = str(vars(signed_message)).encode()

    time_ver1 = time.time()
    valid_sign = verifySignature(pk, sign, message_bytes)
    time_ver = time.time() - time_ver1

    if valid_sign:
        # 2: Verify uniqueness of csr_id
        csr_att = csr.split('/')[-2]
        if (pk in df.pk.to_list()):
            print('[system] !!! PK ALREADY PRESENT !!!')
            return 0, time_ver, time_check

        else:

            data = [{'csr_id': csr_id, 'P': rec_P, 'pk': pk, 'signature': sign}]
            df = pd.DataFrame(data)
            df.to_csv(file_name, mode='a', index=False, header=False, encoding='utf-8')

            add_csr_av = [{'csr': csr_att, 'csr_id': csr_id}]
            df_av = pd.DataFrame(add_csr_av)
            df_av.to_csv(av_records_file, mode='a', index=False, header=False, encoding='utf-8')

            print('[system] Record added to system')
            return 1, time_ver, time_check
    else:
        print('[system] !!! Not a valid signature !!!')
        return 0, time_ver, time_check


def takeEntry(sk, csr_id, file_name):
    df = pd.read_csv(file_name)

    if type(csr_id) != str:
        print('[system] !!! NOT A VALID CSR_ID !!!')
        return b'0'
    time_checkDB1 = time.time()
    time_sign = 0
    if csr_id in df.csr_id.to_list():
        time_checkDB = time.time() - time_checkDB1
        print('[system] Taking csr entry')
        entry = df[df.csr_id == csr_id]
        if entry.shape[0] != 1:
            print('[system] !!! There are multiple entries!!!')
            return b'0', time_checkDB, time_sign
        else:
            P = entry['P'].iloc[0]
            pk_entry = entry['pk'].iloc[0]
            # signature = entry['signature'].iloc[0]
            to_sign = RecordToSignClient(csr_id, P, pk_entry)
            to_sign_bytes = str(vars(to_sign)).encode()

            time_sign1 = time.time()
            signature = sk.sign(to_sign_bytes)
            time_sign = time.time() - time_sign1

            send_entry = RecordToClient(csr_id, P, pk_entry, signature)
            send_entry_bytes = str(vars(send_entry)).encode()

            return send_entry_bytes, time_checkDB, time_sign

    else:
        print('[system] !!! CSR_ID DOES NOT EXIST !!!')
        time_checkDB = time.time() - time_checkDB1
        return b'0', time_checkDB, time_sign
