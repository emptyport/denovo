import os
import ftplib
import collections
import tarfile
from copy import copy
import progressbar
import urllib

def traverse(ftp, depth=0):
    """
    return a recursive listing of an ftp server contents (starting
    from the current directory)

    listing is returned as a recursive dictionary, where each key
    contains a contents of the subdirectory or None if it corresponds
    to a file.

    @param ftp: ftplib.FTP object
    """
    if depth > 10:
        return ['depth > 10']
    level = {}
    for entry in (path for path in ftp.nlst() if path not in ('.', '..')):
        try:
            ftp.cwd(entry)
            level[entry] = traverse(ftp, depth+1)
            ftp.cwd('..')
        except ftplib.error_perm:
            level[entry] = None
    return level

def getFileNames(d, result=[]):
    for k, v in d.iteritems():
        if isinstance(v, dict):
            getFileNames(v, result)
        if "final_true" in k:
            result.append(k)
    return result

def keypaths(d):
    for k, v in d.iteritems():
        if isinstance(v, collections.Mapping):
            for subkey, subvalue in keypaths(v):
                yield [k] + subkey, subvalue
        else:
            yield [k], v

def main():
    ftp = ftplib.FTP("chemdata.nist.gov")
    ftp.connect()
    ftp.login()
    #ftp.set_pasv(True)
    ftp.cwd('download/peptide_library/libraries')
    
    print 'Finding files. This may take a moment...'
    d = traverse(ftp)

    print 'Yay! We got the file list!'
    file_names = getFileNames(d)
    reverse_d = {}
    for keypath, value in keypaths(d):
        reverse_d.setdefault(value, []).append(keypath)
    raw_path_list = reverse_d[None]
    path_list = []
    for f in file_names:
        for p in raw_path_list:
            if f in p:
                path_list.append('download/peptide_library/libraries/'+'/'.join(p))

    if not os.path.exists('./data'):
        os.makedirs('./data')
    
    downloaded = []
    try:
        downloaded_files = open('downloaded.txt', 'r+')
        downloaded = downloaded_files.read().splitlines()
    except IOError:
        downloaded_files = open('downloaded.txt', 'w')

    print "Now it's time to download the files. This may take a while..."
    ftp.cwd('../../..')
    filecount = 1
    filetotal = len(path_list)
    for p in path_list:
        filename = p.split('/')[-1]
        if p in downloaded:
            filecount += 1
            print 'Already downloaded',filename,'\n'
            continue
        print "Downloading ("+str(filecount)+"/"+str(filetotal)+") " + filename
        ftp.sendcmd("TYPE i")
        filesize = ftp.size(p)
        ftp.sendcmd("TYPE A")
        '''
        site = urllib.urlopen("ftp://chemdata.nist.gov/"+p)
        meta = site.info()
        filesize = int(meta.getheaders('Content-Length')[0])
        '''
        widgets = [
            'Status: ', progressbar.Percentage(),
            ' ', progressbar.Bar(marker='#', left='[', right=']'),
        ]
        bar = progressbar.ProgressBar(widgets=widgets, maxval=filesize)
        bar.start()
        bar.update(0)
        total = 0
        with open('./data/'+filename, 'wb') as f:
            def callback(chunk):
                f.write(chunk)
                current = bar.percentage()/100.0*filesize
                new_current = current + len(chunk)
                if new_current > filesize:
                    new_current = filesize
                bar.update(new_current)

            ftp.retrbinary('RETR ' + p, lambda chunk: callback(chunk))
        bar.finish()
        downloaded_files.write(p+'\n')
        filecount += 1
        print '\n'
    downloaded_files.close()
    ftp.quit()

if __name__ == '__main__':
    main()