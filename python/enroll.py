import os
import glob
import sys
import time
from vendor import enrollMe
from utils.utils_ import numerical_sort

if sys.argv[1] == 'reset':
    os.system('python3 ./python/vendor.py reset')
    sys.exit(1)


def enrollment(port):
    base_path = '/Users/monica.arenas/PycharmProjects/csr_pipeline/datasets/csr_images/Enrollment/'
    csrs = sorted(glob.glob(os.path.join(base_path, '*/*')), key=numerical_sort)

    t0 = time.time()
    for csr in csrs:
        csr_name = csr.split('/')[-1]
        print(f'-- {csr_name} --')
        attempts = sorted(glob.glob(csr + '/*'), key=numerical_sort)
        for attempt in attempts:
            enrollMe(port, attempt)
            print('\n')
        print(f'\nTotal time: {(time.time() - t0) / 60}', 'minutes')

    return


if __name__ == '__main__':
    enrollment(int(sys.argv[1]))
