#library imports
import json
import csv
import copy
import random
from data.library.prettytable import PrettyTable
from nltk.tokenize import word_tokenize
import operator

#functions
from functions.base import mean
from functions.base import manual_annotation_list

class evaluation:
	
	def __init__(self, setup):
		self.setup = setup
			
	def classifier_score(self):
		with open(self.file_subset, 'r') as f:
			data = json.load(f)
		with open(self.file_classified , 'r') as f:
			classifier = json.load(f)

		text_sentiment = {	'positive': 0,
					'negative': 0,
					'neutral':  0}
		scores_sentiment = {	1: copy.deepcopy(text_sentiment),
					2: copy.deepcopy(text_sentiment),
					3: copy.deepcopy(text_sentiment),
					4: copy.deepcopy(text_sentiment),
					5: copy.deepcopy(text_sentiment)}


		judgement = { 	'agreements': 	 0,
				'disagreements': 0}

		i = 0 # debug counter
		for review in sorted(classifier):

			overall_score = float(data[review]['Ratings']['Overall'])
			
			#classifier_sentiment = classifier[review]['Sentiment']
			if classifier[review]['Score'] > 0.7:
				classifier_sentiment = 'positive'
			elif classifier[review]['Score'] < -0.7:
				classifier_sentiment = 'negative'
			else:
				classifier_sentiment = 'neutral'

			scores_sentiment[overall_score][classifier_sentiment] += 1
		
		return self.print_evaluation_classifier_score(classifier, scores_sentiment)
		
	def print_evaluation_classifier_score(self, classifier, scores_sentiment):
		i = 0

		message = 'EVALUATION\n'
		message += '-'*50 + '\n'		
		message += 'reviews	 	=	'+str(len(classifier)) + '\n'
		message += '-'*50 + '\n'	

		for sentiment in sorted(scores_sentiment):
			keys = ['']
			values = [sentiment]
			for key in sorted(scores_sentiment[sentiment]):
				keys.append(key)
				values.append(scores_sentiment[sentiment][key])
			if i < 1:
				t = PrettyTable(keys)
				
			t.add_row(values)
			i += 1
		
		message += str(t)
		return message

	def evaluate_documents(self):
		words_csv = self.setup.file_csv_analysis_word
		documents_csv = self.setup.file_csv_analysis_documents

		with open(self.setup.file_tokenized, 'r') as f:
			data = json.load(f)
		with open(self.setup.file_potts, 'r') as f:
			classifier = json.load(f)
		
		#get sentiment words
		positive_words = []
		negative_words = []
		for word_tag in classifier:
			word = word_tag.split('/')[0]
			if word not in positive_words and classifier[word_tag]['NormedScore'] > 0:
				positive_words.append(word)
			elif word not in negative_words and classifier[word_tag]['NormedScore'] < 0:
				negative_words.append(word)

		word_counts = {}
		word_review_counts = {}
		word_normed_score = {}
		word_is_sentiment = {}
		word_is_positive = {}
		word_is_negative = {}

		document_words_counts = {}
		document_sentiment_counts = {}
		document_positive_counts = {}
		document_negative_counts = {}
		contains_sentiment = {}

		#count all individual occurancies
		assessed_words = []
		nr = 0
		for review in data:
			review_words = []
			pos_words = []
			neg_words = []
			senti_words = []
			#print(data[review])
			for word in data[review]['Tokens']:	
				word_is_senti = False			
				if word in positive_words:
					word_is_positive[word] = 1
					pos_words.append(word)
					word_is_senti = True
				else:
					word_is_positive[word] = 0
				if word in negative_words:
					word_is_negative[word] = 1
					neg_words.append(word)
					word_is_senti = True
				else:
					word_is_negative[word] = 0
				if word_is_senti == True:
					word_is_sentiment[word] = 1
					senti_words.append(word)
				else:
					word_is_sentiment[word] = 0

				try: #get word count
					word_counts[word] += 1
				except KeyError:
					word_counts[word] = 1
				
				if word not in review_words: #get amount of documents of word
					try:
						word_review_counts[word] += 1
					except KeyError:
						word_review_counts[word] = 1
				review_words.append(word)
				assessed_words.append(word)
			#document properties
			document_words_counts[review] 		= len(review_words)
			document_sentiment_counts[review] 	= len(senti_words)
			document_positive_counts[review] 	= len(pos_words)
			document_negative_counts[review] 	= len(neg_words)
			
			if len(senti_words) > 0:
				contains_sentiment[review] = 1
			else:
				contains_sentiment[review] = 0

			nr += 1

			#print(document_words_counts[review], document_sentiment_counts[review], document_positive_counts[review], document_negative_counts[review], contains_sentiment[review])
		with open(self.setup.file_csv_analysis_word, "w") as csvfile:
			fieldnames_words = ['word', 'total_occurencies', 'document_occurencies', 'sentiment_word', 'word_is_positive', 'word_is_negative']
			writer_words = csv.DictWriter(csvfile, fieldnames=fieldnames_words)
			writer_words.writeheader()

			for word in sorted(word_is_sentiment): 
				row = {}
				row['word'] 			= word
				row['total_occurencies'] 	= word_counts[word]
				row['document_occurencies'] 	= word_review_counts[word]
				row['sentiment_word'] 		= word_is_sentiment[word]
				row['word_is_positive'] 	= word_is_positive[word]
				row['word_is_negative'] 	= word_is_negative[word]

				writer_words.writerow(row)
	
		with open(self.setup.file_csv_analysis_documents, "w") as csvfile:
			fieldnames_document = ['document', 'total_words', 'sentiment_words', 'contains_sentiment', 'positive_words', 'negative_words']
			writer_document = csv.DictWriter(csvfile, fieldnames=fieldnames_document)
			writer_document.writeheader()

			for review in sorted(data): 
				row = {}
				row['document'] 		= review
				row['total_words'] 		= document_words_counts[review]
				row['sentiment_words'] 		= document_sentiment_counts[review]
				row['contains_sentiment'] 	= contains_sentiment[review]
				row['positive_words'] 		= document_positive_counts[review]
				row['negative_words'] 		= document_negative_counts[review]

				writer_document.writerow(row)	
		
	def text_evaluation_most_common_words(self):
		with open(self.file_subset, 'r') as f:
			data = json.load(f)
		with open(self.file_classified, 'r') as f:
			classifier = json.load(f)

		classifier_words = []
		for word_tag in classifier:
			word = word_tag.split('/')[0]
			if word not in classifier_words and abs(classifier[word_tag]['NormedScore']) > 0:
				classifier_words.append(word)

		words = []
		for word in data:
			if word in classifier_words:
				words.append((word, data[word]))
			
		s = sorted(words, key=lambda x: x[1], reverse=True)
		
		message = 'EVALUATION\n'
		message += 'most informative sentiment words of the dataset\n'
		for word, count in s[:50]:
			message += word +'\t\t'+ str(count)+'\n'
		return message

	def text_evaluation_most_common_words(self):
		with open(self.file_subset, 'r') as f:
			data = json.load(f)
		with open(self.file_classified, 'r') as f:
			classifier = json.load(f)

		classifier_words = []
		for word_tag in classifier:
			word = word_tag.split('/')[0]
			if word not in classifier_words and abs(classifier[word_tag]['NormedScore']) > 0:
				classifier_words.append(word)

		words = []
		for word in data:
			if word not in stop_words_list():
				if word in classifier_words:
					words.append((word, data[word]))
			
		s = sorted(words, key=lambda x: x[1], reverse=True)
		
		message = 'EVALUATION\n'
		message += 'most informative sentiment words of the dataset\n'
		for word, count in s[:50]:
			message += word +'\t\t'+ str(count)+'\n'
		return message

	def export_to_csv(self):
		with open(self.setup.file_subset, 'r') as f:
			data = json.load(f)
		with open(self.setup.file_classified, 'r') as f:
			classifier = json.load(f)
		with open(self.setup.file_csv_export_data, "w") as csvfile:

			fieldnames = ['ID', 'text_sentiment', 'overall', 'service', 'rooms', 'value', 'cleanliness', 'sleep_quality', 'location', 'check_in', 'business_service']
			writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
			writer.writeheader()

			for review in sorted(classifier): #['Service', 'Rooms', 'Value', 'Cleanliness', 'Sleep Quality', 'Location', 'Overall', 'Check in / front desk', 'Business service (e.g., internet access)']
				row = {}
				row['ID'] = review
				row['text_sentiment'] = classifier[review]['Score']

				try:
					row['overall'] = data[review]['Ratings']['Overall']
				except KeyError: 
					row['overall'] = 'NA'
	
				try:
					row['service'] = data[review]['Ratings']['Service']
				except KeyError: 
					row['service'] = 'NA'

				try:
					row['rooms'] = data[review]['Ratings']['Rooms']
				except KeyError: 
					row['rooms'] = 'NA'	

				try:
					row['value'] = data[review]['Ratings']['Value']
				except KeyError: 
					row['value'] = 'NA'

				try:
					row['cleanliness'] = data[review]['Ratings']['Cleanliness']
				except KeyError: 
					row['cleanliness'] = 'NA'

				try:
					row['sleep_quality'] = data[review]['Ratings']['Sleep Quality']
				except KeyError: 
					row['sleep_quality'] = 'NA'

				try:
					row['location'] = data[review]['Ratings']['Location']
				except KeyError: 
					row['location'] = 'NA'

				try:
					row['check_in'] = data[review]['Ratings']['Check in / front desk']
				except KeyError: 
					row['check_in'] = 'NA'
			
				try:
					row['business_service'] = data[review]['Ratings']['Business service (e.g., internet access)']
				except KeyError: 
					row['business_service'] = 'NA'
				
				writer.writerow(row)			
		
	def manual_sentiment_annotation(self):
		with open(self.setup.file_subset, 'r') as f:
			data = json.load(f)
		with open(self.setup.file_classified, 'r') as f:
			classifier = json.load(f)
		with open(self.setup.file_csv_output, "w") as csvfile:

			ratings = []
			fieldnames = ['ID', 'text_sentiment', 'overall', 'text_content']
			writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
			writer.writeheader()
			
			score_1 = 0
			score_2 = 0
			score_3 = 0
			score_4 = 0
			score_5 = 0
			

			for review in classifier: 
				checker = False
				overall_score = int(float(data[review]['Ratings']['Overall']))
				if len(data[review]['Content']) < 300 and len(data[review]['Content']) > 150:
					if overall_score == 1 and score_1 < 20:
						checker = True
						score_1 += 1
					elif overall_score == 2 and score_2 < 20:
						checker = True
						score_2 += 1
					elif overall_score == 3 and score_3 < 20:
						checker = True
						score_3 += 1
					elif overall_score == 4 and score_4 < 20:
						checker = True
						score_4 += 1
					elif overall_score == 5 and score_5 < 20:
						checker = True
						score_5 += 1

				if checker is True:
					row = {}
					row['ID'] = review
					row['text_sentiment'] = classifier[review]['Score']

					try:
						row['overall'] = data[review]['Ratings']['Overall']
					except KeyError: 
						row['overall'] = 'NA'
	
					try:
						row['text_content'] = data[review]['Content']
					except KeyError: 
						row['text_content'] = 'NA'
				
					writer.writerow(row)	

	def export_base_to_csv(self):
		with open(self.setup.file_subset, 'r') as f:
			data = json.load(f)
		with open(self.setup.file_csv_output, "w") as csvfile:
			
			ratings = []
			fieldnames = ['ID', 'overall', 'service', 'rooms', 'value', 'cleanliness', 'sleep_quality', 'location', 'check_in', 'business_service']
			writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
			writer.writeheader()
			for review in sorted(data): #['Service', 'Rooms', 'Value', 'Cleanliness', 'Sleep Quality', 'Location', 'Overall', 'Check in / front desk', 'Business service (e.g., internet access)']

				row = {}
				row['ID'] = review

				try:
					row['overall'] = data[review]['Ratings']['Overall']
				except KeyError: 
					row['overall'] = 'NA'
	
				try:
					row['service'] = data[review]['Ratings']['Service']
				except KeyError: 
					row['service'] = 'NA'

				try:
					row['rooms'] = data[review]['Ratings']['Rooms']
				except KeyError: 
					row['rooms'] = 'NA'	

				try:
					row['value'] = data[review]['Ratings']['Value']
				except KeyError: 
					row['value'] = 'NA'

				try:
					row['cleanliness'] = data[review]['Ratings']['Cleanliness']
				except KeyError: 
					row['cleanliness'] = 'NA'

				try:
					row['sleep_quality'] = data[review]['Ratings']['Sleep Quality']
				except KeyError: 
					row['sleep_quality'] = 'NA'

				try:
					row['location'] = data[review]['Ratings']['Location']
				except KeyError: 
					row['location'] = 'NA'

				try:
					row['check_in'] = data[review]['Ratings']['Check in / front desk']
				except KeyError: 
					row['check_in'] = 'NA'
			
				try:
					row['business_service'] = data[review]['Ratings']['Business service (e.g., internet access)']
				except KeyError: 
					row['business_service'] = 'NA'
				
				writer.writerow(row)	

	def check_setup_accuracy(self): #setup accuracy
		with open(self.setup.file_classified, 'r') as f:
			tokenizer = json.load(f)


		with open(self.setup.file_csv_output_setup, "w") as csvfile:
			fieldnames = ['ID', self.setup.setup]
			writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
			writer.writeheader()
		
			for ID in manual_annotation_list():
				row = {}
				row['ID'] = ID
				row[self.setup.setup] = tokenizer[ID]['Score']


				writer.writerow(row)	


	def print_random_lexicon(self):
		with open(self.setup.file_potts, 'r') as f:
			classifier = json.load(f)
			
		keys =  list(sorted(classifier.keys()))
		random.seed(1)
		random.shuffle(keys)
		
		i = 0
		for word in keys:
			tag = word.split('/')[1]
			if classifier[word]['NormedScore'] > 0 and tag == 'a' and i < 5:
				print(word, round(classifier[word]['NormedScore'], 3))
				i += 1
		print('-'*20)
		i = 0
		for word in keys:
			tag = word.split('/')[1]
			if classifier[word]['NormedScore'] > 0 and tag == 'r' and i < 5:
				print(word, round(classifier[word]['NormedScore'], 3))
				i += 1
		print('-'*20)
		i = 0
		for word in keys:
			tag = word.split('/')[1]
			if classifier[word]['NormedScore'] < 0 and tag == 'a' and i < 5:
				print(word, round(classifier[word]['NormedScore'], 3))
				i += 1
		print('-'*20)
		i = 0
		for word in keys:
			tag = word.split('/')[1]
			if classifier[word]['NormedScore'] < 0 and tag == 'r' and i < 5:
				print(word, round(classifier[word]['NormedScore'], 3))
				i += 1

		for word in keys:
			tag = word.split('/')[1]
			if tag not in ['r', 'a']:
				print(word)

	def export_ratings_to_csv(self):
		with open(self.setup.file_raw_skewed, 'r') as f:
			data = json.load(f)
		print(self.setup.file_csv_export_data)
		with open(self.setup.file_csv_export_data, "w") as csvfile:

			fieldnames = ['ID','overall', 'service', 'rooms', 'value', 'cleanliness', 'sleep_quality', 'location', 'check_in', 'business_service']
			writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
			writer.writeheader()

			for review in sorted(data): #['Service', 'Rooms', 'Value', 'Cleanliness', 'Sleep Quality', 'Location', 'Overall', 'Check in / front desk', 'Business service (e.g., internet access)']
				row = {}
				row['ID'] = review

				try:
					row['overall'] = data[review]['Ratings']['Overall']
				except KeyError: 
					row['overall'] = 'NA'
	
				try:
					row['service'] = data[review]['Ratings']['Service']
				except KeyError: 
					row['service'] = 'NA'

				try:
					row['rooms'] = data[review]['Ratings']['Rooms']
				except KeyError: 
					row['rooms'] = 'NA'	

				try:
					row['value'] = data[review]['Ratings']['Value']
				except KeyError: 
					row['value'] = 'NA'

				try:
					row['cleanliness'] = data[review]['Ratings']['Cleanliness']
				except KeyError: 
					row['cleanliness'] = 'NA'

				try:
					row['sleep_quality'] = data[review]['Ratings']['Sleep Quality']
				except KeyError: 
					row['sleep_quality'] = 'NA'

				try:
					row['location'] = data[review]['Ratings']['Location']
				except KeyError: 
					row['location'] = 'NA'

				try:
					row['check_in'] = data[review]['Ratings']['Check in / front desk']
				except KeyError: 
					row['check_in'] = 'NA'
			
				try:
					row['business_service'] = data[review]['Ratings']['Business service (e.g., internet access)']
				except KeyError: 
					row['business_service'] = 'NA'
				
				writer.writerow(row)		