import csv, json
import sys
from collections import defaultdict

def inversion(block):
    out = defaultdict(set)
    for each in block:
        out[each[0]].add(each[1])
    with open('inverted.json', 'w') as f:
        o = {}
        for k in out:
            l= list(out[k])
            l.sort()
            o[k] = l
        f.write(json.dumps(o))


def get_postings(term, block, compression_mode):
    if compression_mode == 'DAAS':
        string, table = block
        entire_range = list(table.keys())
        tmp_range = [int(e) for e in entire_range]

        while len(tmp_range) > 1:
            if string[tmp_range[int(len(tmp_range)/2)-1]:tmp_range[int(len(tmp_range)/2)]]> term:
                tmp_range = tmp_range[:int(len(tmp_range)/2)]
            elif string[tmp_range[int(len(tmp_range)/2)-1]:tmp_range[int(len(tmp_range)/2)]]< term:
                tmp_range = tmp_range[int(len(tmp_range)/2):]
            elif string[tmp_range[int(len(tmp_range)/2)- 1]:tmp_range[int(len(tmp_range)/2)]] == term:
                tmp_range = [tmp_range[int(len(tmp_range)/2) - 1]]

        if len([tmp_range]) == 0:
            return []
        else:
            return table[str(tmp_range[0])][0]

    else:
        if term in block:
            return block[term]
        else:
            return []

def query(exp, block, compression_mode):
    op = ''
    postings = []
    for i, com in enumerate(exp.split(' ')):
        if com == '&' or com == '|' or com == '!':
            op = com
            continue
        if op:
            if op == '&':
                postings = [e for e in get_postings(com, block, compression_mode) if e in postings]
            elif op == '|':
                postings = list(set(get_postings(com, block, compression_mode)+postings))
            elif op == '!':
                postings = [e for e in  postings if e in get_postings(com, block, compression_mode)]
            op = ''
            continue
        if i ==0:
            postings = get_postings(com, block, compression_mode)
    return postings


def compression(compression_mode):
    with open('tmp27') as f:
        block = csv.reader(f)
        inversion(block)
    if compression_mode=='dictAsString':
        with open('inverted.json',) as f:
            block = json.load(f)
            table = {}
            longstring = ''
            for b in block:
                table[len(longstring)] = [block[b], len(block[b])]
                longstring+=b
        open('DAAS.json', 'w').write(json.dumps([longstring, table]))



def dictAsString(block):
    string = ''
    dict_ = {}
    for b in block:
        string+=id(b)
        dict_[id(b)] = []

def search(q, compression_mode):
    if compression_mode =='':
        block = json.load(open('inverted.json'))
    elif compression_mode == 'DAAS':
        block = json.load(open('DAAS.json'))
    return query(q, block, compression_mode)

if __name__=='__main__':
    compression_mode = 'DAAS'
    q = sys.argv[1]
    if len(sys.argv)==2:
        mode = 'AND'
    else:
        mode = sys.argv[2]
    # compression(compression_mode)
    print(search(q, compression_mode))