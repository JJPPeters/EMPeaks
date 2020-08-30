import numpy as np
cimport numpy as np

DTYPE = np.float64
ctypedef np.float64_t DTYPE_t

cdef extern from "math.h":    # this is where the real speed boost came from
    float sqrt(float x)
    float exp(float x)

cimport cython
@cython.boundscheck(False) # turn of bounds-checking for entire function
def peak_pair_c(np.ndarray[DTYPE_t, ndim=1] pos_x, np.ndarray[DTYPE_t, ndim=1] pos_y, float step_x, float step_y, float thresh):
    # accepts peak positions x, y, the basis step x, y and the threshold of the basis the point must be within (in pixels?).
    # returns two arrays with indices of peaks ine one and indices of pairs in another

    assert pos_x.dtype == DTYPE and pos_y.dtype == DTYPE

    cdef unsigned int sz = pos_x.size

    cdef np.ndarray[DTYPE_t, ndim=1] shifted_x = np.zeros(sz, dtype=DTYPE)
    cdef np.ndarray[DTYPE_t, ndim=1] shifted_y = np.zeros(sz, dtype=DTYPE)

    # apply the basis shift to the peak positions
    shifted_x = pos_x + step_x
    shifted_y = pos_y + step_y

    cdef np.ndarray[np.int_t, ndim=1] pairs_ind = np.zeros(sz, dtype=np.int)
    cdef np.ndarray[np.int_t, ndim=1] peak_ind = np.zeros(sz, dtype=np.int)
    cdef np.ndarray[DTYPE_t, ndim=1] radius = np.zeros(sz, dtype=DTYPE)

    pairs_ind.fill(-1)

    cdef float min_r
    cdef float r
    cdef unsigned int min_j
    cdef unsigned int ind

    cdef unsigned int i
    cdef unsigned int j
    cdef unsigned int counter = 0

    # loop through all the peaks
    for i in range(0, sz):

        min_r = thresh

        # loop through all the shifted peaks
        for j in range(0, sz):
            # simple check that the individual shifts are within the threshold
            if abs(pos_x[i] - shifted_x[j]) > thresh or abs(pos_y[i] - shifted_y[j]) > thresh:
                continue

            # now get the distance
            r = distance(pos_x[i], pos_y[i], shifted_x[j], shifted_y[j])
            if r < min_r:
                min_r = r
                min_j = j

        # if we are within the threshold, and not considering the same peak
        if min_r <= thresh and min_j != i:
            # we already have this peak as a pair
            if min_j in pairs_ind:
                ind = np.where(pairs_ind == min_j)[0][0] # it returns tuples and shit so need [0][0]
                # override it if this one is a better fit
                if min_r < radius[ind]:
                    radius[ind] = min_r
                    peak_ind[ind] = i
                    # pairs_ind should be the correct value already
            else:
                # add our peak, pair and radius data
                peak_ind[counter] = i
                pairs_ind[counter] = min_j
                radius[counter] = min_r
                counter += 1

    # delete unused parts of array before returning
    outPeakI = np.delete(peak_ind, np.arange(counter, sz))
    outPairsI = np.delete(pairs_ind, np.arange(counter, sz))

    return outPeakI, outPairsI


@cython.boundscheck(False) # turn of bounds-checking for entire function
def sub_peak_pair_c(np.ndarray[np.int_t, ndim=1] peakX, np.ndarray[np.int_t, ndim=1] pairX, np.ndarray[np.int_t, ndim=1] peakY, np.ndarray[np.int_t, ndim=1] pairY, int start):
    #
    # the inputs are INDICES, not the coordinates
    #
    cdef unsigned int sz = np.max((peakX.size, peakY.size))

    cdef np.ndarray[np.int_t, ndim=1] new_peaks = np.full(2*sz, -1,dtype=np.int)
    cdef np.ndarray[np.int_t, ndim=1] sub = np.full(2*sz, -1, dtype=np.int)
    cdef unsigned int new_i = 0
    cdef unsigned int start_sub_i = 0
    cdef unsigned int sub_i = 0

    # TODO: I think main slowdown now is the fact that we have to constantly search the sub array to check if the values have been added already
    # I think this could be solved by having an 'added' bool array for each peak/pair array
    # this would mean some duplicates would get added and would be neede to be deleted at the end
    # duplicates come from the fact that the indices can exist in all 4 peak/pair arrays, but each duplicate won't add any more duplicates

    sub[0] = start
    sub_i += 1
    new_peaks[0] = start
    new_i += 1

    while new_i != 0:
        start_sub_i = sub_i

        for i in range(0, new_i):#peak in newPeaks:

            # find where peak exists in our arrays
            t = np.where(peakX == new_peaks[i])[0]
            if len(t) > 0 and not np.any(sub == pairX[t[0]]):
                sub[sub_i] = pairX[t[0]]
                sub_i += 1

            t = np.where(pairX == new_peaks[i])[0]
            if len(t) > 0 and not np.any(sub == peakX[t[0]]):
                sub[sub_i] = peakX[t[0]]
                sub_i += 1

            t = np.where(peakY == new_peaks[i])[0]
            if len(t) > 0 and not np.any(sub == pairY[t[0]]):
                sub[sub_i] = pairY[t[0]]
                sub_i +=1

            t = np.where(pairY == new_peaks[i])[0]
            if len(t) > 0 and not np.any(sub == peakY[t[0]]):
                sub[sub_i] = peakY[t[0]]
                sub_i += 1

        new_peaks[:sub_i-start_sub_i] = sub[start_sub_i:sub_i]
        new_i = sub_i-start_sub_i

    return np.delete(sub, np.arange(sub_i, 2*sz))

cdef float distance(float x1, float y1, float x2, float y2):
    cdef float diffX = abs(x1-x2)
    cdef float diffY = abs(y1-y2)
    return sqrt(diffX*diffX+diffY*diffY)