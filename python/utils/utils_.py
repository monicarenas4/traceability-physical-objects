import cv2
import numpy as np
import pandas as pd
import random
import re
from dataclasses import dataclass

numbers = re.compile(r'(\d+)')


@dataclass
class classP():
    sketch: list
    hash: str
    r: str

    def __str__(self):
        return str(vars(self))


@dataclass
class SignedRecord():
    csr_id: bytes
    P: str
    pub_key: bytes
    nonces: str

    def __str__(self):
        return str(vars(self))


@dataclass
class RecordToSignClient():
    csr_id: bytes
    P: str
    pub_key: bytes

    def __str__(self):
        return str(vars(self))


@dataclass
class RecordToClient():
    csr_id: bytes
    P: str
    pub_key: bytes
    signature: bytes

    def __str__(self):
        return str(vars(self))


@dataclass
class SignedCSRIDnonce():
    csr_id: bytes
    nonces: str
    signature: bytes

    def __str__(self):
        return str(vars(self))


@dataclass
class SendRecord():
    csr: str
    csr_id: bytes
    P: str
    pub_key: bytes
    nonces: str
    signature: bytes

    def __str__(self):
        return str(vars(self))


def open_image(file_name):
    """
    :param file_name: path of the image
    :rtype: (image)
    """
    image = cv2.imread(file_name)
    return image


def numerical_sort(value):
    parts = numbers.split(value)
    parts[1::2] = map(int, parts[1::2])
    return parts


def string_blobs(omega: pd.DataFrame):
    """
    :param omega: dataframe
    :return: string
    """
    blobs_string = ''

    if type(omega) == pd.DataFrame:
        for row in omega.index:
            # if (omega.loc[row] != '0.0').all():
            bit_x0 = f"{int(omega['x'][row]):#0{6}x}"[2:]
            bit_y0 = f"{int(omega['y'][row]):#0{6}x}"[2:]

            blobs_string += (bit_x0 + bit_y0)
    else:
        blobs_string = '0'

    return blobs_string


def find_centers(x_omega: int, y_omega: int, factor: int):
    """
    :param x_omega: x-position
    :param y_omega: y-position
    :param factor: K * a
    :return:  x- y-center
    """
    N = 6
    x_index_start, y_index_start = (x_omega // factor), (y_omega // factor)

    index = y_index_start * N + x_index_start
    center = np.array([int((x_index_start * factor) + factor // 2), int((y_index_start * factor) + factor // 2)])

    return index, center


def blob_movement(x_omega, y_omega, k, N, a=1):
    """
    :param x_omega: x_omega
    :param y_omega: y_omega
    :param k: average blob (grid) size
    :param N: number of grids on one dimension
    :param coin: 1 or 0
    :param a: secure factor
    :return: index, sketch
    """

    coin = random.randint(0, 1)
    # factor = k * a
    factor = 4 * a
    k_center = factor // 2
    x_max: Union[int, Any] = N * factor

    if (x_omega % factor == 0) and (y_omega % factor == 0):
        x_new = ((x_omega + k_center) % x_max) if (coin == 1) else ((x_omega - k_center) % x_max)
        y_new = ((y_omega + k_center) % x_max) if (coin == 1) else ((y_omega - k_center) % x_max)
    elif (x_omega % factor == 0) and (y_omega % factor != 0):
        x_new, y_new = ((x_omega + k_center) % x_max) if (coin == 1) else (x_omega - k_center) % x_max, y_omega
    elif (x_omega % factor != 0) and (y_omega % factor == 0):
        x_new, y_new = x_omega, ((y_omega + k_center) % x_max) if (coin == 1) else ((y_omega - k_center) % x_max)
    else:
        x_new, y_new = x_omega, y_omega

    _, center = find_centers(x_new, y_new, factor)
    # sketch = center - omega
    s = np.array([center[0] - x_omega, center[1] - y_omega])

    return s


def grid_positioning(image_height: int, blob_diameter: int, blobs_detected: pd.DataFrame, a=1):
    """
    :param image_height: in pixels
    :param blob_diameter: blob's average
    :param blobs_detected: dataframe [x,y] with the detected blobs
    :param a: security value
    :return: N, grid
    """
    factor = a * blob_diameter
    # N = len(np.arange(0, image_height, factor))
    N = 128

    omega = pd.DataFrame(np.zeros((N ** 2, 2)).astype(str), columns=['x', 'y'])

    for i in blobs_detected.index:
        x, y = blobs_detected['x'][i], blobs_detected['y'][i]
        if x == image_height:
            index = ((y // factor) * N + (x // factor)) % (N * N) - N
        else:
            index = ((y // factor) * N + (x // factor)) % (N * N)

        omega.loc[index] = blobs_detected.loc[i]

    return N, omega
