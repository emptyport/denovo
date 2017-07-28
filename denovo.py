import glob
import numpy as np

def find_nearest(array, value):
    idx = (np.abs(array-value)).argmin()
    return idx


def match_spectra(mz, ints, max_int, offset, seqs):
    mz = np.array(mz)
    mz = mz-offset
    b_matches = []
    y_matches = []
    for s in seqs:
        b_indices = []
        b_mz_diffs = []
        b_int_overlap = []
        y_indices = []
        y_mz_diffs = []
        y_int_overlap = []
        for b in s['b']:
            i = find_nearest(mz, b)
            b_mz_diffs.append(np.abs(b-mz[i]))
            b_int_overlap.append(ints[i]/max_int)
        for y in s['y']:
            i = find_nearest(mz, y)
            y_mz_diffs.append(np.abs(y-mz[i]))
            y_int_overlap.append(ints[i]/max_int)
        if np.median(b_mz_diffs) <= 0.5:
            b_matches.append({
                'sequence': s['sequence'],
                'diff': np.median(b_mz_diffs),
                'overlap': np.sum(b_int_overlap),
                'offset': offset
            })
        if np.median(y_mz_diffs) <= 0.5:
            y_matches.append({
                'sequence': s['sequence'],
                'diff': np.median(y_mz_diffs),
                'overlap': np.sum(y_int_overlap),
                'offset': offset
            })
    top_five_b = sorted(b_matches, key=lambda k: k['diff'])[0:5]
    top_five_y = sorted(y_matches, key=lambda k: k['diff'])[0:5]

    return top_five_b, top_five_y


AA = {}
with open('AA.dat', 'r') as f:
    for line in f:
        line = line.rstrip()
        if line[0] == 'I':
            continue
        AA[line.split(" ")[0]] = float(line.split(" ")[4])

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

SEQUENCES = []
for a in AA:
    for b in AA:
        for c in AA:
            sequence = a+b+c
            peaks = [
                AA[a],
                AA[a]+AA[b],
                AA[a]+AA[b]+AA[c]
            ]
            b_ions = np.array(peaks)+1.0
            y_ions = np.array(peaks)+19.0
            SEQUENCES.append({
                'sequence': sequence,
                'peaks': peaks,
                'b':list(b_ions),
                'y':list(y_ions)
            })
'''
SEQUENCES = []
for a in AA:
    for b in AA:
        sequence = a+b
        peaks = [
            AA[a],
            AA[a]+AA[b]
        ]
        b_ions = np.array(peaks)+1.0
        y_ions = np.array(peaks)+19.0
        SEQUENCES.append({
            'sequence': sequence,
            'peaks': peaks,
            'b':list(b_ions),
            'y':list(y_ions)
        })
'''
file_list = glob.glob('./MGF/*.mgf')

count = 0
for filename in file_list:
    count += 1
    if filename != './MGF/AAPGYHMAK_vcent.mgf':
        continue
    spectrum = {
        'charge': 0,
        'peptide_mass': 0,
        'raw_peak_list': [],
        'peak_list': [],
        'max_intensity': 0,
        'mz_arr': [],
        'int_arr': []
    }

    with open(filename, "r") as f:
        for line in f:
            line = line.rstrip()
            if 'CHARGE' in line:
                charge = line.split('=')[1]
                charge = charge.replace('+', '')
                spectrum['charge'] = int(charge)
            elif 'PEPMASS' in line:
                pepmass = line.split('=')[1]
                spectrum['peptide_mass'] = float(pepmass)
            elif 'ION' in line:
                continue
            else:
                mz = float(line.split(" ")[0])
                intensity = float(line.split(" ")[1])
                if intensity > spectrum['max_intensity']:
                    spectrum['max_intensity'] = intensity
                spectrum['raw_peak_list'].append({
                    'mz': mz,
                    'intensity': intensity
                })
    
    for item in spectrum['raw_peak_list']:
        if item['intensity']/spectrum['max_intensity'] >= 0.03:
            spectrum['peak_list'].append({
                'mz': item['mz'],
                'intensity': item['intensity']
            })
            spectrum['mz_arr'].append(item['mz'])
            spectrum['int_arr'].append(item['intensity'])
    #print spectrum['peak_list']
    #print spectrum['mz_arr']
    #print spectrum['int_arr']
    b_matches = []
    y_matches = []
    top_five_b, top_five_y = match_spectra(spectrum['mz_arr'], spectrum['int_arr'], spectrum['max_intensity'], 0, SEQUENCES)
    b_matches += top_five_b
    y_matches += top_five_y

    for mass in spectrum['mz_arr']:
        print mass
        top_five_b, top_five_y = match_spectra(spectrum['mz_arr'], spectrum['int_arr'], spectrum['max_intensity'], mass, SEQUENCES)
        b_matches += top_five_b
        y_matches += top_five_y

    outfile = open('b_data', 'w')
    for thing in b_matches:
        outfile.write(thing['sequence'])
        outfile.write(" ")
        outfile.write(str(thing['diff']))
        outfile.write(" ")
        outfile.write(str(thing['overlap']))
        outfile.write("\n")
    outfile.close

    outfile = open('y_data', 'w')
    for thing in y_matches:
        outfile.write(thing['sequence'])
        outfile.write(" ")
        outfile.write(str(thing['diff']))
        outfile.write(" ")
        outfile.write(str(thing['overlap']))
        outfile.write("\n")
    outfile.close

    print filename

