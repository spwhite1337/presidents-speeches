import os
import re
import argparse
import pickle
import pprint

import pandas as pd

from gensim import corpora, models, similarities

from config import Config, logger


class SpeechPredictor(object):
    """
    Object to determine the speech and president an input sentence is most similar
    """
    data_dir = Config.CURATED_DIR
    load_dir = Config.RESULTS_DIR

    # Words to drop
    stoplist = set('for a of the and to in (applause.) -– - -- – –- q.'.split(' '))

    def __init__(self):
        logger.info('Load Corpus')
        with open(os.path.join(self.data_dir, 'corpus.pkl'), 'rb') as fp:
            self.corpus = pickle.load(fp)

        logger.info('Loading Dictionary, Similarity Index')
        self.dictionary = corpora.Dictionary.load(os.path.join(self.data_dir, 'dictionary.dict'))
        self.similarity_index = similarities.MatrixSimilarity.load(os.path.join(self.load_dir, 'similarities.index'))

        logger.info('Load models')
        self.tfidf = models.TfidfModel.load(os.path.join(self.load_dir, 'tfidf.model'))
        self.lsi_model = models.LsiModel.load(os.path.join(self.load_dir, 'lsi.model'))

    def tokenize_input(self, query: str):
        """
        Process an input in the same manner as training the embeddings
        """
        no_specials = re.sub('[^a-zA-Z \']', ' ', query)
        clean_query = [w for w in no_specials.lower().split() if w not in self.stoplist]
        return self.dictionary.doc2bow(clean_query)

    def get_similarities(self, query: list):
        """
        A list of tokens is converted to a vector in the LSI space of the trained model and compared to corpus
        """
        logger.info('Mapping query to LSI Space')
        query_tfidf = self.tfidf[query]
        query_lsi = self.lsi_model[query_tfidf]

        logger.info('Comparing to Corpus')
        return self.similarity_index[query_lsi]

    @staticmethod
    def serialize_output(labels: list, n: int = 10) -> dict:
        """
        Convert list of labeled similarities to a dictionary where keys are output labels and values are sorted lists
        of most similar entries
        """
        # df sorted by similarities
        df = pd.DataFrame(labels)
        df.columns = ['id', 'similarity', 'president', 'speech']

        # Top speeches
        # Get cumulative score for each speech as the sum of similarities for top ten closest documents for that
        # speech. E.g. Which documents for this speech are closest to query (top 3)? What is the total sum of
        # all similarity scores? Which n speeches had the highest sum?
        df_speeches = df.copy()
        # Score for a speech is the cumulative sum of similarities, ordered by most similar -> least similar
        df_speeches['speech_score'] = df_speeches.groupby('speech')['similarity'].cumsum()
        # Rank the documents in the speech by most similar -> least similar
        df_speeches['doc_rank'] = df_speeches.groupby('speech')['similarity'].cumcount() + 1

        # Look at the fifth most similar document (or lowest rank if less than five documents)
        # This number is relatively arbitrary, but captures intuition that "a few documents should be similar to input,
        # not just one or two, but not all documents have to be similar to the input".
        df_speeches = df_speeches[df_speeches['doc_rank'] < 5]
        df_speeches = df_speeches[df_speeches['doc_rank'] == df_speeches['doc_rank'].max()]

        # Sort document-speeches by score and return the top n
        df_speeches = df_speeches.sort_values('speech_score', ascending=False).reset_index(drop=True)
        speeches = list(df_speeches['speech'])[:n]
        speeches_score = list(df_speeches['speech_score'])[:n]

        # Same approach for presidents
        df_pres = df.copy()
        # Score for a president is the cumulative sum of similarities, ordered by most similar -> least similar
        df_pres['president_score'] = df_pres.groupby('president')['similarity'].cumsum()
        # Rank the documents in the president by most similar -> least similar
        df_pres['doc_rank'] = df_pres.groupby('president')['similarity'].cumcount() + 1

        # Look at the fifth most similar document (or lowest rank if less than five documents)
        # This number is relatively arbitrary, but captures intuition that "a few documents should be similar to input,
        # not just one or two, but not all documents have to be similar to the input".
        df_pres = df_pres[df_pres['doc_rank'] < 5]
        df_pres = df_pres[df_pres['doc_rank'] == df_pres['doc_rank'].max()]

        # Sort document-presidents by score and return the top n
        df_pres = df_pres.sort_values('president_score', ascending=False).reset_index(drop=True)
        presidents = list(df_pres['president'])[:n]
        presidents_score = list(df_pres['president_score'])[:n]

        return {'speeches': speeches, 'presidents': presidents, 'speeches_sim': speeches_score,
                'presidents_sim': presidents_score}

    def predict(self, query: str, n: int = 10, display_output: bool = False) -> dict:
        """
        Return the most similar speeches, presidents
        """
        token = self.tokenize_input(query)
        sims = self.get_similarities(token)

        # Enumerate and sort similarities by similarity output
        sims = sorted(enumerate(sims), key=lambda i: -i[1])
        # Add president, speech labels
        sims = [sim + self.corpus['labels'][sim[0]] for sim in sims]
        # Serialize output
        output = self.serialize_output(sims, n)

        return {query: output}


def api_cli():
    parser = argparse.ArgumentParser(prog='Presidential similarity')
    parser.add_argument('--query', type=str, default='Fake News')
    parser.add_argument('--num_out', type=int, default=10)
    parser.add_argument('--display', action='store_true')
    args = parser.parse_args()

    api(args.query, args.num_out, args.display)


def api(query: str, num_out: int = 10, display_output: bool = False):
    predictor = SpeechPredictor()
    output = predictor.predict(query, num_out, display_output)
    if display_output:
        pp = pprint.PrettyPrinter(indent=4, compact=True)
        logger.info('Output: \n {}'.format(pp.pprint(output)))
    return output
