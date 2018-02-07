from oct2py import octave
octave.addpath('/home/iso/PycharmProjects/git_dcstest/matVM')
octave.addpath('/home/iso/PycharmProjects/git_dcstest/matVM/matpower6.0')
octave.addpath('/home/iso/PycharmProjects/git_dcstest/matVM/matpower6.0/t')

octave.addpath('/home/iso/dcstest/matVM')
octave.addpath('/home/iso/dcstest/matVM/matpower6.0')
octave.addpath('/home/iso/dcstest/matVM/matpower6.0/t')

import numpy as np
from pprint import pprint as ppr
import sys

octave.eval("y=1")
#print(octave.eval("y"))
print(octave.pull("y"))

mpc = octave.case33bw_dcs2()
r = octave.runopf(mpc)

ppr(r["gen"])