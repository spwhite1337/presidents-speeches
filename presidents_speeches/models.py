import os
import pickle

from gensim import corpora

from config import ROOT_DIR, logger


class SpeechModeler(object):
    """
    Object to model a vectorized corpus
    """
    load_dir = os.path.join(ROOT_DIR, 'data', 'curated')

    def __init__(self):
        logger.info('Loading Curated Corpus, Dictionary')
        with open(os.path.join(self.load_dir, 'corpus.pkl'), 'rb') as fp:
            self.corpus = pickle.load(fp)
        self.dictionary = corpora.Dictionary.load(os.path.join(self.load_dir, 'dictionary.dict'))
        logger.info('Loading Vectorized Corpus')
        self.vectorized = corpora.MmCorpus(os.path.join(self.load_dir, 'vectorized.mm'))

    def vectorize_corpus(self):
        logger.info('Vectorizing Corpus')
        return [self.dictionary.doc2bow(doc) for doc in self.corpus['documents']]

    def train(self):
        corpus = self.vectorize_corpus()
        logger.info('Training LSI Model')


def model():
    modeler = SpeechModeler()
    modeler.train()
