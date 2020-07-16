import os
import pickle

from gensim import corpora, models, similarities

from config import ROOT_DIR, logger


class SpeechModeler(object):
    """
    Object to model a vectorized corpus
    """
    load_dir = os.path.join(ROOT_DIR, 'data', 'curated')
    save_dir = os.path.join(ROOT_DIR, 'modeling', 'results')

    def __init__(self, num_topics: int = 10):
        logger.info('Loading Curated Corpus, Dictionary')
        with open(os.path.join(self.load_dir, 'corpus.pkl'), 'rb') as fp:
            self.corpus = pickle.load(fp)
        self.dictionary = corpora.Dictionary.load(os.path.join(self.load_dir, 'dictionary.dict'))
        logger.info('Loading Vectorized Corpus')
        self.vectorized = corpora.MmCorpus(os.path.join(self.load_dir, 'vectorized.mm'))

        # Number of dimensions in latent vector space
        self.num_topics = num_topics
        self.tfidf = None
        self.corpus_tfidf = None
        self.lsi_model = None
        self.similarity_index = None

        # I/O
        if not os.path.exists(self.save_dir):
            os.makedirs(self.save_dir)

    def _tfidf(self):
        """
        Map to term-frequency index
        """
        self.tfidf = models.TfidfModel(self.vectorized)
        self.corpus_tfidf = self.tfidf[self.vectorized]

    def train(self):
        """
        Train embeddings and similarities
        """
        logger.info('Training TFIDF Model')
        self._tfidf()
        logger.info('Training LSI Model')
        self.lsi_model = models.LsiModel(self.corpus_tfidf, id2word=self.dictionary, num_topics=self.num_topics)
        logger.info('Similarity Transformation of corpus')
        self.similarity_index = similarities.MatrixSimilarity(self.lsi_model[self.corpus_tfidf],
                                                              num_features=self.num_topics)

    def save(self):
        """
        Save dictionary, models, and similarity index
        """
        logger.info('Save tfidf model')
        self.tfidf.save(os.path.join(self.save_dir, 'tfidf.model'))
        logger.info('Save LSI model')
        self.lsi_model.save(os.path.join(self.save_dir, 'lsi.model'))
        logger.info('Saving Similarity Index')
        self.similarity_index.save(os.path.join(self.save_dir, 'similarities.index'))


def model():
    modeler = SpeechModeler()
    modeler.train()
    modeler.save()
