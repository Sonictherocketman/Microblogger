""" Tests the speed of the dateutil parser. """

import timeit

from dateutil.parser import parse
import time

date_str = 'Mon, 29 Dec 2014 16:45:00'
avg = 0.0
runs = 100000
for x in range(runs):
    b = time.time()
    dt = parse(date_str)
    e = time.time()
    avg += (e - b)
avg /= runs
print 'Runs: '+ str(runs)  + '\nAverage Time: '
print '\tSeconds: ' + str(avg)
print '\tMilliseconds: ' + str(avg * 1000)
