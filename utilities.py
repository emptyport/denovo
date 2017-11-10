# utilities.py
#
# These are various helper functions for the denovo script
#
# Michael Porter 2017
# 

from pyteomics import mgf
import numpy as np

# open_aa opens up a file containing the amino acid residue masses
# and returns a dict where the keys are the amino acid single
# letter codes and the values are the masses 
def open_aa():
    AA = {}
    with open('AA.dat', 'r') as f:
        for line in f:
            line = line.rstrip()
            if line[0] == 'I':
                continue
            AA[line.split(" ")[0]] = float(line.split(" ")[3])
    return add_mods(AA)

# add_mods takes in a dict of amino acid codes/masses and then adds
# in the mods specified in the mods file
# The format for the mods in the mods file is:
# Single letter code of the residue being modified (string)
# Mass shift of the modification (float)
# Whether it's an increase/decrease in mass (+/-)
# Whether or not it's a fixed or a variable mod (f/v)
# Example:
# M 15.9949 + v
# In this case methionine is being modified with a mass increase
# of 15.9949 Da and it is a variable modification
def add_mods(AA):
    with open('MODS.dat', 'r') as f:
        for line in f:
            line = line.rstrip()
            residue = line.split(" ")[0]
            mass_shift = float(line.split(" ")[1])
            direction = line.split(" ")[2]
            type = line.split(" ")[3]
            key = residue+'['+direction+str(mass_shift)+']'
            if direction=='+':
                AA[key] = AA[residue] + mass_shift
            else:
                AA[key] = AA[residue] - mass_shift
            if type=='f':
                del AA[residue]
    return AA

# find_nearest will find the value in array that is closest to value
def find_nearest(array, value):
    idx = (np.abs(array-value)).argmin()
    return idx

# read_mgf will read in an mgf file and return a list of the
# spectra contained within that file
def read_mgf(filename):
    spectra = mgf.read(filename)
    return spectra

# filter_noise uses statistics to remove noise from the spectrum
# the intensites are log transformed and then anything that is
# more than 1.5 times the standard deviation above the mean
# is kept as a good signal
def filter_noise(spectrum):
    mz = spectrum['m/z array']
    intensity = spectrum['intensity array']

    log_intensity = np.log10(intensity)
    mean_log_intensity = np.mean(log_intensity)
    std_log_intensity = np.std(log_intensity)
    cutoff = 2
    upper_bound = mean_log_intensity + cutoff * std_log_intensity

    filtered_mz = []
    filtered_intensity = []

    for m, i, log_i in zip(mz, intensity, log_intensity):
        if log_i > upper_bound:
            filtered_mz.append(m)
            filtered_intensity.append(i)

    return filtered_mz, filtered_intensity

# filter_paths makes sure that at least one of the mass
# differences in a path corresponds to an expected mass
# from our amino acid dict
def filter_paths(paths, mz, AA):
    filtered_paths = []
    valid_values = AA.values()
    for path in paths:
        matches = False
        for i in range(1,len(path)):
            mass_1_idx = path[i-1]
            mass_2_idx = path[i]
            mass_1 = mz[mass_1_idx]
            mass_2 = mz[mass_2_idx]
            mass_diff = mass_2 - mass_1
            closest_idx = find_nearest(valid_values, mass_diff)
            error = abs(valid_values[closest_idx] - mass_diff)
            if error < 0.5:
                matches = True
        if matches == True:
            filtered_paths.append(path)
    return filtered_paths