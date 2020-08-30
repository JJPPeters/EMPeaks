import os
import re
import numpy as np
from scipy import interpolate


def load_colour_maps(path):
    maps = std_colour_maps.copy()
    maps.update(load_user_colour_maps(path))
    return maps


def load_user_colour_maps(path):
    # interpret .txt file to build colour maps (so user can set them)
    # RULES OF THE TEXT FILE
    # each line contains 1 colourmap (should be changed tbh)
    # must start with the name of the colourmap
    # then OPTIONAL sub menu text (must start with a-z or A-Z)
    # hash (#) can be used to comment out a line
    # then a series of  number that go in order of:
    # position, float, 0.0 to 1.0 - the position of the colour
    # R G B A, int, 0 to 255 - the colour at the set position
    # these 'position R G B A' entries are separated by spaces and/or commas
    # values must contain a 0.0 and 1.0 position (though the order will be worked out)

    map_path = path + os.sep + "ColourMaps" + os.sep + "ColourMaps.txt"

    if not os.path.isfile(map_path):
        return {}

    map_dict = {}

    map_file = open(map_path, "r")
    # could use something like ^(?!#) at the start to find comments, instead I just check the start of the line
    # and compare it to the '#' character (using lstrip)
    regex = re.compile(r'\s*([\w.]+)(?:\s+([a-zA-Z][\w\.]*))?((?:[ ,\t\n\r\f\v]+[\d*\.\d+|\d]+)*)')
    regex_rgba = re.compile(r'\s+(\d*\.\d+|\d+)\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+)')

    for line in map_file:
        if len(line) <= 0 or line.lstrip() == '' or line.lstrip()[0] == "#":  # is this line a comment?
            continue

        try:
            phrase = regex.findall(line)[0]
        except IndexError:
            continue
        try:
            rgb = regex_rgba.findall(phrase[2])
            if len(rgb) < 2:
                continue
        except IndexError:
            continue

        key = phrase[0]
        menu = phrase[1]
        values = []

        valid = True

        for i in rgb:
            try:
                p = float(i[0])
                r = int(i[1])
                g = int(i[2])
                b = int(i[3])
                a = int(i[4])
            except ValueError:
                valid = False
            values.append([p, [r, g, b, a]])

        sorted_values = sorted(values, key=lambda x: x[0])

        if not sorted_values[0][0] == 0.0 or not sorted_values[-1][0] == 1.0:
            valid = False

        if valid:
            map_dict[key] = (menu, sorted_values)

    return map_dict

std_colour_maps = {'Gray': ("", [[0.0, [0, 0, 0, 255]],
                                 [1.0, [255, 255, 255, 255]]]),
                   'Viridis': ("", [[0.0, [68, 0, 84, 255]],
                                    [0.125, [71, 45, 123, 255]],
                                    [0.25, [58, 82, 139, 255]],
                                    [0.375, [44, 114, 142, 255]],
                                    [0.5, [32, 144, 140, 255]],
                                    [0.625, [40, 174, 128, 255]],
                                    [0.75, [94, 201, 97, 255]],
                                    [0.875, [173, 220, 48, 255]],
                                    [1.0, [253, 231, 36, 255]]]),
                   'Magma': ("", [[0.0, [0, 0, 3, 255]],
                                  [0.125, [28, 16, 70, 255]],
                                  [0.25, [80, 18, 123, 255]],
                                  [0.375, [130, 37, 129, 255]],
                                  [0.5, [182, 54, 121, 255]],
                                  [0.625, [230, 81, 98, 255]],
                                  [0.75, [251, 136, 97, 255]],
                                  [0.875, [254, 196, 136, 255]],
                                  [1.0, [251, 252, 191, 255]]]),
                   'Hot': ("", [[0.0, [10, 0, 0, 255]],
                                [0.375, [255, 0, 0, 255]],
                                [0.75, [255, 255, 0, 255]],
                                [1.0, [255, 255, 255, 255]]]),
                   'Bone': ("", [[0.0, [0, 0, 0, 255]],
                                 [0.375, [81, 81, 113, 255]],
                                 [0.75, [166, 198, 198, 255]],
                                 [1.0, [255, 255, 255, 255]]]),
                   # I fucking hate jet
                   # 'Jet': ("", [[0.0, [0, 0, 143, 255]],
                   #           [0.125, [0, 0, 255, 255]],
                   #           [0.375, [0, 255, 255, 255]],
                   #           [0.625, [255, 255, 0, 255]],
                   #           [0.875, [255, 0, 0, 255]],
                   #           [1.0, [128, 0, 0, 255]]]),
                   'Cool': ("", [[0.0, [0, 255, 255, 255]],
                                 [1.0, [255, 0, 255, 255]]]),
                   'BrBG11': ("Divergent", [[0.0, [84, 48, 5, 255]],
                                            [0.125, [155, 92, 15, 255]],
                                            [0.3, [219, 186, 113, 255]],
                                            [0.5, [245, 245, 245, 255]],
                                            [0.7, [117, 199, 187, 255]],
                                            [0.875, [7, 114, 107, 255]],
                                            [1.0, [0, 60, 48, 255]]]),
                   'BuOr10': ("Divergent", [[0.0, [7, 90, 254, 255]],
                                            [0.5, [235, 255, 235, 255]],
                                            [1.0, [255, 85, 0, 255]]]),
                   'PRG11': ("Divergent", [[0.0, [64, 0, 75, 255]],
                                           [0.125, [122, 48, 136, 255]],
                                           [0.5, [247, 247, 247, 255]],
                                           [0.875, [40, 135, 65, 255]],
                                           [1.0, [0, 68, 27, 255]]]),
                   'RBGY360': ("Directional", [[0.0, [255, 0, 0, 255]],
                                               [0.25, [0, 0, 255, 255]],
                                               [0.5, [0, 255, 0, 255]],
                                               [0.75, [255, 255, 0, 255]],
                                               [1.0, [255, 0, 0, 255]]]),
                   'OGCP360': ("Directional", [[0.0, [0, 140, 255, 255]],
                                               [0.25, [65, 194, 0, 255]],
                                               [0.5, [255, 115, 0, 255]],
                                               [0.75, [129, 0, 194, 255]],
                                               [1.0, [0, 140, 255, 255]]]),
                   'RBGY4': ("Directional", [[0.0, [255, 0, 0, 255]],
                                             [0.12, [255, 0, 0, 255]],
                                             [0.13, [0, 0, 255, 255]],
                                             [0.37, [0, 0, 255, 255]],
                                             [0.38, [0, 255, 0, 255]],
                                             [0.62, [0, 255, 0, 255]],
                                             [0.63, [255, 255, 0, 255]],
                                             [0.87, [255, 255, 0, 255]],
                                             [0.88, [255, 0, 0, 255]],
                                             [1.0, [255, 0, 0, 255]]]),
                   'OGCP4': ("Directional", [[0.0, [0, 140, 255, 255]],
                                             [0.12, [0, 140, 255, 255]],
                                             [0.13, [65, 194, 0, 255]],
                                             [0.37, [65, 194, 0, 255]],
                                             [0.38, [255, 115, 0, 255]],
                                             [0.62, [255, 115, 0, 255]],
                                             [0.63, [129, 0, 194, 255]],
                                             [0.87, [129, 0, 194, 255]],
                                             [0.88, [0, 140, 255, 255]],
                                             [1.0, [0, 140, 255, 255]]]),
                   'RPBY360': ("Directional", [[0.0, [231, 74, 33, 255]],
                                               [0.05, [231, 74, 33, 255]],
                                               [0.2, [79, 37, 119, 255]],
                                               [0.3, [79, 37, 119, 255]],
                                               [0.45, [0, 146, 169, 255]],
                                               [0.55, [0, 146, 169, 255]],
                                               [0.7, [243, 229, 0, 255]],
                                               [0.8, [243, 229, 0, 255]],
                                               [0.95, [231, 74, 33, 255]],
                                               [1.0, [231, 74, 33, 255]]]),
                   'Jet like': ("Divergent", [[0.0, [127, 0, 255, 255]],
                                              [0.1, [76, 79, 251, 255]],
                                              [0.2, [25, 150, 242, 255]],
                                              [0.325, [24, 205, 227, 255]],
                                              [0.45, [76, 242, 206, 255]],
                                              [0.5, [127, 254, 179, 255]],
                                              [0.55, [178, 242, 149, 255]],
                                              [0.675, [230, 205, 115, 255]],
                                              [0.8, [255, 150, 78, 255]],
                                              [0.9, [255, 79, 40, 255]],
                                              [1.0, [231, 0, 0, 255]]]),
                   'ReYeBl': ("Divergent", [[0.0, [158, 1, 66, 255]],
                                            [0.1, [213, 62, 79, 255]],
                                            [0.2, [244, 109, 67, 255]],
                                            [0.3, [253, 174, 97, 255]],
                                            [0.4, [254, 224, 139, 255]],
                                            [0.5, [255, 255, 191, 255]],
                                            [0.6, [230, 245, 152, 255]],
                                            [0.7, [171, 221, 164, 255]],
                                            [0.8, [102, 194, 165, 255]],
                                            [0.9, [50, 136, 189, 255]],
                                            [1.0, [94, 79, 162, 255]]]),
                   'NASA': ("", [[0.0, [200, 90, 130, 255]],
                                 [0.29, [255, 220, 255, 255]],
                                 [0.49, [90, 30, 80, 255]],
                                 [0.59, [145, 40, 25, 255]],
                                 [0.63, [220, 70, 10, 255]],
                                 [0.70, [180, 180, 15, 255]],
                                 [0.80, [30, 130, 130, 255]],
                                 [0.95, [35, 35, 35, 255]],
                                 [1.00, [0, 0, 0, 255]]]),
                   'Swamp': ("", [[0.00, [0, 0, 0, 255]],
                                  [0.2, [35, 35, 35, 255]],
                                  [0.5, [30, 130, 130, 255]],
                                  [1.00, [180, 180, 15, 255]]]),
                   }
