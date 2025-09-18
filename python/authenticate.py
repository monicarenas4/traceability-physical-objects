#!/usr/bin python3
import os
import random
import glob
import sys
import time
from utils.utils_ import numerical_sort
from client import authenticateIntraMe, authenticateInterMe

PORT = sys.argv[1]

if __name__ == '__main__':
    base_path = '/Users/monica.arenas/PycharmProjects/csr_pipeline/datasets/csr_images/Authentication/'
    csrs = sorted(glob.glob(os.path.join(base_path, '*/*')), key=numerical_sort)
    if not csrs:
        raise ValueError("No CSRs found.")

    t0 = time.time()
    for csr in csrs:
        csr_name = csr.split('/')[-1]
        print(f'-- {csr_name} --')

        attempts = sorted(glob.glob(csr + '/*'), key=numerical_sort)
        for att in attempts:
            random_csr = random.choice(csrs)
            while random_csr == csr:
                random_csr = random.choice(csrs)

            random_attempts = sorted(glob.glob(random_csr + '/*'), key=numerical_sort)
            random_att = random.choice(random_attempts)

            authenticateIntraMe(int(PORT), att)

            authenticateInterMe(int(PORT), att, random_att)

        print(f'\nTotal time: {(time.time() - t0) / 60}', 'minutes')
