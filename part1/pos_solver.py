###################################
# CS B551 Fall 2016, Assignment #3
#
#
# Anup Bharadwaj
# Supreeth Prakash
# Raghuveer Krishnamurthy
#
# (Based on skeleton code by D. Crandall)
#
#
####
# Put your report here!!
####


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

    def get_simplified_tag_prob(self, word):
        if word not in self.tokTags:
            return "noun", 0
        counter = self.tokTags[word]
        max_tag = counter.most_common(1)[0][0]
        word_tag = self.find_prob(counter[max_tag], sum(counter.values()))

        return max_tag,word_tag

    # Functions for each algorithm.
    #
    def simplified(self, sentence):
        tag_list = []
        prob_list = []
        for word in sentence:
            tag, prob = self.get_simplified_tag_prob(word)
            tag_list.append(tag)
            prob_list.append(round(prob,3))


        return [[tag_list], [prob_list]]

    def find_log_prob(self, count, total):
        return math.log(float(count) / total)

    def transition_probability(self, cur_tag, prev_tag):
        count_tag = self.tagTags[cur_tag][prev_tag]
        total_count = sum(self.tagTags[cur_tag].values())
        # total_count = self.tags[prev_tag]
        return float(count_tag) / total_count

    def find_max_prob(self, prev_tags, tag):
        prob_array = []
        for p_tag in prev_tags:
            prob = self.transition_probability(tag, p_tag)
            prob_array.append(prob)
        max_prob = max(prob_array)
        return prev_tags[prob_array.index(max_prob)], max_prob

    def get_word_count(self, word):
        if word not in self.tokTags:
            return 1
        return sum(self.tokTags[word].values())

    def get_possible_tags(self, word):
        if word not in self.tokTags:
            return ['noun']  # self.tags.keys()
        return self.tokTags[word].keys()

    def word_tag_count(self, word, tag):
        if word not in self.tokTags:
            return float(self.tags[tag]) / self.tagCount
        return self.tokTags[word][tag]

    def find_prob(self, a, b):
        return float(a) / b

    def find_tag_prob(self, tag):
        return float(self.tags[tag]) / self.tagCount

    def emission_probability(self, word, tag):
        wt_count = self.word_tag_count(word, tag)
        wc = self.get_word_count(word)
        word_tag_prob = self.find_prob(wt_count, wc)
        # tag_prob = self.find_tag_prob(tag)

        return float(word_tag_prob)

    def hmm(self, sentence):
        v = defaultdict(Counter)

        start_word = sentence[0]
        s_prob_count = sum(self.iv.values())

        possible_tags = self.get_possible_tags(start_word)
        for tag in possible_tags:
            v[0][tag] = self.emission_probability(start_word, tag) * self.find_prob(self.iv[tag], s_prob_count)

        for i in range(1, len(sentence)):
            word = sentence[i]
            possible_tags = self.get_possible_tags(word)
            for tag in possible_tags:
                max_tag, prev_max = self.find_max_prob(v[i - 1].keys(), tag)
                v[i][tag] = self.emission_probability(word, tag) * prev_max

        tag_list = [v[j].most_common(1)[0][0] for j in range(len(sentence))]


        return [[tag_list], []]

    def find_two_tag_max(self, data, index, tag):
        t2 = self.find_max_prob(data[index - 1].keys(), tag)[0]
        t1 = self.find_max_prob(data[index - 2].keys(), t2)[0]

        tag_count = self.tags[tag]
        if t2 not in self.tagTagTags[tag] or t1 not in self.tagTagTags[tag][t2]:
            return float(self.tags[tag]) / self.tagCount  # 0.00000000001
        seq_tag_count = self.tagTagTags[tag][t2][t1]

        return self.find_prob(float(seq_tag_count), tag_count)

    def complex(self, sentence):
        w = defaultdict(Counter)
        start_word = sentence[0]
        s_prob_count = sum(self.iv.values())
        possible_tags = self.get_possible_tags(start_word)
        for tag in possible_tags:
            w[0][tag] = self.emission_probability(start_word,tag) * self.find_prob(self.iv[tag], s_prob_count)

        prev_max = w[0].most_common(1)[0]

        if len(sentence) < 2:
            return [[[prev_max[0]]], [[0]]]

        second_word = sentence[1]
        possible_tags = self.get_possible_tags(second_word)
        for tag in possible_tags:
            prev_tag, prev_prob = self.find_max_prob(w[0].keys(), tag)
            w[1][tag] = self.emission_probability(second_word,tag) * prev_prob

        for i in range(2, len(sentence)):
            word = sentence[i]
            possible_tags = self.get_possible_tags(word)
            for tag in possible_tags:
                w[i][tag] = self.emission_probability(word,tag) * self.find_two_tag_max(w, i, tag)

        tag_list = [w[j].most_common(1)[0][0] for j in range(len(sentence))]
        prob_list = [round(self.emission_probability(sentence[j], w[j].most_common(1)[0][0]),3) for j in range(len(sentence))]

        return [[tag_list], [prob_list]]

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
