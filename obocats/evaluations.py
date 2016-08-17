# !/usr/bin/python3
import numpy as np


def rank_freq(vocab_index):
    word_freq_dict = {word: len(id_set) for word, id_set in vocab_index.items()}
    lables, values = zip(*word_freq_dict.items())

    indsort = np.argsort(values)[::-1]