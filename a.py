import sys, os
import csv
import re
from time import time
from nltk.stem.porter import *

# Initialization
if not os.path.exists('term_pairs'):
    os.mkdir('term_pairs')
if not os.path.exists('term_pairs_sorted'):
    os.mkdir('term_pairs_sorted')
dir = sys.argv[1]
block_size = int(sys.argv[2])
counter = 0
block_count = 0
block = []
fw = open('term_pairs/token_doc0.csv', 'a')
csv_output = csv.writer(fw, lineterminator='\n')

def get_term(token, docid, stemmer):
    # Remove puncutaions
    token = re.sub(r'[^\w\s]', '', token)
    token = re.sub(r'_', '', token)

    # Stem
    token = stemmer.stem(token)
    # Case folding
    token = token.lower()
    # Remove numbers
    token = re.sub('\d+', '', token)
    return [token, docid]


def get_tokens(lines, docid, stemmer):
    global block_count, block, fw, csv_output

    for line in lines:
        # Replace whitespaces to single space
        line = re.sub('\s+', ' ', line)
        for token in line.split(' '):
            term_pair = get_term(token, docid, stemmer)
            # Check empty token
            if term_pair[0] != '':
                block.append(term_pair)
                if len(block) == block_size:
                    fw = open('term_pairs/token_doc' + str(block_count) + '.csv', 'a')
                    csv_output = csv.writer(fw, lineterminator='\n')
                    block_count += 1
                    csv_output.writerows(block)
                    fw.close()
                    block = []


def get_files(dir):
    return os.listdir(dir)

def inversion(block):
    names = []
    postings = []
    for each in block:
        if each[0] not in names:
            names.append(each[0])
            postings.append(each[1])
        else:
            postings[names.index(each[0])].append(each[1])
    names.sort()
    return [[names[i], postings[i]] for i in range(len(names))]

def merge(file1, file2, out):
    with open(out, 'a') as f:
        o = csv.writer(f)
        counts = [block_size, block_size]
        head1 = None
        head2 = None
        last1 = None
        last2 = None
        f1 = open(file1, 'r')
        f2 = open(file2, 'r')
        reader1 = csv.reader(f1)
        reader2 = csv.reader(f2)
        while counts[0] >0 or counts[1]>0:
            if not head1:
                try:
                    head1 = next(reader1)
                except:
                    head1 = None
            if not head2:
                try:
                    head2 = next(reader2)
                except:
                    head2 = None
            if head1==None and head2==None:
                break


            elif not head2 and head1:
                if head1[0]!=last1:
                    o.writerow([head1[0], head1[1]])
                    last1 = head1[0]
                head1 = None
                counts[0] -= 1

            elif not head1 and head2:
                if head2[0]!=last2:
                    o.writerow([head2[0], head2[1]])
                    last2 = head2[0]
                head2 = None
                counts[1] -= 1

            elif head1[0] > head2[0]:
                if head2[0] != last2:
                    o.writerow([head2[0], head2[1]])
                    last2 = head2[0]
                head2 = None
                counts[1] -= 1
            elif (head1[0] < head2[0]):
                if head1[0] != last1:
                    o.writerow([head1[0], head1[1]])
                    last1 = head1[0]
                head1 = None
                counts[0] -= 1

            elif head1[0]==head2[0]:
                if head1[0] != last1 and head2[0] != last2:
                    posting =head1[1].split('|')
                    posting.append(head2[1])
                    posting = list(set(posting))
                    posting.sort()
                    # block.append([head1[0], ','.join(posting)])
                    o.writerow([head1[0], '|'.join(posting)])
                    last1 = head1[0]
                    last2 = head2[0]
                head1, head2=None, None
                counts[0] -= 1
                counts[1] -= 1

if __name__ == '__main__':
    # stemmer = PorterStemmer()
    #
    # # Read files
    # files = get_files('HillaryEmails')
    #
    # count = 0
    # start = time()
    # # Tokenization
    # for f in files:
    #     with open('HillaryEmails/' + f, errors="ignore") as fp:
    #         get_tokens(fp.readlines(), f.replace('.txt', ''), stemmer)
    #     count += 1
    # print('Tokenization took:', time() - start)
    #
    # # BSBI
    # start = time()
    # termfiles = os.listdir('term_pairs')
    # for f in termfiles:
    #     with open('term_pairs/'+f) as ftoken, open('term_pairs_sorted/'+f, 'w') as fw:
    #         block = list(csv.reader(ftoken))
    #         block.sort()
    #         csv.writer(fw, lineterminator='\n').writerows(block)
    # print('Sort took:', time() - start)

    start = time()
    sorted_files = os.listdir('term_pairs_sorted')
    tmp = None
    for i, f in enumerate(sorted_files):
        if i ==0:
            tmp = f
            continue
        merge('term_pairs_sorted/'+tmp, 'term_pairs_sorted/'+f, 'term_pairs_sorted/tmp'+str(i))
        tmp ='tmp'+str(i)
    print('Final sort took:', time() - start)


