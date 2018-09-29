import sys
import time

from flask import Flask, jsonify, request
import logbook

from .core import Autocompleter


logger = logbook.Logger(__name__)
log_handler = logbook.FingersCrossedHandler(logbook.StreamHandler(sys.stderr))
autocompleter = Autocompleter()
app = Flask(__name__)


@app.route('/search/')
def search():
    word = request.args.get('word')
    if not word:
        return jsonify({'data': [], 'execution_time_ns': 0})
    start_time = time.perf_counter_ns()
    with log_handler:
        suggestions = list(autocompleter.suggest_matches(word))
        time_taken = time.perf_counter_ns() - start_time
        slow = time_taken > 100_000_000
        if slow:
            logger.error(f'Execution too slow: {time_taken}')
    return jsonify({
        'data': suggestions, 'execution_time_ns': time_taken,
        'is_slow': slow})
