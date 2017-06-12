#library imports
import json
import math
from nltk.sentiment.vader import SentimentIntensityAnalyzer

#functions
from functions.base import mean

class classification:
	
	def __init__(self, setup):
		self.setup = setup

	def classify(self):
		if self.setup.lexicon in [1, 2]:
			self.potts_lexicon_classifier()
		elif self.setup.lexicon == 3:
			self.opinion_lexicon_classifier()
		elif self.setup.lexicon in [4, 5]:
			self.swn_lexicon_classifier()
		elif self.setup.lexicon == 6:
			self.vader_lexicon_classifier()

	def potts_lexicon_classifier(self): #potts = potts-lexicon based classifier
		
		classified_data = {}

		with open(self.setup.file_tokenized, 'r') as f:
			data = json.load(f)
			for review in sorted(data):
				word_list = []
				#print(nltk.help.upenn_tagset()) #in order to make the right conventions
				for word in sorted(data[review]['Tags']): #this whole for loop is due to the position tagging of senti_synsets, which is not important for us
					if word[1] in ['JJ', 'JJS', 'JJR']: #convert tags to adjectives
						word_list.append(word[0]+'/a')
					elif word[1] in ['RB', 'RBR', 'RBS', 'RP', 'WRB']: #convert tags to match adverbs
						word_list.append(word[0]+'/r')
					elif word[1] in ['bi', 'tri']: #convert bigrams and trigrams to uniform - others
						word_list.append(word[0]+'/o')
				
				potts_sentiment, positive, negative = self.potts_lexicon(word_list, data[review]['Content'], data[review]['Ratings']['Overall'])

				if    potts_sentiment == 'positive':
					data[review]['Sentiment'] = 'positive'
				elif  potts_sentiment == 'negative':
					data[review]['Sentiment'] = 'negative'
				else:
					data[review]['Sentiment'] = 'neutral'	

				classified_data[review] = { 'Sentiment': data[review]['Sentiment'],
							    'Positive':  positive,
							    'Negative':  negative,
							    'Score': 	 positive+negative }

		with open(self.setup.file_classified, 'w') as f:
			classified = {}
			for review in sorted(classified_data):
				classified[review] = classified_data[review]

			json.dump(classified, f)

	def potts_lexicon(self, sentence_tokenized, content, overall):		
		with open(self.setup.file_lexicon, 'r') as f:
			data = json.load(f)
			pos_score = 0
			neg_score = 0
			a = 0
			b = 0

			assessed_keys = []
			pos_ass = []
			neg_ass = []
			#optimalization in computation_time, learned in the course search engines
			optimized = [sorted(sentence_tokenized), sorted(data.keys())]
			neg = 0
			pos = 0
			while True:
				try:
					if a not in assessed_keys:
						bi_tri = optimized[0][a].split('/')
						bi_tri_check = optimized[1][b].split('/')
						if bi_tri[1] == 'o':
							if bi_tri[0] == bi_tri_check[0]: 
								if data[optimized[1][b]]['NormedScore'] > 0:
									pos_score += data[optimized[1][b]]['NormedScore']
									pos_ass.append(a)
								elif data[optimized[1][b]]['NormedScore'] < 0:
									neg_score += data[optimized[1][b]]['NormedScore']
									neg_ass.append(a)
								assessed_keys.append(a)

						elif optimized[0][a] == optimized[1][b]:
							if data[optimized[1][b]]['NormedScore'] > 0:
								pos_score += data[optimized[1][b]]['NormedScore']
								pos_ass.append(a)
							elif data[optimized[1][b]]['NormedScore'] < 0:
								neg_score += data[optimized[1][b]]['NormedScore']
								neg_ass.append(a)
							assessed_keys.append(a)

					if optimized[0][a] <= optimized[1][b]:
						a += 1
					else:
						b += 1
				except IndexError:	
					break	
			score = pos_score+neg_score	
			#score = pos_score+neg_score
			if score > 0.5:
				return 'positive', pos_score, neg_score 
			elif score < -0.5:
				return 'negative', pos_score, neg_score 
			else:
				return 'neutral', pos_score, neg_score 
				
	def opinion_lexicon_classifier(self): #demo_liu_hu_lexicon

		classified_data = {}
		i = 0
		with open(self.setup.file_tokenized, 'r') as f:
			data = json.load(f)

			for review in sorted(data):
				liu_hu_sentiment, positive, negative = self.opinion_lexicon(data[review]['Tokens'], lh_file)

				if liu_hu_sentiment == 'positive':
					data[review]['Sentiment'] = 'positive'
				elif  liu_hu_sentiment == 'negative':
					data[review]['Sentiment'] = 'negative'
				else:
					data[review]['Sentiment'] = 'neutral'	

				classified_data[review] = { 'Sentiment': data[review]['Sentiment'],
							    'Positive':  positive,
							    'Negative':  negative,
							    'Score': 	 positive-negative }

		with open(self.setup.file_classified, 'w') as f:
			classified = {}
			for review in sorted(classified_data):
				classified[review] = classified_data[review]

			json.dump(classified, f)	

	def opinion_lexicon(self, sentence_tokenized, lh_file):
		with open(self.setup.file_lexicon, 'r') as f:
			data = json.load(f)
			pos_words = 0
			neg_words = 0
			y = []

			a = 0
			b = 0
			c = 0

			assessed_keys = []
			#optimalization in computation_time, learned in the course search engines
			optimized = [sorted(sentence_tokenized), sorted(data['positive']), sorted(data['negative'])]
		
			while True:
				try:
					if a not in assessed_keys:
						if optimized[0][a] == optimized[1][b]:
							pos_words += 1
							y.append(1) # positive
							assessed_keys.append(a)
						elif optimized[0][a] == optimized[2][c]:
							neg_words += 1
							y.append(-1) # negative
							assessed_keys.append(a)
						else:
							y.append(0) # neutral
					
					#print(assessed_keys)

					if optimized[0][a] <= optimized[1][b] and optimized[0][a] <= optimized[2][c]:
						a += 1
					elif optimized[1][b] <= optimized[0][a] and optimized[1][b] <= optimized[2][c]:
						b += 1
					else:
						c += 1

				except IndexError:	
					break	

			if pos_words > neg_words:
				return 'positive', pos_words, neg_words 
			elif pos_words < neg_words:
				return 'negative', pos_words, neg_words 
			elif pos_words == neg_words:
				return 'neutral', pos_words, neg_words 	

	def swn_lexicon_classifier(self): #SWN = SentiWordNet classifier
		classified_data = {}
		with open(self.setup.file_tokenized, 'r') as f:
			data = json.load(f)
			for review in sorted(data):
				word_list = []
				
				for word in sorted(data[review]['Tags']): #this whole for loop is due to the position tagging of senti_synsets, which is not important for us
					if word[1] in ['NNP', 'NNS']:
						word_list.append(word[0]+'.n')
					elif word[1] in ['VB', 'VBD', 'VBN']:
						word_list.append(word[0]+'.v')
					elif word[1] in ['JJ', 'JJS', 'JJR']: #convert tags to adjectives
						word_list.append(word[0]+'.a')
					#elif word[1] in []: #convert tags to adjective sattelites, not taggable
					#	word_list.append(word[0]+'.s')
					elif word[1] in ['RB', 'RBR', 'RBS', 'WRB']: #convert tags to match adverbs
						word_list.append(word[0]+'.r')
				swn_sentiment, positive, negative = self.swn_lexicon(word_list, swn_file)

				if    swn_sentiment == 'positive':
					data[review]['Sentiment'] = 'positive'
				elif  swn_sentiment == 'negative':
					data[review]['Sentiment'] = 'negative'
				else:
					data[review]['Sentiment'] = 'neutral'	

				classified_data[review] = { 'Sentiment': data[review]['Sentiment'],
							    'Positive':  positive,
							    'Negative':  negative,
							    'Score': 	 positive-negative }

		with open(self.setup.file_classified, 'w') as f:
			classified = {}
			for review in sorted(classified_data):
				classified[review] = classified_data[review]

			json.dump(classified, f)

	def swn_lexicon(self, sentence_tokenized): #calculates the sentiment of the word based on SWN
		with open(self.setup.file_lexicon, 'r') as f:
			data = json.load(f)
			pos_score = 0
			neg_score = 0
			a = 0
			b = 0

			optimized = [sorted(sentence_tokenized), sorted(data.keys())]
			assessed_keys = []
			while True:
				try:
					if a not in assessed_keys:
						if optimized[0][a] == optimized[1][b]:
							pos_score += data[optimized[0][a]]['positive']
							neg_score += data[optimized[0][a]]['negative']
							assessed_keys.append(a)
					if optimized[0][a] <= optimized[1][b]:
						a += 1
					else:
						b += 1
				except IndexError:	
						break	

			score = pos_score-neg_score

			if score > 0:
				return 'positive', pos_score, neg_score 
			elif score < 0:
				return 'negative', pos_score, neg_score 
			else:
				return 'neutral', pos_score, neg_score 
	def vader_lexicon_classifier(self):
		sid = SentimentIntensityAnalyzer()
		classified_data = {}
		with open(self.setup.file_tokenized, 'r') as f:
			data = json.load(f)
			for review in sorted(data):
				content = data[review]['Content']
				ss = sid.polarity_scores(content)
				if ss['compound'] > 0:
					data[review]['Sentiment'] = 'positive'
				elif  ss['compound'] < 0:
					data[review]['Sentiment'] = 'negative'
				else:
					data[review]['Sentiment'] = 'neutral'	

				classified_data[review] = { 'Sentiment': data[review]['Sentiment'],
							    'Positive':  ss['pos'],
							    'Negative':	 ss['neg'],
							    'Score': 	 ss['compound'] }

		with open(self.setup.file_classified, 'w') as f:
			classified = {}
			for review in sorted(classified_data):
				classified[review] = classified_data[review]

			json.dump(classified, f)


	def find_word_pos_amounts(self, wanted_word): #just a random function to find the occurences of the word good
		
		classified_data = {}
		word_a = 0
		word_r = 0
		with open(self.setup.file_tokenized, 'r') as f:
			data = json.load(f)
			for review in sorted(data):
				word_list = []
				#print(nltk.help.upenn_tagset()) #in order to make the right conventions
				for word in sorted(data[review]['Tags']): #this whole for loop is due to the position tagging of senti_synsets, which is not important for us
					if word[0] == wanted_word:	
						if word[1] in ['JJ', 'JJS', 'JJR']: #convert tags to adjectives
							word_a += 1
						elif word[1] in ['RB', 'RBR', 'RBS', 'RP', 'WRB']: #convert tags to match adverbs
							word_r += 1
				
		print(word_a)
		print(word_r)

	