from entries.cas_entry import CasEntry
import csv


dir = 'C:/Users/WitLab/Desktop/190710_test'
flist = CasEntry.search(dir)

outfile = open(dir + '/output.csv', 'w')
csv_writer = csv.writer(outfile)
csv_writer.writerow(['time', 'illum', 'cct', 'swr'])

for fname in flist:
    entry = CasEntry(fname)
    if not entry.valid:
        continue

    time = entry.get_datetime(tostr=True)
    illum = entry.get_attrib('Photometric')
    cct = entry.get_attrib('CCT')
    swr = entry.get_attrib('swr')

    row = [time, illum, cct, swr]
    print(row)
    csv_writer.writerow(row)

outfile.close()



