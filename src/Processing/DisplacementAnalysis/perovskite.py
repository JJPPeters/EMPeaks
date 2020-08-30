import numpy as np
from scipy import interpolate

from Processing.Utilities import distance_2d, point_in_poly, get_nearest_neighbours, cartesian_to_polar


def ABO_ca_ratio(Adata, Bdata, ysz, xsz):
    Asz = Adata.shape[0]  # Number of A sites
    Bsz = Bdata.shape[0]  # Number of B sites

    # grid will later be mades to use size? same size as image?
    yy, xx = np.mgrid[0:1:ysz*1j, 0:1:xsz*1j]
    xx *= xsz
    yy *= ysz
    ca_ratio = np.zeros((Bsz,), dtype=np.float32)  # to store the displacements

    a_ratio = np.zeros((Bsz,), dtype=np.float32)  # not ratios
    c_ratio = np.zeros((Bsz,), dtype=np.float32)

    centre = np.zeros(Bdata.shape, dtype=np.float32)

    neighbours = 4
    nearest_n = get_nearest_neighbours(Bdata, Adata, neighbours)[0]

    for i, nn in enumerate(nearest_n):

        inside = point_in_poly(Bdata[i], nn)

        if inside:
            NN_y = np.sort(nn[:, 0])
            NN_x = np.sort(nn[:, 1])
            a_110 = (NN_x[2] + NN_x[3]) / 2 - (NN_x[0] + NN_x[1]) / 2
            c = (NN_y[2] + NN_y[3])/2 - (NN_y[0] + NN_y[1])/2

            # TODO: make this programmatic
            a = a_110  # np.sqrt(np.square(2*a_110)/2)

            centre[i, 0] = np.sum(NN_x)/4 + np.random.random()
            centre[i, 1] = np.sum(NN_y)/4 + np.random.random()

            a_ratio[i] = a
            c_ratio[i] = c
            ca_ratio[i] = c/a  # np.random.random() #
        else:
            centre[i, :] = Bdata[i, :]
            ca_ratio[i] = 1
            a_ratio[i] = 1
            c_ratio[i] = 1

    # np.savetxt("D:/test_a.csv", np.hstack((centre, a_ratio.reshape((a_ratio.size, 1)))), delimiter=', ')
    # np.savetxt("D:/test_c.csv", np.hstack((centre, c_ratio.reshape((c_ratio.size, 1)))), delimiter=', ')
    # np.savetxt("D:/test_ca.csv", np.hstack((centre, ca_ratio.reshape((ca_ratio.size, 1)))), delimiter=', ')

    ratio_im = interpolate.griddata(centre, ca_ratio, (xx, yy), method='nearest')
    # magim = interpolate.griddata(centre, mag, (xx, yy), method='cubic', fill_value=0)
    # angim = interpolate.griddata(centre, ang, (xx, yy), method='cubic', fill_value=0)

    return ratio_im


def abo_displacement(reference_pos, displaced_data, neighbours, limit=None, polar=False, average=None):
    # nearest_n has 3 axes, first is the different B atoms,
    # second is the A atoms and the third contains the x and y data
    nearest_n = get_nearest_neighbours(displaced_data, reference_pos, neighbours)[0]

    centre = np.mean(nearest_n, axis=1)
    disp = displaced_data - centre

    # remove entries outside our limit (these usually don't have a full unit cell to reference)
    if limit is not None:
        valid = np.where(np.hypot(disp[:,0], disp[:,1]) < limit)[0]
        disp = disp[valid, :]
        centre = centre[valid, :]

        # modify this data for averaging (if needed)
        if average is not None and average > 1:
            displaced_data = displaced_data[valid, :]

    if average is not None and average > 1:
        # do averaging here
        # first need to find the nearest neighbours (indices of these)
        nearest_inds = get_nearest_neighbours(displaced_data, displaced_data, average)[1]
        disp = np.mean(disp[nearest_inds, :], axis=1)

    if polar:
        return centre, cartesian_to_polar(disp[:, 0], disp[:, 1])
    else:
        return centre, (disp[:, 0], disp[:, 1])


def abo_displacement_field(reference_pos, displaced_data, xsz, ysz, neighbours, direction,
                           method='nearest', limit=None, average=None):
    # here is where the displacements are calculated
    # polar as always False as the discontinuity between 0 and 360 causes the interpolation to fuck up
    centre, disp = abo_displacement(reference_pos, displaced_data, neighbours,
                                    limit=limit, polar=False, average=average)

    # grid will later be made to use size? same size as image?
    xx, yy = np.mgrid[0:1:xsz*1j, 0:1:ysz*1j]
    xx *= xsz
    yy *= ysz

    mag_image = None
    ang_image = None

    if direction == 'Horizontal':
        mag_image = interpolate.griddata(centre, disp[1], (xx, yy), method=method, fill_value=0)
    elif direction == 'Vertical':
        mag_image = interpolate.griddata(centre, disp[0], (xx, yy), method=method, fill_value=0)
    elif direction == '360°':

        y_image = interpolate.griddata(centre, disp[0], (xx, yy), method=method, fill_value=0)
        x_image = interpolate.griddata(centre, disp[1], (xx, yy), method=method, fill_value=0)

        mag_image, ang_image = cartesian_to_polar(y_image, x_image)

    return mag_image, ang_image
