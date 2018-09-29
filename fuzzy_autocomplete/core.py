import collections
import csv
import itertools
import operator
from os import path

import logbook
from tqdm import tqdm


logger = logbook.Logger()


class Autocompleter:
    def __init__(self):
        with open(filename, 'r', newline='') as words_file:
            words_reader = csv.reader(words_file, delimiter='\t')
            self.words = {word: int(occurrence) for word, occurrence in words_reader}
        self._index_words()

    def _index_words(self):
        # TODO: Optimize memory
        self.word_index = {}
        max_occurrence = max(self.words.values())
        substring_positions = collections.defaultdict(lambda: collections.defaultdict(set))
        for word in tqdm(self.words):
            logger.debug(f'Indexing {word}')
            for substring, position in set(word_groups(word)):
                substring_positions[substring][word].add(position)
        for substring, value in substring_positions.items():
            sorted_index = sorted(
                ((word, (min(positions), max_occurrence - self.words[word], len(word)))
                 for word, positions in value.items()),
                key=operator.itemgetter(1))
            self.word_index[substring] = [word for word, _ in sorted_index]
        keys = len(self.word_index.keys())
        values = sum(len(value) for value in self.word_index.values())
        print(f'Index size: {keys} keys, {values} values')

    def suggest_matches(self, word: str):
        return itertools.islice(self._generate_fuzzy_matches(word), 25)

    def _generate_fuzzy_matches(self, word: str):
        # TODO: Fuzzy match. Tolerate typos
        exclude = set()
        for new_word in self._generate_matches(word, exclude):
            yield new_word
            exclude.add(new_word)
        for edit in self._known_edits(word):
            for new_word in self._generate_matches(edit, exclude):
                yield new_word
                exclude.add(new_word)

    alphabet = 'abcdefghijklmnopqrstuvwxyz'

    def _known_edits(self, word: str):
        # Source: http://scottlobdell.me/2015/02/writing-autocomplete-engine-scratch-python/
        length = len(word)
        word_splits = [(word[:i], word[i:]) for i in range(length)]
        deletes = (first + second[1:] for first, second in word_splits)
        swaps = (first + second[1] + second[0] + second[2:]
                 for first, second in word_splits[:-1]
                 if second[0] != second[1])
        replacements = (first + letter + second[1:]
                        for first, second in word_splits
                        for letter in self.alphabet
                        if letter != second[0])
        insertions = (first + letter + second for first, second in word_splits
                      for letter in self.alphabet)
        for edit in set(itertools.chain(deletes, swaps, replacements, insertions)):
            logger.debug(f'Edit: {edit}')
            if edit in self.word_index:
                logger.debug(f'Known edit: {edit}')
                yield edit

    def _generate_matches(self, word: str, exclude: set):
        if word in self.words:
            yield word
            exclude.add(word)
        try:
            bucket = self.word_index[word]
        except KeyError:
            return
        for new_word in bucket:
            # TODO: Optimize data structure
            if new_word in exclude:
                continue
            yield new_word
        exclude.update(bucket)
        logger.debug(f'Excluded elements: {exclude}')


filename = path.join(path.dirname(path.abspath(__file__)), 'word_search.tsv')


def word_groups(word):
    length = len(word)
    for start in range(length):
        for end in range(length, start, -1):
            yield word[start: end], start
