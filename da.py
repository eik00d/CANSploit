import numpy
import math
import time
import struct

from libs.da.separator import Separator

pack = numpy.vectorize(lambda i: struct.pack('!f', i) +
                                 struct.pack('!f', math.sin(i)) +
                                 struct.pack('!f', math.sqrt(i)))


def line() -> numpy.array:
    return numpy.arange(0, 1000)

series = pack(line())
sep = Separator()

start = time.clock()

for x in numpy.nditer(series):
    sep.apply(bytearray(x))

print(time.clock() - start)
print(sep.indexes())

