import os
import numpy as np
import tifffile as tif
import imageio

from .dm3_lib import DM3

import h5py


def ImportImage(file_path):
    file_extension = os.path.splitext(file_path)[1]
    if file_extension == '.h5':
        image = import_hdf5(file_path)
    elif file_extension == '.tif':
        image = ImportTIF(file_path)
    elif file_extension in ['.dm3', '.dm4']:
        image = ImportDM(file_path)
    elif file_extension == '.npy':
        image = ImportNumpy(file_path)
    else:
        raise Exception('Could not open file with unknown type: {}'.format(file_path))

    return image


def import_hdf5(file_path):
    with h5py.File(file_path, 'r') as hf:
        if 'program' not in hf.attrs.keys() or hf.attrs['program'] != 'pypeaks':
            raise Warning("Not a valid PyPeaks hdf5 file")

        output = walk_hdf5(hf)

    return output


def walk_hdf5(hf):
    dic = {}

    for key, val in hf.items():
        if isinstance(val, h5py.Group):
            dic[key] = walk_hdf5(val)
        elif isinstance(val, h5py.Dataset):
            dic[key] = np.array(val)

        for k, v in val.attrs.items():
            dic[key][k] = v

    return dic


def ImportDM(file_path):
    dmf = DM3(file_path)
    output = {'images': {'Image': {'magnitude': dmf.image}}}
    return output

def ImportTIF(file_path):
    tf = tif.imread(file_path)
    output = {'images': {'Image': {'magnitude': tf}}}
    return output


def ImportNumpy(file_path):
    npy = np.load(file_path)
    output = {'images': {'Image': {'magnitude': npy}}}
    return output


def ExportImage(file_path, image):
    file_extension = os.path.splitext(file_path)[1]
    if file_extension == '.tif':
        ExportTIF(file_path, image)
    elif file_extension == '.npy':
        return ExportNumpy(file_path, image)
    else:
        raise Exception('Could not parse file with unknown type: {}'.format(file_path))

def ExportTIF(file_path, image):
    tif.imsave(file_path, image.astype(np.float32))


def ExportNumpy(file_path, image):
    np.save(file_path, image)


def ExportRGB(file_path, image, colour_map=None):
    if colour_map is None:
        imageio.imsave(file_path, image)

    # normalise data to 0-255
    image_byte = image.astype(np.float32) - np.min(image)
    image_byte = 255 * image_byte / np.max(image_byte)
    image_byte = image_byte.astype(np.int)

    # colour map should be 256 length already
    colour_image = colour_map[image_byte, :3]

    imageio.imsave(file_path, colour_image)
