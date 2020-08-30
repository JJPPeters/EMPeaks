from enum import Enum


# 'enum' to give type of annotation
class AnnotationType(Enum):
    Image = 'Image'
    Polar = 'Polar'
    Scatter = 'Scatter'
    Basis = 'Basis'
    Drawing = 'Drawing'
    Quiver = 'Quiver'
    Line = 'Line'
    Histogram = 'Histogram'


# 'enum' to determine image display type
class ImageType(Enum):
    Scalar, Direction = range(2)

class WindowType(Enum):
    Image, Graph = range(2)

# message type for the console
class Console:
    Message, Warning, Error, Success = range(4)


# how to display complex numbers
class ComplexDisplay:
    Real, Imaginary, Amplitude, Phase, PowerSpectrum = range(5)
