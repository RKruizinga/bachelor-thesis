import os
import time
import sys

from classes.setup import setup
from classes.processing import processing
from classes.classification import classification
from classes.evaluation import evaluation

from functions.base import function_start
from functions.base import function_end
from functions.base import compile_information
import spacy


amount = sys.argv[1] #784425 = all
print(amount)
setup = setup(amount)

f = open(setup.file_program_output, 'w')
 
compile_info = compile_information(amount, setup.setup)
f.write(compile_info)

#processing step
proces = processing(setup)
#transform raw_data files to a suitable json format
if setup.MODULE_RAW_TO_JSON == True:
	start_time, function_name = function_start('raw_to_json') #function(current_function_name)
	proces.raw_to_json() 
	function_end(function_name, start_time, f)

if setup.MODULE_PROCESS == True:
	start_time, function_name = function_start('processing') #function(current_function_name)
	proces.process_lexicon()
	function_end(function_name, start_time, f)

if setup.MODULE_SUBSET == True:
	start_time, function_name = function_start('subset') #function(current_function_name)
	proces.subset() 
	function_end(function_name, start_time, f)
	
if setup.MODULE_TOKENIZATION == True:
	start_time, function_name = function_start('tokenization') #function(current_function_name)
	proces.tokenize() 
	function_end(function_name, start_time, f)

#classification step
classifier = classification(setup)

if setup.MODULE_CLASSIFICATION == True:
	start_time, function_name = function_start('classification')
	classifier.classify()
	function_end(function_name, start_time, f)

#evaluation step
evaluation = evaluation(setup)
if setup.MODULE_EVALUATION == True:
	start_time, function_name = function_start('export')
	evaluation.export_to_csv()
	function_end(function_name, start_time, f)

if setup.MODULE_DOCUMENT_EVALUATION == True:
	start_time, function_name = function_start('export_document_evaluation')
	evaluation.evaluate_documents()
	function_end(function_name, start_time, f)
	
if setup.MODULE_LEXICON_RANDOM == True:
	start_time, function_name = function_start('export_lexicon_random')
	evaluation.print_random_lexicon()
	function_end(function_name, start_time, f)

if setup.MODULE_WORD_ANALYZING == True:
	start_time, function_name = function_start('word analyzing')
	classifier.find_word_pos_amounts('good')
	function_end(function_name, start_time, f)

if setup.MODULE_ANALYZE_DOCUMENT == True:
	start_time, function_name = function_start('analyze documents')
	evaluation.evaluate_random_documents()
	function_end(function_name, start_time, f)

f.close() 
#resources: http://sentiment.christopherpotts.net/lexicons.html#relationships