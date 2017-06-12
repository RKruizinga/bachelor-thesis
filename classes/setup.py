##in this file, the user can configure the setup
import os
import time

class setup:
	def __init__(self, amount, manual_annotation = False, unskewed_data = True):
		self.amount = amount
		self.manual_annotation = manual_annotation #if we want to check the manually annotated data
		self.unskewed_data = unskewed_data
		self.current_date = time.strftime("%d%m%Y")
		self.current_time = time.strftime("%H%M%S")

		self.configure_setup()
		self.module_activation()
		self.directories()
		self.files()

		self.file_lexicon = self.select_lexicon()

	def module_activation(self):
		self.MODULE_RAW_TO_JSON = True
		self.MODULE_PROCESS = True
		self.MODULE_SUBSET = True
		self.MODULE_TOKENIZATION = True
		self.MODULE_CLASSIFICATION = True
		self.MODULE_EVALUATION = True
		self.MODULE_DOCUMENT_EVALUATION = True
		self.MODULE_LEXICON_RANDOM = False
		self.MODULE_WORD_ANALYZING = False

	def configure_setup(self):
		#l1 = Potts Lexicon
		#l2 = Potts Lexicon + WordNet
		#l3 = Liu Opinion Lexicon
		#l4 = SentiWordNet 3.0 Lexicon
		#l5 = SentiWordNet 3.0 Lexicon + WordNet
		#l6 = Vader Lexicon
		self.lexicon = 1 #default = 1
		lexicon_str = 'l' + str(self.lexicon)

		#t1 = Word Tokenizer
		#t2 = Treebank Tokenizer
		#t3 = RegExp Tokenizer
		#t4 = Whitespace Tokenizer
		#t5 = SpaCy tokenizer
		self.tokenizer = 1 #default = 1
		tokenizer_str = 't' + str(self.tokenizer)

		#f0 = none
		#f1 = Punctuation 
		#f2 = Punctuation + N-grams
		#f3 = N-grams
		self.features = 2 # default = 2
		features_str = 'f' + str(self.features)

		self.setup = lexicon_str + tokenizer_str + features_str
	
	def directories(self):
		self.dir_data = 'data/'
		self.dir_data_raw = self.dir_data + 'raw_data/' #all raw hotel review are in this directory
		self.dir_data_lexicons = self.dir_data + 'lexicons/' #the unprocessed lexicons
		self.dir_data_library = self.dir_data + 'library/' #library functions are in this directoryself.dir_data_subset = self.dir_data + str(self.amount) + '/' #the subdir for the subsetted data
		self.dir_data_subset = self.dir_data + str(self.amount) + '/' #the subdir for the subsetted data
		self.dir_data_subset_setup = self.dir_data + str(self.amount) + '/' + self.setup + '/' #subset + setup
		self.dir_data_program_output = self.dir_data_subset_setup + 'output/program/' #the standard output in text files
		self.dir_data_csv_output = self.dir_data_subset_setup + 'output/csv/' #the evaluation output in csv	
		self.dir_program_output_date = self.dir_data_program_output + self.current_date + '/'
		self.dir_csv_output_date = self.dir_data_csv_output + self.current_date + '/'

		all_paths = [	self.dir_data, self.dir_data_raw, self.dir_data_lexicons, self.dir_data_library, 
				self.dir_data_subset, self.dir_data_subset_setup,self.dir_data_program_output, 
				self.dir_data_csv_output, self.dir_program_output_date, self.dir_csv_output_date]

		self.path(all_paths) #make the path structure

	def files(self):
		self.file_raw = self.dir_data + 'all_reviews.json'
		self.file_raw_skewed = self.dir_data + 'all_reviews_skewed.json'
		self.file_subset = self.dir_data_subset + 'subset_reviews.json'
		self.file_tokenized = self.dir_data_subset_setup + 'tokenized.json'
		self.file_classified = self.dir_data_subset_setup + 'classified.json'
		self.file_csv_export_data =  self.dir_data_subset_setup + 'export.csv'
		
		self.file_program_output = self.dir_program_output_date + self.current_time + '.txt'
		self.file_csv_output = self.dir_csv_output_date + self.current_time + '.csv'
		self.file_csv_analysis_word = self.dir_csv_output_date + self.current_time + '_words.csv'
		self.file_csv_analysis_documents = self.dir_csv_output_date + self.current_time + '_documents.csv'

		#classifiers
		self.file_unprocessed_lexicon_potts = self.dir_data_lexicons + 'wn-asr-multilevel-assess.csv'
		self.file_potts = self.dir_data_subset_setup + 'potts.json'
		self.file_potts_wordnet = self.dir_data_subset_setup + 'potts_wordnet.json'
		self.file_swn = self.dir_data_subset_setup + 'swn.json'
		self.file_swn_wordnet = self.dir_data_subset_setup + 'swn_wordnet.json'
		self.file_opinion_lexicon = self.dir_data_subset_setup + 'opinion_lexicon.json'
		
	def path(self, paths):
		for path in paths:
			if not os.path.exists(path):
	 			os.makedirs(path)

	def select_lexicon(self):
		if self.lexicon == 1:
			return self.file_potts
		elif self.lexicon == 2:
			return self.file_potts_wordnet
		elif self.lexicon == 3:
			return self.file_opinion_lexicon
		elif self.lexicon == 4:
			return self.file_swn
		elif self.lexicon == 5:
			return self.file_swn_wordnet
		elif self.lexicon == 6:
			return 'vader_lexicon'

			