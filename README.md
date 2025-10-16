# EMPeaks

EMPeaks is a program written in python designed for interacting with an analysing transmission electron microscopy (TEM) images. It has two particular strengths:
 
 - OpenGL accelerate graphing allows for quick, easy interaction with your data (even for extremely large images)
 - Plug-in development to design and perform your own analysis (using scipy for example)

## Cython compilation

The peak pairs code is compiled in cython for speed. This can be done by navigating to the peak pairs folder and running

```
python .\setup_peak_pairs.py build_ext --inplace
```
