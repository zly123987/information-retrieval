import csv, json
import sys
from collections import defaultdict
import time
block_size = 10
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

def ori_inversion(block):
    out = defaultdict(set)
    for each in block:
        out[each[0]].add(each[1])
    with open('ori_inverted.json', 'w') as f:
        o = {}
        for k in out:
            l = list(out[k])
            l.sort()
            o["{:<127}".format(k)] = l
        f.write(json.dumps(o))

def get_postings(term, block, compression_mode):
    if compression_mode == 'DAAS':
        string, table = block
        tmp_range = list(table.keys())

        while len(tmp_range) > 1:
            if string[tmp_range[int(len(tmp_range)/2)-1]:tmp_range[int(len(tmp_range)/2)]]> term:
                tmp_range = tmp_range[:int(len(tmp_range)/2)]
            elif string[tmp_range[int(len(tmp_range)/2)-1]:tmp_range[int(len(tmp_range)/2)]]< term:
                tmp_range = tmp_range[int(len(tmp_range)/2):]
            elif string[tmp_range[int(len(tmp_range)/2)- 1]:tmp_range[int(len(tmp_range)/2)]] == term:
                tmp_range = [tmp_range[int(len(tmp_range)/2) - 1]]

        if len(tmp_range) == 0:
            return []
        else:
            return table[tmp_range[0]]
    elif compression_mode == 'blocking':
        string, table, length = block
        entire = list(table.keys())


        tmp_range = entire
        while len(tmp_range) > 2:
            if string[tmp_range[int(len(tmp_range) / 2) ]:tmp_range[int(len(tmp_range) / 2)+1]][:length[entire.index(tmp_range[int(len(tmp_range) / 2)])][0]] == term:
                tmp_range = [tmp_range[int(len(tmp_range) / 2)]]
            elif string[tmp_range[int(len(tmp_range) / 2) ]:tmp_range[int(len(tmp_range) / 2)+1]] > term:
                tmp_range = tmp_range[:int(len(tmp_range) / 2)]
            elif string[tmp_range[int(len(tmp_range) / 2) ]:tmp_range[int(len(tmp_range) / 2)]+1] < term:
                tmp_range = tmp_range[int(len(tmp_range) / 2):]

        if len(tmp_range)==2:
            if string[tmp_range[1]:entire[entire.index(tmp_range[1])+1]] > term:
                tmp_range = [tmp_range[0]]
            else:
                tmp_range = [tmp_range[1]]
        if len(tmp_range) == 0:
            return []
        else:
            offset = 0
            for i, le in enumerate(length[entire.index(tmp_range[0])]):
                print(string[tmp_range[0]+offset: tmp_range[0]+offset+le])
                if string[tmp_range[0]+offset: tmp_range[0]+offset+le] == term:
                    return table[tmp_range[0]][i]
                offset+=le
            return []
    else:
        term = "{:<127}".format(term)
        tmp_range = list(block.keys())
        while len(tmp_range) > 1:
            if tmp_range[int(len(tmp_range) / 2) - 1] > term:
                tmp_range = tmp_range[:int(len(tmp_range) / 2)]
            elif tmp_range[int(len(tmp_range) / 2) - 1] < term:
                tmp_range = tmp_range[int(len(tmp_range) / 2):]
            elif tmp_range[int(len(tmp_range) / 2) - 1] == term:
                tmp_range = [tmp_range[int(len(tmp_range) / 2) - 1]]

        if len(tmp_range) == 0:
            return []
        else:
            return block[tmp_range[0]]


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
                postings = [e for e in postings if e not in get_postings(com, block, compression_mode)]
            op = ''
            continue
        if i ==0:
            postings = get_postings(com, block, compression_mode)
    time.sleep(0.2)
    return postings


def compression(compression_mode):
    # with open('tmp27') as f:
    #     block = csv.reader(f)
    #     inversion(block)
    if compression_mode=='':
        with open('inverted.json', ) as f:
            out=json.load(f)
            block = {}
            for k in out:
                l = list(out[k])
                l.sort()
                block["{:<127}".format(k)] = l

    if compression_mode == 'DAAS':
        with open('inverted.json', ) as f:
            block = json.load(f)
            table = {}
            longstring = ''
            for b in block:
                table[len(longstring)] = block[b]
                longstring += b
        # open('DAAS.json', 'w').write(json.dumps([longstring, table]))
        block = [longstring, table]
    elif compression_mode == 'blocking':
        with open('inverted.json', ) as f:
            block = json.load(f)
            table = {}
            length= []
            tmp = None
            longstring = ''
            current = 0
            count = 0
            for b in block:
                if count%block_size==0:
                    current = len(longstring)
                    if tmp:
                        length.append(tmp)
                    table[current] = [block[b]]
                    longstring += b
                    tmp = [len(b)]

                else:
                    table[current].append(block[b])
                    longstring += b
                    tmp.append(len(b))
                count +=1
        # open('DAAS.json', 'w').write(json.dumps([longstring, table]))
        length.append(tmp)
        block = [longstring, table, length]
    return block



def dictAsString(block):
    string = ''
    dict_ = {}
    for b in block:
        string+=id(b)
        dict_[id(b)] = []

def search(q, compression_mode):
    if compression_mode =='':
        block = json.load(open('ori_inverted.json'))
    elif compression_mode == 'bloccccccccccccccking':
        block = json.load(open('DAAS.json'))
    return query(q, block, compression_mode)

if __name__=='__main__':
    start = time.time()
    compression_mode = 'blocking'
    q = sys.argv[1]
    block = compression(compression_mode)
    print('Compression took', time.time()-start)
    start = time.time()
    print(query(q.lower(), block, compression_mode))
    print('Search took', time.time() - start)