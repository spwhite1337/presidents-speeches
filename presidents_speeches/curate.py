import os
import re
import json

from config import ROOT_DIR, logger


class SpeechCurator(object):
    """
    Object to curate speeches into corpora
    """
    load_dir = os.path.join(ROOT_DIR, 'data', 'raw')
    save_dir = os.path.join(ROOT_DIR, 'data', 'curated')

    # Words to drop
    stoplist = set('for a of the and to in (applause.) -– - -- – –- q.'.split())

    def __init__(self):
        if not os.path.exists(self.save_dir):
            os.makedirs(self.save_dir)

        logger.info('Loading Raw Speeches')
        # Dictionary of (presidents: list of speeches)
        with open(os.path.join(self.load_dir, 'speeches.json'), 'r') as fp:
            self.raw = json.load(fp)

        logger.info('Loading Groups')
        # Dictionary defining eras, parties from presidents
        with open(os.path.join(self.load_dir, 'groups.json'), 'r') as fp:
            self.groups = json.load(fp)

    def _clean_speech(self, speech: str) -> list:
        no_specials = re.sub('[^a-zA-Z \']', '', speech)
        return [w for w in no_specials.lower().split() if w not in self.stoplist]

    def create_groups(self):
        # Get speeches for each era, party
        eras = self.groups['eras']