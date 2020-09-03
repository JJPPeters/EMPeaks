import io
import numpy as np


def ExportQuiver(file_path: str, positions, magnitudes, angles):
    out_data = np.column_stack((np.fliplr(positions), magnitudes, angles))
    np.savetxt(file_path, out_data, delimiter=",", header="x,y,magnitude,angle")
