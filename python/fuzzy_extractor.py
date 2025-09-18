import hashlib
import numpy as np
import random
import pandas as pd
from utils.utils_ import blob_movement, string_blobs, find_centers


def secure_sketch(omega: pd.DataFrame, k: int, N: int) -> pd.DataFrame:
    """
    :param omega: with positioned indices
    :param k: blob's diameter
    :param N: number of grids in 1D
    :param coin: random 1 or 0
    :return: dataframe sketch
    """
    sketch = pd.DataFrame(np.zeros((len(omega), 2)).astype(str), columns=['x', 'y'])

    for i in omega.index:
        # if (omega.loc[i] != '0.0').all():
        s = blob_movement(omega["x"][i], omega["y"][i], k, N)
        sketch.loc[i] = s

    return sketch


def robust_secure_sketch(omega: pd.DataFrame, sketch: pd.DataFrame):
    """
    :param omega: dataframe
    :param sketch: dataframe
    :return: str, str
    """
    omega_str = string_blobs(omega).encode()
    sketch_str = string_blobs(sketch).encode()

    hash = "{0:d}".format(int(hashlib.sha256(omega_str + sketch_str).hexdigest(), 16))

    return hash, omega_str


def generation(omega: pd.DataFrame, sketch: pd.DataFrame):
    """
    :param omega: robust omega
    :param sketch: sketch
    :return: P tuple, secret string
    """
    r = "{0:d}".format(random.randint(0, 2 ** 256)).encode()
    hash, omega_str = robust_secure_sketch(omega, sketch)
    x = sketch.to_string(header=False,
                    index=False,
                    index_names=False).split('\n')
    sketch_ni = [','.join(ele.split()) for ele in x]
    #sketch_ni = sketch.to_string(index=False)
    P = (sketch_ni, hash, r.decode())

    R = "{0:d}".format(int(hashlib.sha256(omega_str + r).hexdigest(), 16))

    return P, R


def reconstruction(omega_prime: pd.DataFrame, sketch: pd.DataFrame, k: int):
    """
    :param omega_prime: robust omega prime
    :param sketch: sketch
    :param k: blob diameter
    :return: omega rec
    """
    v = pd.DataFrame(np.zeros((len(omega_prime), 2)).astype(int), columns=['x', 'y'])
    z = pd.DataFrame(np.zeros((len(omega_prime), 2)).astype(int), columns=['x', 'y'])
    factor = k * 1  # a = 1, a is a security parameter
    threshold = factor // 2

    for i in omega_prime.index:
        # if (omega_prime.loc[i] != '0.0').all():
        # Omega movement: v = omega_prime + s
        v.loc[i] = omega_prime.loc[i] + sketch.loc[i]
        _, center = find_centers(v.loc[i]['x'], v.loc[i]['y'], factor)
        # condition to reconstruct omega
        if ((center[0] - v.loc[i]['x']) < threshold) and ((center[1] - v.loc[i]['y']) < threshold):
            # Reconstruct omega: z = omega?
            z.loc[i] = center[0] - sketch.loc[i]['x'], center[1] - sketch.loc[i]['y']
        else:
            return '0'

    return z


# def robust_reconstruction(omega_prime: pd.DataFrame, sketch: pd.DataFrame, k: int, h: int):
def robust_reconstruction(omega_rec: pd.DataFrame, sketch: pd.DataFrame, h):
    """
    :param omega_rec:  robust omega prime
    :param sketch: sketch
    :param h: hash value
    :return:
    """
    # omega_rec = reconstruction(omega_prime, sketch, k)

    omega_rec_str = string_blobs(omega_rec).encode()
    sketch_str = string_blobs(sketch).encode()

    h_rec = "{0:d}".format(int(hashlib.sha256(omega_rec_str + sketch_str).hexdigest(), 16))

    if h == h_rec:
        return omega_rec_str
    else:
        # return '0', '0'
        return '0'


def reproduction(omega_prime: pd.DataFrame, sketch: pd.DataFrame, h, r):
    """
    :param omega_prime:  robust omega prime
    :param sketch: sketch
    :param k: blobs diameter
    :param h: hash value
    :param r: 256-bits random number
    :return:
    """
    # omega_rec, omega_rec_str = robust_reconstruction(omega_prime, sketch, k, h)
    omega_rec_str = robust_reconstruction(omega_prime, sketch, h)
    if omega_rec_str != '0':
        R = "{0:d}".format(int(hashlib.sha256(omega_rec_str + r).hexdigest(), 16))
    else:
        R = "{0:d}".format(int(0.0))

    return R
