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

        return [[tag_list], []]

    def find_log_prob(self, count, total):

        try:
            return math.log(float(count) / total)
        except Exception:
            print("Count: %d, Total: %d, count/total = %d" % (count, total, count / total))
            return 0


    # def find_prob(self, count, total):
    #
    #     try:
    #         return math.log(float(count) / total)
    #     except Exception:
    #         print("Count: %d, Total: %d, count/total = %d" % (count, total, count / total))
    #         return 0

    def transition_probability(self,cur_tag,prev_tag):
        count_tag = self.tagTags[cur_tag][prev_tag]
        total_count = sum(self.tagTags[cur_tag].values())
        return float(count_tag)/total_count

    def find_max_prob_2(self,prev_tags,tag):
        prob_array = []
        for p_tag in prev_tags:
            prob = self.transition_probability(tag,p_tag)
            prob_array.append(prob)
        max_prob = max(prob_array)
        return prev_tags[prob_array.index(max_prob)], max_prob

    def find_max_prob(self, data, index, sentence):
        try:
            counter = data[index]
            return counter.most_common(1)[0]
        except Exception:
            print("There was an error in determining the max")
            print(sentence[index])
            return False

    def assign_unknown_emission_prob(self, word,prev_tag):
        counter = Counter()
        #for tag in self.tagTags:
        #       counter[tag] += 1
        for tag in self.tags.keys():
            mc = self.tagTags[tag].most_common(1)[0]
            mc_tag = mc[0]
            if mc_tag == prev_tag:
                counter[tag] = mc[1]

        if len(counter) == 0:
            counter["noun"] += 1
        new_ctr = Counter()
        prob_tag = counter.most_common(1)[0][0]
        new_ctr[prob_tag] += 1
        self.tokTags[word] = new_ctr

    def get_word_count(self,word):
        if word not in self.tokTags:
            return 1
        return sum(self.tokTags[word].values())

    def get_possible_tags(self,word):
        if word not in self.tokTags:
            return ["noun"]
        return self.tokTags[word].keys()

    def word_tag_count(self, word, tag):
        if word not in self.tokTags:
            return float(self.tags[tag])/self.tagCount
        return self.tokTags[word][tag]

    def find_prob(self,a,b):
        return float(a)/b

    def hmm(self, sentence):
        v = defaultdict(Counter)
        start_word = sentence[0]

        start_word_count = self.get_word_count(start_word)
        s_prob_count = sum(self.iv.values())

        possible_tags = self.get_possible_tags(start_word)
        for tag in possible_tags:
            v[0][tag] = self.find_prob(self.word_tag_count(start_word,tag), start_word_count) * self.find_prob(
                self.iv[tag], s_prob_count)
        # prev_max = v[0].most_common(1)[0][0]
        # tag_list = [prev_max]
        tag_link = []
        for i in range(1, len(sentence)):
            word = sentence[i]
            word_count = self.get_word_count(word)
            possible_tags = self.get_possible_tags(word)
            for tag in possible_tags:
                max_tag, prev_max = self.find_max_prob_2(v[i-1].keys(),tag)
                v[i][tag] = self.find_prob(self.word_tag_count(word,tag), word_count) * \
                            prev_max

            # tag_list.append(max_tag)

        tag_list = [v[j].most_common(1)[0][0] for j in range(len(sentence))]
        # prev = v[len(sentence)-1].most_common(1)[0][0]
        # tag_list = [prev]
        #
        # for j in range(len(sentence)-2,-1,-1):
        #     prev = self.find_max_prob_2(v[j].keys(),prev)[0]
        #     tag_list.insert(0,prev)

        return [[tag_list], []]
        # return [ [ [ "noun" ] * len(sentence)], [] ]

    def find_two_tag_max(self,data,index,tag):
        # t2 = self.find_max_prob(data,index-1,"")[0]
        # t1 = self.find_max_prob(data,index-2,"")[0]
        t2 = self.find_max_prob_2(data[index-1].keys(),tag)[0]
        t1 = self.find_max_prob_2(data[index-2].keys(),t2)[0]
        tag_count = self.tags[tag]
        if t2 not in self.tagTagTags[tag] or t1 not in self.tagTagTags[tag][t2]:
            return 0.00000000001
        # else:
        seq_tag_count = self.tagTagTags[tag][t2][t1]

        return float(seq_tag_count)/tag_count

    def complex(self, sentence):
        w = defaultdict(Counter)
        start_word = sentence[0]

        # if start_word not in self.tokTags:
        #     self.assign_unknown_emission_prob(start_word,self.iv.most_common(1)[0][0])
        #
        # start_word_count = sum(self.tokTags[start_word].values())

        start_word_count = self.get_word_count(start_word)
        s_prob_count = sum(self.iv.values())
        possible_tags = self.get_possible_tags(start_word)
        for tag in possible_tags:
            # w[0][tag] = self.find_log_prob(self.tokTags[start_word][tag], start_word_count) + self.find_log_prob(
            #     self.iv[tag], s_prob_count)
            w[0][tag] = self.find_prob(self.word_tag_count(start_word,tag),start_word_count) * self.find_prob(self.iv[tag],s_prob_count)

        prev_max = w[0].most_common(1)[0]#self.find_max_prob(w, 0, sentence)

        if len(sentence) < 2:
            return [[[prev_max[0]]],[[0]]]
        second_word = sentence[1]
        #second_word_count = sum(self.tokTags[second_word].values())
        second_word_count = self.get_word_count(second_word)
        possible_tags = self.get_possible_tags(second_word)
        for tag in possible_tags:
            # w[1][tag] = self.find_log_prob(self.tokTags[second_word][tag], second_word_count) + \
            #                 prev_max[1]
            prev_tag,prev_prob = self.find_max_prob_2(w[0].keys(),tag)
            w[1][tag] = self.find_prob(self.word_tag_count(second_word,tag),second_word_count) * prev_prob

        for i in range(2,len(sentence)):
            word = sentence[i]
            # if word not in self.tokTags:
            #     self.assign_unknown_emission_prob(word,self.iv.most_common(1)[0][0])
            # word_count = sum(self.tokTags[word].values())
            word_count = self.get_word_count(word)
            possible_tags = self.get_possible_tags(word)
            for tag in possible_tags:
                # w[i][tag] = self.find_log_prob(self.tokTags[word][tag], word_count) + self.find_two_tag_max(w,i,tag)
                w[i][tag] = self.find_prob(self.word_tag_count(word,tag),word_count) * self.find_two_tag_max(w,i,tag)
        tag_list = [w[j].most_common(1)[0][0] for j in range(len(sentence))]


        return [[tag_list], [[0] * len(sentence), ]]

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
