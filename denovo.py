import glob
import numpy as np
import utilities as util
from MassGraph import MassGraph

AA = util.open_aa()

file_list = glob.glob('./MGF/*.mgf')

count = 0
for filename in file_list:
    count += 1
    if filename != './MGF/AAPGYHMAK_vcent.mgf':
        continue
    
    spectra = util.read_mgf(filename)
    
    for spectrum in spectra:
        mz, intensity = util.filter_noise(spectrum)

        mg = MassGraph(mz=mz, minMass=56, maxMass=200, aa=AA)    
        mg.find_paths()
        
    print filename

