from concurrent.futures import ProcessPoolExecutor
import mmap
import os
from itertools import repeat

def findranges(chunksize, filesize, numchunks, filepath):
    ranges = []
    with open(filepath, "rb") as f:
        mm = mmap.mmap(f.fileno(), 0, access=mmap.ACCESS_READ)
        start = 0
        for i in range(numchunks - 1):
            mm.seek((i + 1) * chunksize)
            mm.readline()

            end = mm.tell()
            ranges.append((start, end))
            start = end
    ranges.append((start, filesize))
    return ranges

def processchunk(filepath, start, end):
    with open(filepath, "rb") as f:
        mm = mmap.mmap(f.fileno(), 0, access=mmap.ACCESS_READ)
        mm.seek(start)
        res = {}
        while mm.tell() < end:
            line = mm.readline()
            if not line:
                break
            city, val = line.strip().split(b";")
            val = float(val)
            cl = res.get(city, [9999, -9999, 0, 0])
            cl[0] = min(cl[0], val)
            cl[1] = max(cl[1], val)
            cl[2] += val
            cl[3] += 1
            res[city] = cl
        return res

def main():
    filepath = "measurements.txt"
    filesize = os.path.getsize(filepath)
    cities = {}
    numchunks = 16
    chunksize = filesize // numchunks
    ranges = findranges(chunksize, filesize, numchunks, filepath)
    starts = [r[0] for r in ranges]
    ends = [r[1] for r in ranges]
    
    with ProcessPoolExecutor(max_workers=numchunks) as executor:
        workers_res = list(executor.map(processchunk, repeat(filepath), starts, ends))

    for d in workers_res:
        for k, v in d.items():
            if k not in cities:
                cities[k] = v
            else:
                cities[k][0] = min(cities[k][0], v[0])
                cities[k][1] = max(cities[k][1], v[1])
                cities[k][2] += v[2]
                cities[k][3] += v[3]

    sorted_res = sorted([(c, v) for c, v in cities.items()])

    for c, v in sorted_res:
        print(f"{str(c, "utf-8")}, min: {v[0]}, avg: {round(v[2] / v[3], 1)}, max: {v[1]}")
    
if __name__ == "__main__":
  main()