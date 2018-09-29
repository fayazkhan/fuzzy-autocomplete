import csv
import itertools
import operator
from os import path

import logbook


logger = logbook.Logger()


class Autocompleter:
    def __init__(self):
        with open(filename, 'r', newline='') as words_file:
            words_reader = csv.reader(words_file, delimiter='\t')
            word_list = sorted(
                ((word, int(occurrence)) for word, occurrence in words_reader),
                key=operator.itemgetter(1), reverse=True)
            self.words = dict(word_list)

    def suggest_matches(self, word: str):
        return itertools.islice(self._generate_fuzzy_matches(word), 25)

    def _generate_fuzzy_matches(self, word: str):
        exclude = []
        if word in self.words:
            logger.debug(f'Word: {word} Count: {self.words[word]}')
            yield word
            exclude.append(word)
        yield from self._generate_matches(word, exclude)

    def _generate_matches(self, word: str, exclude: list):
        for dictionary_word, count in self.words.items():
            if dictionary_word in exclude:
                continue
            for letter in word:
                if letter not in dictionary_word:
                    break
            else:
                logger.debug(f'Word: {dictionary_word} Count: {count}')
                yield dictionary_word


filename = path.join(path.dirname(path.abspath(__file__)), 'word_search.tsv')
