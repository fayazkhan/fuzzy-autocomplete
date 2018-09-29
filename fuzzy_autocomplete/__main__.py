import sys
import time

import logbook

from fuzzy_autocomplete import core


logbook.StreamHandler(sys.stderr).push_application()
autocompleter = core.Autocompleter()


while True:
    try:
        word = input('Enter word: ')
    except EOFError:
        print()
        break
    print('Matches:')
    start_time = time.perf_counter_ns()
    time_taken = time.perf_counter_ns() - start_time
    print(f'Execution time: {time_taken} ns')
    if time_taken > 50000:
        print('Excution slow!!!')
    for i, match in enumerate(autocompleter.suggest_matches(word), 1):
        print(f'{i}. {match}')
    print()
