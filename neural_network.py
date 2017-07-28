import glob
import re
import numpy as np

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
    check_data = []
    check_target = []
    print 'Reading data...'
    file_list = glob.glob('./data/*.msp')
    for f in file_list:
        if count > 1:
            continue
        count += 1
        learn_data = []
        target = []
        
        #if f != './data/2012_04_20_human_qtof_consensus_final_true_lib.tar.gz-human_qtof_consensus_final_true_lib.msp':
            #continue
        print 'Processing',f,'...'
        fi = fileIterator(f)
        processed = 0
        for thing in fi:
            processed += 1
            clean_seq = re.sub(r'\([A-Za-z]{1,}\)', '', thing['name'])
            clean_seq = clean_seq.split("/")[0]
            mods = getMods(thing['comment'])
            for i in range(0, len(thing['peak_list'])):
                peak = thing['peak_list'][i]
                peak_class = peak[2].split("/")[0]
                if "-" in peak_class or "^" in peak_class or "i" in peak_class or "?" in peak_class:
                    continue
                peak_type = peak_class[0]
                peak_position = peak_class[1:]
                print peak_type,peak_position


            

if __name__ == '__main__':
    main()