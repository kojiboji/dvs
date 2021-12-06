import cv2
import imutils
import numpy as np


def stitch(partitions):
    stitcher = cv2.createStitcher() if imutils.is_cv3() else cv2.Stitcher_create()
    for element in partitions:
        ret = (status, stitched) = stitcher.stitch([element[0], element[1]])
        print(status)
        yield ret


def zero_resize(a, shape):
    ret = np.zeros(shape, dtype=a.dtype)
    ret[0:a.shape[0], 0:a.shape[1], 0:a.shape[2]] = a
    return ret
