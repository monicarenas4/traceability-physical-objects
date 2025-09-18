#!/usr/bin python3
import datetime
import socket
import sys
import os
import time
from random import randint
from digital_signature import key_gen
from utils.utils_server import head_csv_db_file, create_unique_csr, addRecord, takeEntry, NONCE_SERVER

today = str(datetime.date.today()).replace('-', '')
folder_time = "results/time/"
os.makedirs(folder_time, exist_ok=True)

if len(sys.argv) != 3:
    print(f'Usage: {sys.argv[0]} <port> <DB>')
    print(f'    <DB> - \'new\', reset DB')
    print(f'    <DB> - \'add\', add to DB')
    sys.exit(1)

if __name__ == '__main__':
    # DB creation
    print("""        =========================================\n
              Artifact Authentication Server\n
        =========================================\n\n""")
    db_path = 'server_data/db_server.csv'
    av_records = 'client_data/av_rec.csv'
    check_existance = os.path.isfile(db_path)

    pk_as, sk_as = key_gen(NONCE_SERVER)

    filename = "./keys/key_server.txt"
    with open(filename, "w") as f:
        f.write(f"{pk_as.to_string().hex()}")
    print(f"Server's key generated in {filename}\n\n")

    if sys.argv[2] == 'new':
        if check_existance:
            os.remove(db_path)
        head_csv_db_file(db_path, av_records)

    elif sys.argv[2] == 'add':
        if check_existance == False:
            print('No DB found. Creating an empty DB.')
            head_csv_db_file(db_path, av_records)

    else:
        print(f'Usage: {sys.argv[0]} <host> <port> <DB>')
        print(f'    <DB> - \'new\', reset DB')
        print(f'    <DB> - \'add\', add to DB')
        sys.exit(1)
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    PORT = int(sys.argv[1])
    server_address = ('localhost', PORT)
    s.bind(server_address)
    s.listen(1)  # limit to only one client per moment

    try:
        while True:
            c, addr = s.accept()
            print('[system] -- new connection --')
            data = c.recv(4096)
            data = data.decode()

            # Vendor messages
            if data[:7] == "request":
                phase1_0 = time.time()
                n_AS = str(randint(0, 2 ** 256))
                n_ED = data[7:]
                nonces = n_ED + n_AS
                print('[system] ENROLLMENT PHASE')
                print('[system] request for new csr_id')
                csr_id_m_sign, csr_id, time_sign1 = create_unique_csr(db_path, sk_as, nonces)
                phase1_1 = time.time() - phase1_0
                c.send(csr_id_m_sign)
                print('[system] csr_id sent')
                #  received record
                record = c.recv(4096)
                phase1_02 = time.time()
                time_ver, time_check = 0, 0
                if record.decode() != 'None':
                    save, time_ver, time_check = addRecord(record, db_path, av_records, csr_id, nonces)
                    if save:
                        c.send('->[server] Successful Enrollment\n'.encode('utf-8'))
                    else:
                        c.send(
                            '->[server] !!! Server Error: DUPLICATE CSR_ID/CSR or INVALID SIGNATURE\n'.encode('utf-8'))
                else:
                    c.send('->[server] !!! Server Error: None received\n'.encode('utf-8'))

                phase1_2 = time.time() - phase1_02
                phase1_tot = time.time() - phase1_0
                with open(os.path.join(folder_time, f"{today} time_server_phase1.txt"), "a") as file:
                    file.write(str(csr_id) + '\t'
                               + str(phase1_tot) + '\t'
                               + str(phase1_1) + '\t'
                               + str(time_sign1) + '\t'
                               + str(phase1_2) + '\t'
                               + str(time_ver) + '\t'
                               + str(time_check)
                               + '\n')
            # Client messages
            else:
                phase2_0 = time.time()
                print('[system] AUTHENTICATION PHASE')
                csr_entry, time_checkDB, time_sign = takeEntry(sk_as, data, db_path)
                if csr_entry == b'0':
                    c.send('->[server] !!! Server Error: INVALID CSR or MISSING CSR_ID !!!\n'.encode('utf-8'))
                else:
                    print('[system] Sending csr entry')
                    c.send(csr_entry)
                phase2 = time.time() - phase2_0

                with open(os.path.join(folder_time, f"{today} time_server_phase2.txt"), "a") as file:
                    file.write(str(data) + '\t'
                               + str(phase2) + '\t'
                               + str(time_checkDB) + '\t'
                               + str(time_sign)
                               + '\n')

            c.close()
            print('[system] close connection\n')
    except KeyboardInterrupt:
        print("\nCaught keyboard interrupt, stopping server")
    finally:
        s.close()
