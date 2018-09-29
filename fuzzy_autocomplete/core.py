import collections
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
            self.word_index = collections.defaultdict(
                lambda: collections.defaultdict(list))
            for word in self.words:
                for position, letter in enumerate(word):
                    self.word_index[letter][word].append(position)
            for key, value in self.word_index.items():
                sorted_index = sorted(value.items(), key=lambda item: min(item[1]))
                self.word_index[key] = {
                    word: positions for word, positions in sorted_index}

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
        exclude = exclude[:]
        for letter in word:
            bucket = self.word_index[letter]
            suggestions = self._generate_matches_in_bucket(
                word=word, bucket=bucket, exclude=exclude[:])
            for new_word in suggestions:
                yield new_word
                exclude.append(new_word)

    def _generate_matches_in_bucket(
            self, *, word: str, bucket: dict, exclude: list):
        for dictionary_word in bucket:
            if dictionary_word in exclude:
                continue
            for letter in word:
                if letter not in dictionary_word:
                    break
            else:
                logger.debug(f'Word: {dictionary_word} Count: {self.words[dictionary_word]}')
                yield dictionary_word


filename = path.join(path.dirname(path.abspath(__file__)), 'word_search.tsv')
