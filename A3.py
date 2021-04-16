import csv, time
import os
import re, json
from nltk.stem.porter import *
import math
def get_term(token, stemmer):
    # Remove puncutaions
    token = re.sub(r'[^\w\s]', '', token)
    token = re.sub(r'_', '', token)

    # Stem
    token = stemmer.stem(token)
    # Case folding
    token = token.lower()
    # Remove numbers
    token = re.sub('\d+', '', token)
    return token

def get_tokens(lines, stemmer):
    terms = {}
    for line in lines:
        # Replace whitespaces to single space
        line = re.sub('\s+', ' ', line)
        for token in line.split(' '):
            term = get_term(token,  stemmer)
            # Check empty token
            if term != '':
                if term in terms:
                    terms[term] += 1
                else:
                    terms[term] = 0
    return terms

def get_files(dir):
    return os.listdir(dir)

def get_tf():
    tf = {}
    if os.path.exists('tf.json'):
        return json.load(open('tf.json'))
    files = get_files('HillaryEmails')
    for f in files:
        docid = f.replace('.txt', '')
        with open('HillaryEmails/' + f, errors="ignore") as fp:
            tf[docid] = get_tokens(fp.readlines(), stemmer)
    return tf

def get_df():
    return json.load(open('inverted.json'))

def calc_idf(df, N):
    idf = {}
    for t, postings in df.items():
        idf[t] = math.log(N/len(postings), 10)
    return idf

def calc_w(idf, tf):
    w = {}
    for doc, tf_ in tf.items():
        w[doc] = {}
        for term in tf_:
            if term in idf:
                w[doc][term] = math.log(1+int(tf_[term]),10)*float(idf[term])
    return w
if __name__=='__main__':
    stemmer = PorterStemmer()
    count = 0
    start = time.time()
    # tf = get_tf(files)
    # open('tf.json', 'w').write(json.dumps(tf))
    print('get tf took', time.time() - start)
    tf = get_tf()
    print(len(tf))
    df = get_df()
    idf = calc_idf(df, len(tf))
    w = calc_w(idf, tf)
    print(w)





