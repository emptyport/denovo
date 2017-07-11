import glob
import re
import numpy as np
from sklearn.linear_model import PassiveAggressiveClassifier

def getMods(comment):
    elems = comment.split(" ")
    raw_mods = ""
    for thing in elems:
        if thing.startswith("Mods="):
            raw_mods = thing.split("=")[1]
            next
    mod_list = raw_mods.split("/")
    mods = []
    for i in range(1, len(mod_list)):
        info = mod_list[i].split(",")
        position = info[0]
        mod = info[2]
        mods.append( [position, mod] )
    return mods

def processPeakList(peak_list):
    good_peak_list = []
    for peak in peak_list:
        elems = peak.split("\t")
        mz = elems[0]
        intensity = elems[1]
        label = elems[2].replace("\"","")
        ion_info = label.split(" ")[0]

        for ion in ion_info.split(","):
            if not ion.startswith("y") and not ion.startswith("b") and not ion.startswith("a"):
                good_peak_list.append([ float(mz), float(intensity), "?" ])
            else:
                good_peak_list.append([ float(mz), float(intensity), ion.split("/")[0] ])

    return good_peak_list

def fileIterator(filename):
    name = ""
    mw = 0.0
    comment = ""
    num_peaks = 0
    peak_list = []
    with open(filename, "r") as f:
        for line in f:
            line = line.rstrip()
            if len(line) == 0:
                vals = {'name':name,
                        'mw':mw,
                        'comment':comment,
                        'num_peaks':num_peaks,
                        'peak_list':processPeakList(peak_list)
                        }
                name = ""
                mw = 0.0
                comment = ""
                num_peaks = 0
                peak_list = []
                yield vals
            elif "Name: " in line:
                name = line.split(" ")[1]
            elif "MW: " in line:
                mw = float(line.split(" ")[1])
            elif "Comment: " in line:
                comment = line.replace("Comment: ", "")
            elif "Num peaks: " in line:
                num_peaks = int(line.split(" ")[2])
            else:
                peak_list.append(line)


def main():
    count = 0
    clf = PassiveAggressiveClassifier(n_jobs=4)
    print 'Reading data...'
    file_list = glob.glob('./data/*.msp')
    for f in file_list:
        if count > 5:
            continue
        count += 1
        learn_data = []
        target = []
        classes = []
        #if f != './data/2012_04_20_human_qtof_consensus_final_true_lib.tar.gz-human_qtof_consensus_final_true_lib.msp':
            #continue
        print 'Processing',f,'...'
        fi = fileIterator(f)
        for thing in fi:
            clean_seq = re.sub(r'\([A-Za-z]{1,}\)', '', thing['name'])
            clean_seq = clean_seq.split("/")[0]
            mods = getMods(thing['comment'])
            for i in range(0, len(thing['peak_list'])):
                peak = thing['peak_list'][i]
                peak_def = peak[2].split("^")[0]
                try:
                    peak_loss = peak_def.split("-")[1]
                except IndexError:
                    peak_loss = "0"
                try:
                    peak_gain = peak_def.split("+")[1]
                except IndexError:
                    peak_gain = "0"
                peak_type = peak_def.split("-")[0]
                peak_type = peak_type.split("+")[0]
                peak_type = peak_type.replace("i", "").replace("*", "")
                if peak_type.startswith("y"):
                    index = len(clean_seq) - int(peak_type[1:])
                elif peak_type != "?":
                    index = int(peak_type[1:]) - 1
                else:
                    index = -1
                if peak_type != "?":
                    label = clean_seq[index]
                else:
                    label = "?"
                for m in mods:
                    if int(m[0]) == index:
                        label += "("+m[1]+")"
                before_values = []
                after_values = []
                for j in range(i, i-10):
                    if j<0:
                        mass_diff = 0
                        intensity = 0
                    else:
                        mass_diff = thing['peak_list'][j][0] - peak[0]
                        intensity = thing['peak_list'][j][1] / 10000
                    before_values.append(mass_diff)
                    before_values.append(intensity)
                
                for j in range(i, i+10):
                    if j>=len(thing['peak_list']):
                        mass_diff = 0
                        intensity = 0
                    else:
                        mass_diff = thing['peak_list'][j][0] - peak[0]
                        intensity = thing['peak_list'][j][1] / 10000
                    after_values.append(mass_diff)
                    after_values.append(intensity)
                
                input = [peak[1]/10000] + before_values + after_values
                learn_data.append(input)
                target.append(label)
                classes.append(label)

        classes = list(set(classes))
        print 'Classifying...'
        clf.partial_fit(learn_data, target, classes)
        print 'Score:',clf.score(learn_data, target)

if __name__ == '__main__':
    main()