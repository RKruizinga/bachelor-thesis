import nltk
from nltk.tokenize import treebank
from nltk.tokenize import word_tokenize
from nltk.tokenize import RegexpTokenizer
from nltk.tokenize import WhitespaceTokenizer

from functions.base import process_word

class tokenization:
	
	def __init__(self, tokenizer, features):
		self.tokenizer = tokenizer
		self.features = features
		if tokenizer == 5:
			self.nlp = spacy.load('en_default')

	def set_data(self, data):
		self.data = data

	def tokenize(self, review):

		if self.tokenizer == 1:
			tokens, tags = self.word_tokenizer(review)
		elif self.tokenizer == 2:
			tokens, tags = self.treebank_tokenizer(review)
		elif self.tokenizer == 3:
			tokens, tags = self.regexp_tokenizer(review)
		elif self.tokenizer == 4:
			tokens, tags = self.whitespace_tokenizer(review)
		elif self.tokenizer == 5:
			tokens, tags = self.spacy_tokenizer(review)

		return tokens, tags

	def word_tokenizer(self, review):
		if self.features in [1, 2]:
			tokens = [process_word(word.lower()) for word in word_tokenize(self.data[review]['Content'])]
		else: 
			tokens = [word.lower() for word in word_tokenize(self.data[review]['Content'])]

		tags = nltk.pos_tag(tokens)

		if self.features in [2, 3]:
			tags = self.ngrams(tokens, tags)

		return tokens, tags

	def treebank_tokenizer(self, review):
		tokenizer = treebank.TreebankWordTokenizer()
		if self.features in [1, 2]:
			tokens = [process_word(word.lower()) for word in tokenizer.tokenize(self.data[review]['Content'])]
		else: 
			tokens = [word.lower() for word in tokenizer.tokenize(self.data[review]['Content'])]

		tags = nltk.pos_tag(tokens)		
		
		if self.features in [2, 3]:
			tags = self.ngrams(tokens, tags)

		return tokens, tags

	def regexp_tokenizer(self, review):
		tokenizer = RegexpTokenizer(r'\w+') 
		if self.features in [1, 2]:
			tokens = [process_word(word.lower()) for word in tokenizer.tokenize(self.data[review]['Content'])]
		else: 
			tokens = [word.lower() for word in tokenizer.tokenize(self.data[review]['Content'])]

		tags = nltk.pos_tag(tokens)		
	
		if self.features in [2, 3]:
			tags = self.ngrams(tokens, tags)

		return tokens, tags

	def whitespace_tokenizer(self, review):
		tokenizer = WhitespaceTokenizer() 
		if self.features in [1, 2]:
			tokens = [process_word(word.lower()) for word in tokenizer.tokenize(self.data[review]['Content'])]
		else: 
			tokens = [word.lower() for word in tokenizer.tokenize(self.data[review]['Content'])]

		tags = nltk.pos_tag(tokens)

		return tokens, tags
	
	def spacy_tokenizer(self, review):
		tokens = []
		tags = []

		processed = self.nlp(self.data[review]['Content'])

		for word in processed:
			if self.features in [1, 2]:
				tokens.append(process_word(word.lower_))
				tags.append((process_word(word.lower_), word.tag_))
			else:
				tokens.append(word.lower_)
				tags.append((word.lower_, word.tag_))

		if self.features in [2, 3]:
			tags = self.ngrams(tokens, tags)

		return tokens, tags


	def ngrams(self, tokens, tags):
		x = 0
		trigrams = []
		while x < len(tokens) - 2:
			trigrams.append((tokens[x] +' '+ tokens[x+1] +' '+ tokens[x+2], 'tri'))
			x += 1
		y = 0
		bigrams = []
		while y < len(tokens) - 1:
			bigrams.append((tokens[y] +' '+ tokens[y+1], 'bi'))
			y += 1

		tags = tags + bigrams + trigrams

		return tags