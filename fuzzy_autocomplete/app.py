import sys
import time

from flask import Flask, jsonify, request
import logbook

from .core import Autocompleter


logbook.StreamHandler(sys.stderr).push_application()
autocompleter = Autocompleter()
app = Flask(__name__)


@app.route('/search/')
def search():
    word = request.args.get('word')
    if not word:
        return jsonify({'data': [], 'execution_time_ns': 0})
    start_time = time.perf_counter_ns()
    suggestions = list(autocompleter.suggest_matches(word))
    time_taken = time.perf_counter_ns() - start_time
    slow = time_taken > 100000
    return jsonify({
        'data': suggestions, 'execution_time_ns': time_taken,
        'is_slow': slow})
