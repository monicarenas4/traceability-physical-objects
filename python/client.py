#!/usr/bin python3
import os.path
import time
import datetime
from protocol_phases import authentication
from utils.utils_client import takeID
import socket

today = str(datetime.date.today()).replace('-', '')


def authenticateIntraMe(port, csr_auth_path):
    global time_ver, time_proc, time_rep, time_Kgen, time_comp

    data_folder_path = 'results/'
    csr = csr_auth_path.split('/')[-2]
    version = csr_auth_path.split('/')[-1]

    print(f'\n[system] --  AUTHENTICATION of csr {csr} attempt {version} --')
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect(('localhost', port))

    csr_id = takeID(csr)
    print('[system] requesting entry')
    s.send(csr_id)

    record = s.recv(4096)
    time_auth_intra0 = time.time()
    txt_auth_intra = os.path.join(data_folder_path, f'{today} case1 intra auth_information.txt')

    if record.decode() != 'None':
        valid_intra, time_ver, time_proc, time_robust, time_rep, time_Kgen, time_comp = authentication(csr_id, record,
                                                                                                       csr_auth_path,
                                                                                                       'case1',
                                                                                                       txt_auth_intra)
        folder_conf_matrix = "results/conf_matrix/"
        os.makedirs(folder_conf_matrix, exist_ok=True)
        with open(os.path.join(folder_conf_matrix, f'{today} intra_subject.txt'), 'a') as file:
            file.write(str(csr) + '\t'
                       + str(version) + '\t'
                       + str(1) + '\t'
                       + str(valid_intra)
                       + '\n')
    else:
        print('[system] NO RECORD')
    time_auth_intra = time.time() - time_auth_intra0

    folder_time = "results/time/"
    with open(os.path.join(folder_time, f'{today} time_auth_intra_subject.txt'), 'a') as file:
        file.write(str(csr) + '\t'
                   + str(time_auth_intra) + '\t'
                   + str(time_ver) + '\t'
                   + str(time_proc) + '\t'
                   + str(time_robust) + '\t'
                   + str(time_rep) + '\t'
                   + str(time_Kgen) + '\t'
                   + str(time_comp)
                   + '\n')
    s.close()
    return 1


def authenticateInterMe(port, csr_ref_path, csr_auth_path):
    global time_ver, time_proc, time_robust, time_rep, time_Kgen, time_comp

    data_folder_path = 'results/'
    csr_ref = csr_ref_path.split('/')[-2]
    version_ref = csr_ref_path.split('/')[-1]

    csr_auth = csr_auth_path.split('/')[-2]
    version_auth = csr_auth_path.split('/')[-1]

    print(f'\n[system] --  AUTHENTICATION of csr {csr_ref} attempt {version_ref} -- [{csr_auth},{version_auth}]')
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect(('localhost', port))

    csr_id = takeID(csr_auth)
    print('[system] requesting entry')
    s.send(csr_id)

    record = s.recv(4096)

    time_auth_inter0 = time.time()
    txt_auth_inter = os.path.join(data_folder_path, f'{today} case1 inter auth_information.txt')

    if record.decode() != 'None':
        valid_inter, time_ver, time_proc, time_robust, time_rep, time_Kgen, time_comp = authentication(csr_id, record,
                                                                                                       csr_ref_path,
                                                                                                       'case1',
                                                                                                       txt_auth_inter)
        folder_conf_matrix = "results/conf_matrix/"
        os.makedirs(folder_conf_matrix, exist_ok=True)
        with open(os.path.join(folder_conf_matrix, f'{today} inter_subject.txt'), 'a') as file:
            file.write(str(csr_ref) + '\t'
                       + str(version_ref) + '\t'
                       + str(csr_auth) + '\t'
                       + str(version_auth) + '\t'
                       + str(0) + '\t'
                       + str(valid_inter)
                       + '\n')

    else:
        print('[system] NO RECORD')

    time_auth_inter = time.time() - time_auth_inter0
    folder_time = "results/time/"
    with open(os.path.join(folder_time, f'{today} time_auth_inter_subject.txt'), 'a') as file:
        file.write(str(csr_ref) + '\t'
                   + str(time_auth_inter) + '\t'
                   + str(time_ver) + '\t'
                   + str(time_proc) + '\t'
                   + str(time_robust) + '\t'
                   + str(time_rep) + '\t'
                   + str(time_Kgen) + '\t'
                   + str(time_comp)
                   + '\n')
    s.close()
    return 1
