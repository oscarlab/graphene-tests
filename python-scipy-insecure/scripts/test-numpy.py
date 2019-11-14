#!/usr/bin/env python3

import numpy
import sys
import timeit

try:
    import numpy.core._dotblas
    print('FAST BLAS')
except ImportError:
    print('slow blas')

print("version: " + numpy.__version__)

x = numpy.random.random((1000,1000))

setup = "import numpy; x = numpy.random.random((1000,1000))"
count = 5

t = timeit.Timer("numpy.dot(x, x.T)", setup=setup)
print("dot: " + str(t.timeit(count)/count) + " sec")
