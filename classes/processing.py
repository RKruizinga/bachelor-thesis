#library imports
import json
import nltk
import spacy
import string
import random
import csv
from nltk.corpus import wordnet as wn
from nltk.corpus import opinion_lexicon as ol
from nltk.corpus import sentiwordnet as swn

from os import listdir

from classes.tokenization import tokenization

#functions
from functions.base import mean
from functions.base import manual_annotation_list
from functions.base import process_word

class processing:
	
	def __init__(self, setup):
		self.setup = setup
		self.tokenization = tokenization(self.setup.tokenizer, setup.features)	

	def raw_to_json(self):
		hotel_list_files = listdir(self.setup.dir_data_raw)
		review_info = {} 
		for hotel_file in hotel_list_files: 
			with open(self.setup.dir_data_raw + hotel_file) as data_file:    
				data = json.load(data_file)	

				for review in data['Reviews']:
					if len(review['Ratings']) >= 7: #atleast 7 aspects should be rated in the review
						if 'Title' in review: #so no errors occur
							review_info[review['ReviewID']] = { 'Ratings': 	review['Ratings'],
											    'Title': 	review['Title'],
											    'Content': 	review['Content']}

		with open(self.setup.file_raw, 'w') as review_information:
			json.dump(review_info, review_information)

	def check_json_size(self, file_path): #simple function to check the size of a JSON file
		with open(file_path, 'r') as f:
			data = json.load(f)
			print(len(data))	

	def check_raw_files(self):
		hotel_list_files = listdir(self.setup.dir_data_raw)
		reviews = []
		review_ratings = {	0: 0,
					1: 0,
					2: 0,
					3: 0,
					4: 0,
					5: 0} 

		for hotel_file in hotel_list_files: 
			with open(self.setup.dir_data_raw + hotel_file) as data_file:    
				data = json.load(data_file)
		
				for review in data['Reviews']:
					reviews.append(review['ReviewID'])
					review_ratings[int(float(review['Ratings']['Overall']))] += 1
		print(len(reviews))
		print(review_ratings)

	def check_file_function(self):
		hotel_list_files = listdir(self.setup.dir_data_raw)
		review_info = {} 

		for hotel_file in hotel_list_files: 
			with open(self.setup.dir_data_raw + hotel_file) as data_file:    
				data = json.load(data_file)
		
				for review in data['Reviews']:
					
					review_info[review['ReviewID']] = { 'Ratings': 	review['Ratings'] }

		with open(self.setup.file_raw_skewed, 'w') as review_information:
			json.dump(review_info, review_information)
	def subset(self):
		with open(self.setup.file_raw, 'r') as f: #open the raw file
			data = json.load(f)

		with open(self.setup.file_subset, 'w') as f:
			i = 0
			score_1 = 0
			score_2 = 0
			score_3 = 0
			score_4 = 0
			score_5 = 0
			subset = {}	

			if self.setup.manual_annotation == True:
				i = 0
				for review in manual_annotation_list(): #if the amount is 100, take the manual annotation list
					if review in data:					
						subset[review] = data[review]
			else:
				if self.setup.unskewed_data == True:
					self.setup.amount = self.setup.amount/5
					
					keys = list(sorted(data.keys()))
					random.seed(1)
					random.shuffle(keys)

					for review in keys:
						i += 1
						overall_score = int(float(data[review]['Ratings']['Overall']))
						if overall_score == 1 and score_1 < self.setup.amount:
							subset[review] = data[review]
							score_1 += 1						
						elif overall_score == 2 and score_2 < self.setup.amount:
							subset[review] = data[review]
							score_2 += 1
						elif overall_score == 3 and score_3 < self.setup.amount:
							subset[review] = data[review]
							score_3 += 1
						elif overall_score == 4 and score_4 < self.setup.amount:
							subset[review] = data[review]
							score_4 += 1
						elif overall_score == 5 and score_5 < self.setup.amount:
							subset[review] = data[review]
							score_5 += 1
				else:
					for review in data:
						if i < self.setup.amount:
							subset[review] = data[review]
							i += 1
			
			json.dump(subset, f)

	def tokenize(self):
		tokenized_data = {}

		with open(self.setup.file_subset, 'r') as f: #open subset file
			data = json.load(f)
			self.tokenization.set_data(data)
			i = 0
			for review in data:
				tokens, tags = self.tokenization.tokenize(review)

				tokenized_data[review] = {	'Ratings': 		data[review]['Ratings'],
								'Content':		data[review]['Content'],
								'Tokens':		tokens,
								'Tags':			tags}

		with open(self.setup.file_tokenized, 'w') as f: #open classified file
			tokenized = {}
			for review in sorted(tokenized_data):
				tokenized[review] = tokenized_data[review]
		
			json.dump(tokenized, f)

	def process_lexicon(self):
		if self.setup.lexicon in [1, 2]:
			self.potts_lexicon()
			if self.setup.lexicon == 2:
				self.expand_potts_lexicon()
		elif self.setup.lexicon == 3:
			self.opinion_lexicon()
		elif self.setup.lexicon in [4, 5]:
			self.swn_lexicon()
			if self.setup.lexicon == 5:
				self.expand_swn_lexicon()
		
	def potts_lexicon(self):
		lexicon_data = {}
		#add data from the regular resource
		with open(self.setup.file_unprocessed_lexicon_potts, 'rt') as csvfile:
			datareader = csv.reader(csvfile)
			next(datareader)
			for row in datareader:
				lexicon_data[row[0]] = { 'NormedScore': float(row[29]) }
		with open(self.setup.file_potts, 'w') as f:
			lexicon = {}
			for word in sorted(lexicon_data):
				lexicon[word] = lexicon_data[word]

			json.dump(lexicon, f)

	def expand_potts_lexicon(self):
		new_lexicon_data = {}
		#add data from the regular resource
		with open(self.setup.file_potts, 'rt') as f:
			data = json.load(f)
			
			for row in sorted(data):
				a = row.split('/')
				word = a[0]
				tag =  a[1]
				
				if tag == 'a':
					other_tag = 'r'
				elif tag == 'r':
					other_tag = 'a'

				checker = word+'/'+other_tag	
				no_tags_of_other_kind = False
				if checker in data:
					if abs(data[checker]['NormedScore']) > 0:
						no_tags_of_other_kind = True # since the other notation is also available in the base file, the program is not allowed to make synonyms for it
				
				if row not in new_lexicon_data:
					new_lexicon_data[row] = data[row] #make a new dict, since you can't change the old one
				if abs(data[row]['NormedScore']) > 0:
					for i,j in enumerate(wn.synsets(word, tag)):
						synset_name = j.name()
						synset_split = synset_name.split('.')
						if synset_split[1] == 's': #conversion, known by the use of wordNet
							synset_split[1] = 'a'
						for synonym in j.lemma_names():
							if no_tags_of_other_kind == False or (no_tags_of_other_kind == True and synset_split[1] == tag):
								synonym = synonym+'/'+synset_split[1]
								if synonym not in new_lexicon_data and synonym not in data: #this means that only the first occuring word will give the score to this new word
									new_lexicon_data[synonym] = {'NormedScore': data[row]['NormedScore']}

		with open(self.setup.file_potts_wordnet, 'w') as f:
			lexicon = {}
			for word in sorted(new_lexicon_data):
				lexicon[word] = new_lexicon_data[word]
		
			json.dump(lexicon, f)

	def swn_lexicon(self):
		lexicon_data = {}
		temp_lexicon = {}
		#add data from the regular resource
		synsets=swn.all_senti_synsets()
		for synset in synsets:
			
			synset_val = str(synset)
			synset_full = synset_val.strip('<').split(':')[0]
			synset_full = synset_full[:-3]
			synset_word = synset_full[:-2]
			synset_tag = synset_full[-1]			

			if synset_tag == 's': 
				synset_tag = 'a'
			if synset_full not in temp_lexicon: #even appends values without a sentiment rating, could be wrong
				temp_lexicon[synset_full] = {	'positive': [synset.pos_score()],
								'negative': [synset.neg_score()]}
			else:
				temp_lexicon[synset_full]['positive'].append(synset.pos_score())
				temp_lexicon[synset_full]['negative'].append(synset.neg_score())


		for word in temp_lexicon:
			if mean(temp_lexicon[word]['positive']) > 0 or mean(temp_lexicon[word]['negative']) > 0:
				lexicon_data[word] = {	'positive': mean(temp_lexicon[word]['positive']),
							'negative': mean(temp_lexicon[word]['negative'])}

		with open(self.setup.file_swn, 'w') as f:
			lexicon = {}
			for word in sorted(lexicon_data):
				lexicon[word] = lexicon_data[word]

			json.dump(lexicon, f)

	def expand_swn_lexicon(self):
		new_lexicon_data = {}
		#add data from the regular resource
		with open(self.setup.file_swn, 'rt') as f:
			data = json.load(f)
			
			for row in sorted(data):
				try:
					word = row[:-2]
					tag  = row[-1]
					
					synsets = wn.synsets(word, tag)
					if row not in new_lexicon_data:
						new_lexicon_data[row] = data[row]

					if data[row]['positive'] > 0 or data[row]['negative'] > 0:
						for synset in sorted(synsets):
							synset_name = synset.name()
							synset_split = synset_name.split('.')
						
							if synset_split[1] == 's': #conversion stuff, known in wordNet
								synset_split[1] = 'a'

							synonym = synset_split[0]+'.'+synset_split[1]
							if synonym not in new_lexicon_data: #this means that only the first occuring word will give the score to this new word
								new_lexicon_data[synonym] = {'positive': data[row]['positive'],	
											     'negative': data[row]['negative']}

					
				except KeyError:
					break
		
		with open(self.setup.file_swn_wordnet, 'w') as f:
			lexicon = {}
			for word in sorted(new_lexicon_data):
				lexicon[word] = new_lexicon_data[word]

			json.dump(lexicon, f)
				

	def opinion_lexicon(self):
		lexicon_data = {'positive': [],
				'negative': []}

		positive_words = ol.positive()
		for word in positive_words:
			lexicon_data['positive'].append(word)
		negative_words = ol.negative()
		for word in negative_words:
			lexicon_data['negative'].append(word)

		with open(self.setup.file_opinion_lexicon, 'w') as f:
			lexicon = {}
			for word in sorted(lexicon_data):
				lexicon[word] = lexicon_data[word]

			json.dump(lexicon, f)
