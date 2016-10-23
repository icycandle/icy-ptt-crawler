import json
from school_ip_map import scan_matcher, ALL_RULES
from ptt_ids import gc, bc
from mission_pigwar import get_fname
import csv

def info_tuple():
    for name, count in gc.items():
        yield name, count, 'good'
    for name, count in bc.items():
        yield name, count, 'bad'

all_data = []
for user, count, side in info_tuple():
    fname = get_fname(user)
    with open(fname, 'r') as f:
        data = json.loads(f.read())
    school = scan_matcher(data['ip'], ALL_RULES)
    data['school'] = school
    data['side'] = side
    data['重複推噓次數'] = count
    if data['name']:
        data['id'] = data['name'][0]
        data['nickname'] = data['name'][1]
    all_data.append(data)

with open('user-school.csv', 'w') as f:  # Just use 'w' mode in 3.x
    w = csv.DictWriter(f, all_data[0].keys())
    w.writeheader()
    for d in all_data:
        w.writerow(d)
