###################################
# CS B551 Fall 2016, Assignment #3
#
# Your names and user ids:
#
# (Based on skeleton code by D. Crandall)
#
#
####
# Put your report here!!
####

import random
import math
from collections import Counter
from collections import defaultdict


# We've set up a suggested code structure, but feel free to change it. Just
# make sure your code still works with the label.py and pos_scorer.py code
# that we've supplied.
#
class Solver:
    tokTags = defaultdict(Counter)
    tags = Counter()
    tagTags = defaultdict(Counter)
    tagTagTags = defaultdict()
    tagCount = 0
    iv = Counter()

    # Calculate the log of the posterior probability of a given sentence
    #  with a given part-of-speech labeling
    # TODO: THis is P(Sentence/POS tags)
    def posterior(self, sentence, label):
        return 0  # TODO: Find the Log of the posterior probability


    # Do the training!
    #
    def train(self, data):

        for tup in data:

            words = tup[0]
            pos_tags = tup[1]
            self.tagCount += len(pos_tags)
            for i in range(len(words)):
                self.tokTags[words[i]][pos_tags[i]] += 1
                self.tags[pos_tags[i]] += 1
            self.iv[pos_tags[0]] += 1
            for j in range(1, len(pos_tags)):
                self.tagTags[pos_tags[j]][pos_tags[j - 1]] += 1
            for k in range(2, len(pos_tags)):
                tag = pos_tags[k]
                prev_tag = pos_tags[k - 1]
                prev_prev_tag = pos_tags[k - 2]
                if tag not in self.tagTagTags:
                    temp_ctr = Counter()
                    temp_ctr[prev_prev_tag] += 1
                    self.tagTagTags[tag] = {prev_tag: temp_ctr}
                    continue
                elif prev_tag not in self.tagTagTags[tag]:
                    temp_ctr = Counter()
                    temp_ctr[prev_prev_tag] += 1
                    self.tagTagTags[tag][prev_tag] = temp_ctr
                    continue

                self.tagTagTags[tag][prev_tag][prev_prev_tag] += 1

        return True

    def bayes_law(self, b_a, a, b):
        return (b_a * a) / b

    def get_simplified_tag_prob(self, word):
        if word not in self.tokTags:
            return "noun", 0
        counter = self.tokTags[word]
        max_tag = counter.most_common(1)[0][0]
        word_tag = float(counter[max_tag]) / sum(counter.values())
        prob_tag = float(self.tags[max_tag]) / self.tagCount
        tag_given_word = self.bayes_law(word_tag, 1, 1)  # TODO Figure out prob_tag

        return max_tag, tag_given_word

    # Functions for each algorithm.
    #
    def simplified(self, sentence):
        tag_list = []
        prob_list = []
        for word in sentence:
            tag, prob = self.get_simplified_tag_prob(word)
            tag_list.append(tag)
            prob_list.append(prob)

        return [[tag_list], [prob_list]]

    def find_log_prob(self, count, total):

        try:
            return math.log(float(count) / total)
        except Exception:
            print("Count: %d, Total: %d, count/total = %d" % (count, total, count / total))
            return 0

    def find_max_prob(self, data, index, sentence):
        try:
            counter = data[index]
            return counter.most_common(1)[0]
        except Exception:
            print(sentence[index])
            return False

    def assign_uniform_emission_prob(self, word):
        counter = Counter()
        # for tag in self.tagTags:
        #    counter[tag] += 1
        counter["noun"] += 1
        self.tokTags[word] = counter

    def hmm(self, sentence):
        v = defaultdict(Counter)
        start_word = sentence[0]

        if start_word not in self.tokTags:
            self.assign_uniform_emission_prob(start_word)

        start_word_count = sum(self.tokTags[start_word].values())
        s_prob_count = sum(self.iv.values())

        for tag in self.tokTags[start_word].keys():
            v[0][tag] = self.find_log_prob(self.tokTags[start_word][tag], start_word_count) + self.find_log_prob(
                self.iv[tag], s_prob_count)
        for i in range(1, len(sentence)):
            word = sentence[i]
            if word not in self.tokTags:
                self.assign_uniform_emission_prob(word)
            word_count = sum(self.tokTags[word].values())
            for tag in self.tokTags[word].keys():
                v[i][tag] = self.find_log_prob(self.tokTags[word][tag], word_count) + \
                            self.find_max_prob(v, i - 1, sentence)[1]

        tag_list = [v[j].most_common(1)[0][0] for j in range(len(sentence))]

        return [[tag_list], []]
        # return [ [ [ "noun" ] * len(sentence)], [] ]

    def complex(self, sentence):
        return [[["noun"] * len(sentence)], [[0] * len(sentence), ]]

    # This solve() method is called by label.py, so you should keep the interface the
    #  same, but you can change the code itself. 
    # It's supposed to return a list with two elements:
    #
    #  - The first element is a list of part-of-speech labelings of the sentence.
    #    Each of these is a list, one part of speech per word of the sentence.
    #
    #  - The second element is a list of probabilities, one per word. This is
    #    only needed for simplified() and complex() and is the marginal probability for each word.
    #
    def solve(self, algo, sentence):
        if algo == "Simplified":
            return self.simplified(sentence)
        elif algo == "HMM":
            return self.hmm(sentence)
        elif algo == "Complex":
            return self.complex(sentence)
        else:
            print "Unknown algo!"
