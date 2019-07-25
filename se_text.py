import re, string, math
import numpy as np
from collections import Counter
from gensim.models.keyedvectors import KeyedVectors as KV

def se_text(caption: str, all_captions: list(str)):
    """
    Returns an embedded representation for a string of text.

    Parameters
    ----------
    caption: String
        The text that you want an embedding for.
    all_captions: list(str)
        All the captions in the database.
    
    Returns
    -------
    np.array([])
        The embedded representation for the string passed in.
    """
    glove50 = KV.load_word2vec_format('/Users/crystal/Desktop/python-workspace/CogWorks2019/glove.6B.50d.txt.w2v', binary=False)

    caption = strip_punc(caption).lower().split()
    embedding = np.zeros((1, 50))

    for word in caption:
        embedding += glove50[word]*to_idf(all_captions)
        
    embedding = normalize(embedding/len(caption))

    return embedding

def normalize(vector):
    """
    Normalize a vector of numbers to have unit length.

    Parameters
    ----------
    Vector: np.array([])
        The vector that you want normalized.

    Returns
    -------
    np.array([])
        The normalized vector.
    """
    return(vector/np.mean(vector) - 1)

def to_idf(all_captions):
    """ 
    Given the vocabulary, and the word-counts for each document, computes
    the inverse document frequency (IDF) for each term in the vocabulary.
    
    Parameters
    ----------
    captions: Iterable(strings)
        All captions in the database.
    
    Returns
    -------
    numpy.ndarray
        An array whose entries correspond to those in `vocab`, storing
        the IDF for each term `t`: 
                           log10(N / nt)
        Where `N` is the number of documents, and `nt` is the number of 
        documents in which the term `t` occurs.
    """
    counters = []
    for caption in all_captions:
        counters.append(Counter(strip_punc(caption).lower().split()))
    
    with open("./dat/stopwords.txt", 'r') as r:
        stops = []
        for line in r:
            stops += [i.strip() for i in line.split('\t')]

    vocab = to_vocab(counters, k=None, stop_words=stops)

    idf = list()
    total_counter = Counter()
    for counter in counters:
        total_counter.update(set(counter)) #makes sure there's only one of each word per doc at most
    for word in vocab:
        idf.append(math.log(len(counters)/total_counter[word], 10))
    return np.array(idf)

def to_vocab(counters, k=None, stop_words=None):
    """ 
    [word, word, ...] -> sorted list of top-k unique words
    Excludes words included in `stop_words`
    
    Parameters
    ----------
    counters : Iterable[Iterable[str]]
    
    k : Optional[int]
        If specified, only the top-k words are returned
    
    stop_words : Optional[Collection[str]]
        A collection of words to be ignored when populating the vocabulary
    """
    vocab_set = set()
    if stop_words is None:
        stop_words = []

    total_counter = Counter()
    for counter in counters:
        total_counter.update(dict((key, value) for key, value in counter.items() if key not in stop_words))

    if k is not None:
        total_counter = total_counter.most_common(k)
        vocab_set.update(pair[0] for pair in total_counter)
    else:
        vocab_set.update(key for key in total_counter.keys())
        
    return sorted(vocab_set)

def strip_punc(corpus):
    """ Removes all punctuation from a string.

        Parameters
        ----------
        corpus : str

        Returns
        -------
        str
            the corpus with all punctuation removed"""

    punc_regex = re.compile('[{}]'.format(re.escape(string.punctuation)))
    return punc_regex.sub("", corpus)