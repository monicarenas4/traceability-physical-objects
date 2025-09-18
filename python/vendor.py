#!/usr/bin python3
import socket
import datetime
import sys, os
import time
from random import randint
from protocol_phases import enrollment
from utils.utils_vendor import take_csr

TODAY = str(datetime.date.today()).replace('-', '')


def enrollMe(port, csr_enroll_path):
    global attempt, time_proc, time_robust, time_sketch, time_gen, time_Kgen, time_sign, en_rec

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # s.bind(('localhost', 0))
    # port = s.getsockname()[1]
    s.connect(('localhost', port))
    data_folder_path = 'results/'
    os.makedirs(data_folder_path, exist_ok=True)
    cases = ['case1', 'case2']
    print('\n[system] -- REQUEST a csr_id --')

    n_ED = str(randint(0, 2 ** 256))

    m1 = 'request' + n_ED
    s.send(m1.encode())
    #  data: csr_id, sign(sk_as,csr_id)
    data = s.recv(4096)
    time_enroll0 = time.time()
    csr_id, nonces, time_ver = take_csr(data, n_ED)
    if csr_id != None:
        attempt = csr_enroll_path.split('/')[-2]
        print(f'[system] Signing {attempt} with id {csr_id}')
        # step 2: take images for enrollment
        for case in cases[:1]:
            txt_enr = os.path.join(data_folder_path, f"{TODAY} {case} enrollment_information.txt")
            en_rec, time_proc, time_robust, time_sketch, time_gen, time_Kgen, time_sign = enrollment(csr_id,
                                                                                                     csr_enroll_path,
                                                                                                     case, txt_enr,
                                                                                                     nonces)

        print('[system] Sending record ')
        s.send(en_rec)
        time_enroll = time.time() - time_enroll0
        rec = s.recv(4096)
        print(rec.decode())
    else:
        s.send('None'.encode('utf-8'))
        time_enroll = time.time() - time_enroll0

    folder_time = "results/time/"
    os.makedirs(folder_time, exist_ok=True)
    with open(os.path.join(folder_time, f"{TODAY} time_enroll.txt"), "a") as file:
        file.write(str(attempt) + '\t'
                   + str(time_enroll) + '\t'
                   + str(time_ver) + '\t'
                   + str(time_proc) + '\t'
                   + str(time_robust) + '\t'
                   + str(time_sketch) + '\t'
                   + str(time_gen) + '\t'
                   + str(time_Kgen) + '\t'
                   + str(time_sign)
                   + '\n')

    s.close()
    return
