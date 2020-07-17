import os
import re
import json
import pickle

from tqdm import tqdm

from gensim import corpora

from config import Config, logger


class SpeechCurator(object):
    """
    Object to curate speeches into corpora
    """
    load_dir = Config.RAW_DIR
    save_dir = Config.CURATED_DIR

    # Words to drop
    stoplist = set('for a of the and to in (applause.) -– - -- – –- q.'.split(' '))

    def __init__(self):
        if not os.path.exists(self.save_dir):
            os.makedirs(self.save_dir)

        logger.info('Loading Raw Speeches')
        # Dictionary of (presidents: list of speeches)
        with open(os.path.join(self.load_dir, 'speeches.json'), 'r') as fp:
            self.speeches = json.load(fp)

        self.corpus = None
        self.dictionary = None
        self.vectorized = None

    def _tokenize(self, speech: str) -> list:
        no_specials = re.sub('[^a-zA-Z \']', ' ', speech)
        return [w for w in no_specials.lower().split() if w not in self.stoplist]

    def create_corpus(self):
        """
        Generate a corpus where each document is a sentence from a speech.
        Speakers are the list of presidents who spoke each document (preserve order)
        """
        documents, labels = [], []
        logger.info('Creating Corpus')
        for president, speeches in tqdm(self.speeches.items()):
            for idx, speech in enumerate(speeches['speeches']):
                # Each sentence defines a document for the president
                sentences = re.split('\. |!|\?', speech)
                # Tokenize each sentence
                clean_sentences = [self._tokenize(sentence) for sentence in sentences]
                # Save documents as lists of cleaned words
                documents += clean_sentences
                # Save speakers, urls as a "label" for each document
                url = speeches['urls'][idx]
                labels += [(president, url)] * len(clean_sentences)
        logger.info('Generated {} documents with {} labels'.format(len(documents), len(labels)))
        self.corpus = {'documents': documents, 'labels': labels}

        return self.corpus

    def create_dictionary(self):
        if self.corpus is None:
            raise ValueError('Run self.create_corpus()')
        logger.info('Vectorizing Corpus')
        # Map corpus to dictionary
        self.dictionary = corpora.Dictionary(self.corpus['documents'])

        # Vectorize corpus
        self.vectorized = [self.dictionary.doc2bow(doc) for doc in self.corpus['documents']]

    def save(self):
        """
        Save organized corpus and vectorized corpus
        """
        logger.info('Saving Corpus')
        with open(os.path.join(self.save_dir, 'corpus.pkl'), 'wb') as fp:
            pickle.dump(self.corpus, fp)

        logger.info('Saving Dictionary')
        self.dictionary.save(os.path.join(self.save_dir, 'dictionary.dict'))

        logger.info('Saving Vectorized Corpus')
        corpora.MmCorpus.serialize(os.path.join(self.save_dir, 'vectorized.mm'), self.vectorized)


def curate():
    curator = SpeechCurator()
    curator.create_corpus()
    curator.create_dictionary()
    curator.save()
