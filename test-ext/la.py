import linecache
import mmap
import random
import sys

def mapcount(filename):
    f = open(filename, "r+")
    buf = mmap.mmap(f.fileno(), 0)
    lines = 0
    readline = buf.readline
    while readline():
        lines += 1
    return lines

total = mapcount("pdflist")
count = 4
chosen_files = random.sample([i for i in xrange(1,total+1)],min(total,count))
for i in chosen_files:
    sys.stdout.write("# %s\n"%i)
    sys.stdout.write("cp \"%s\" .\n"%linecache.getline("pdflist",i).strip())
