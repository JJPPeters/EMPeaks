
def rgb_array_to_greyscale(im):
    if im.ndim != 3 or im.shape[2] not in [3, 4]:
        raise Exception("Converting image to greyscale with unsupported dimensions")

    # luminosity weightings taken from:
    # https://stackoverflow.com/questions/12201577/how-can-i-convert-an-rgb-image-into-grayscale-in-python

    im_out = im[:, :, 0] * 0.2989 + im[:, :, 1] * 0.5870 + im[:, :, 2] * 0.1140

    im[:, :, 0] = im_out
    im[:, :, 1] = im_out
    im[:, :, 2] = im_out

    return im_out
