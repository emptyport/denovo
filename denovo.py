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
        pep_mass = spectrum['params']['pepmass']
        max_length = int(pep_mass[0] / 111.1254) + 5
        mg = MassGraph(mz=mz, minMass=56, maxMass=200, aa=AA, maxLen=max_length)
        #print mg.graph 
        paths = []
        for i in range(0, len(mz)-1):
            for j in range(1, len(mz)):
                p = mg.get_all_paths(i,j)
                paths.extend(p)
        print len(paths)
        #filtered_paths = util.filter_paths(paths, mz, AA)
        #print len(filtered_paths)
        #print len(filtered_paths)/len(paths)
    print filename

