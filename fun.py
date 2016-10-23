from collections import Counter
import re

from pprint import pprint

with open('fun.txt', 'r') as f:
	ls = f.readlines()

bad = []
good = []

bad_pattern = r'噓  \[33m(\w+) \[m'
good_pattern = r'推  \[33m(\w+) \[m'

for l in ls:

	bad_r = re.findall(bad_pattern, l)
	good_r = re.findall(good_pattern, l)

	if bad_r:
		bad += bad_r
	else:
		good += good_r

bc = Counter(bad)
gc = Counter(good)

pprint(bc)
pprint(gc)

print("len(bc): %s" % len(bc))
print("len(gc): %s" % len(gc))
