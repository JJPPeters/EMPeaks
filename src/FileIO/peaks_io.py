import io
import numpy as np


def ImportPeaks(file_path):
    # this is so that the delimiter can be ", " or just ","
    # csv doesnt have the space, but older versions of my program saved with one
    s = io.BytesIO(open(file_path, 'rb').read().replace(b', ', b','))
    peaks = np.loadtxt(s, delimiter=",")
    peaks = np.fliplr(peaks)
    return peaks

def ExportPeaks(file_path, peaks):
    np.savetxt(file_path, np.fliplr(peaks), delimiter=",", header="x,y")
