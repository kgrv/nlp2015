import nltk
from nltk.corpus import stopwords
import numpy as np
from nltk.stem.porter import *
from bs4 import BeautifulSoup
import codecs
from timeit import default_timer as timer
import string


def preprocessing(inFile):

		start = timer()
		print "Preprocssing...."
		xdoc = codecs.open(inFile, 'r',	 errors='ignore')	 # , errors='replace'
		stops = stopwords.words("english")
		reviews, bag_of_w, max_number_s = extractallsentences(xdoc, stops)
		print "Max # of sentences %d" % max_number_s
		bag_of_w = list(set(bag_of_w))
		print "Length bag of words %d" % len(bag_of_w)
		end = timer()
		print "preprocessing time %s" % (end - start)

		start = timer()
		bag_of_w = filter(None, bag_of_w)
		bag_of_w = dict([(bag_of_w[i], i) for i in range(len(bag_of_w))])
		doc_words, docs_sentence_words = create_doc_word_matrix(reviews, bag_of_w, max_number_s)
		end = timer()
		print "create_doc_word_matrix time %s" % (end - start)

		return reviews, bag_of_w, doc_words, docs_sentence_words, max_number_s


def extractallsentences(xdoc, stops):
		
		stemmer = PorterStemmer()
		reviews = []
		punct = ['#', '/', '[', ']', '}', '--', ',', '-/', '+', '-', '((', '))', '0', '1', '2', '3', '4', '5', '6', '7', '8', '9']

		# parser = ET.XMLParser(encoding="utf-8")
		# tree = ET.parse(xdoc, parser=parser)
		tree = BeautifulSoup(xdoc, "xml")

		# assuming file has <data> ... </data> as root tag, so must be added
		# because that was not included in the original files
		numOfReviews = 0
		start = timer()
		bag_of_w = []
		max_number_s = 0

		for review in tree.find_all("review_text"):
				reviewsentences_cleaned = []
				# for each review text: 1) split in sentences
				#																2) get rid of punctuations
				#																3) tokenize to words
				#																4) remove stop words
				reviewsentences = [nltk.word_tokenize(sent) for sent in nltk.sent_tokenize(review.text)]

				for sentence in reviewsentences:
						# get rid off stop words
						#sentence__clean = [stemmer.stem(word.lower().strip().strip(",.;:?!-#*[]()")) for word in sentence if (word not in stops and word not in punct)]
						#sentence__clean = [word.lower().strip().strip(",.;:?!-#*[]()") for word in sentence if (word not in stops and word not in punct)]
						sentence__clean = []
						for word in sentence:
								w = word.lower().strip().strip("',.;:?!-#*[]()")
								if w not in stops and w not in punct:
										sentence__clean.append(w)
	
						sentence__clean = filter(None, sentence__clean)
						for ww in sentence__clean:
								bag_of_w.append(ww)
						reviewsentences_cleaned.append(sentence__clean)

				if max_number_s < len(reviewsentences_cleaned):
						max_number_s = len(reviewsentences_cleaned)
				
				reviews.append(reviewsentences_cleaned)
				numOfReviews += 1
				# print "Number of reviews %d" % numOfReviews
		end = timer()

		print "review in tree.find_all %s" % (end - start)
		print "# of reviews %s" % numOfReviews
		return reviews, bag_of_w, max_number_s


def create_doc_word_matrix(docs, words, max_number_s):

		# vector that holds for each doc the word counts
		dw = np.zeros(len(words))
		# doc_words is a matrix of size "num of docs" X "num of words corpus"
		docs_words_m = np.zeros((len(docs), len(words)))
		docs_sentence_words = []

		print ("Creating doc word matrix...")
		# loop over reviews
		for m, r in enumerate(docs):
				# loop over sentences in review
				doc_sent = []
				for s_idx, s in enumerate(r):
						# loop over word in sentence
						# there were still '' empty symbols in sentences although I thought I filtered them already
						# above...strange
						s = filter(None, s)
						sent_words = []
						for wd in s:
								idx = words[wd]
								docs_words_m[m, idx] += 1
								sent_words.append(idx)
						doc_sent.append(sent_words)
				docs_sentence_words.append(doc_sent)

		# print docs_sentence_words
		print("Finished creating doc word matrix.")

		return docs_words_m, docs_sentence_words
