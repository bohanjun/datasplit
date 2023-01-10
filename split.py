import os
import math
import random
import shutil
import argparse


def two_args_str_float(x):
    try:
        return float(x)
    except:
        return x

parser = argparse.ArgumentParser(description="To split your datasets automatically.", add_help=True)

parser.add_argument("source", type=str, nargs=1)
parser.add_argument("--subset", "-s", action="append", type=two_args_str_float, nargs=2)
parser.add_argument("--format", "-f", action="append", type=str, nargs=2)
parser.add_argument("--list", "-l", action="append", type=str, nargs=3)
parser.add_argument("--random", "-r", action="store_true")
parser.add_argument("--target", "-t", type=str, nargs=1)

args = parser.parse_args()

cwd = os.getcwd()
targetDir = os.path.abspath(args.target[0])
os.makedirs(targetDir, exist_ok=True)
dataSource = os.path.abspath(args.source[0])

os.chdir(dataSource)
files = os.listdir(dataSource)
data = {}
for file in files:
    if not os.path.isfile(file):
        continue
    [filename, filetype] = file.rsplit(".", 1)
    if data.get(filename) == None:
        data[filename] = [filetype]
    else:
        data[filename].append(filetype)

sortedData = list(data)
dataSize = len(data)

if args.random:
    random.shuffle(sortedData)
else:
    sortedData.sort()

total_weight = 0
for subset in args.subset:
    assert type(subset[0]) == str
    assert type(subset[1]) == float
    assert subset[1] > 0
    total_weight += subset[1]

subsetsSize = []
subsetsSizeSum = 0
for subset in args.subset:
    subsetsSize.append(math.floor(dataSize / total_weight * subset[1]))
    subsetsSizeSum += math.floor(dataSize / total_weight * subset[1])

for i in range(subsetsSizeSum, min(dataSize, subsetsSizeSum + len(subsetsSize))):
    subsetsSize[i - subsetsSizeSum] += (
        (dataSize - subsetsSizeSum) // len(subsetsSize)
        + (
            i - subsetsSizeSum
            < ((dataSize - subsetsSizeSum) % len(subsetsSize))
        )
    )

listedData = {}
for li in args.list:
    listedData[(li[0], li[1])] = li[2]

lists = dict([[filename, ""] for filename in list(set(listedData.values()))])

formats = dict(args.format)
curSubsetStart = 0
for i in range(len(args.subset)):
    for j in range(curSubsetStart, curSubsetStart + subsetsSize[i]):
        for filetype in data[sortedData[j]]:
            if not filetype in formats:
                continue
            os.chdir(targetDir)
            targetPath = os.path.abspath((formats[filetype]).format(
                s=args.subset[i][0],
                subset=args.subset[i][0],
                n=sortedData[j],
                name=sortedData[j],
                filename=sortedData[j],
                t=filetype,
                type=filetype,
                filetype=filetype,
            ))
            os.makedirs(os.path.dirname(targetPath), exist_ok=True)
            os.chdir(dataSource)
            sourcePath = os.path.abspath(f"{sortedData[j]}.{filetype}")
            shutil.copy(sourcePath, targetPath)
            if (args.subset[i][0], filetype) in listedData:
                lists[listedData[(args.subset[i][0], filetype)]] += targetPath + "\n"
    curSubsetStart += subsetsSize[i]

os.chdir(targetDir)
for li in lists:
    targetPath = os.path.abspath(li)
    fd = os.open(targetPath, os.O_RDWR | os.O_CREAT)
    os.write(fd, bytes(lists[li], encoding="utf-8"))
    os.close(fd)

print("succeed", subsetsSize)
