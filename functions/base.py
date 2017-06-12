import time
import string
import os

def mean(numbers):
	return float(sum(numbers)) / max(len(numbers), 1)

def function_start(function_name):
	start_time = time.time()
	return start_time, function_name

def function_end(function_name, start_time, f):
	computation_time = round(time.time() - start_time,2)

	message = 'FINALIZED FUNCTION: '+ function_name +" IN %s seconds: " % (computation_time) + '\n'
	f.write(message)
	print(message)


def eval_function(evaluation, tokenized_file, input_file):
	start_time, function_name = function_start('evaluate_classifier_'+input_file) #function(current_function_name)
	eval_function = evaluation.classifier_score(tokenized_file, input_file)
	time_function = function_end(function_name, start_time)
	return eval_function, time_function

def compile_information(amount, setup):
	message = 'BRIEF DESCRIPTION OF CURRENT RUN\n'
	message += '-'*50 + '\n'
	message += 'used features: 	'+setup + '\n'
	message += 'total reviews:	'+str(amount) + '\n'
	message +='-'*50 + '\n'
	return message

def manual_annotation_list():
	manual_annotation = ['UR48548484', 'UR126744672', 'UR122797817', 'UR122428850', 'UR34380371', 'UR107290253', 'UR124896783', 'UR57184426', 'UR122726595', 'UR120335387', 'UR118345938', 'UR52296834', 'UR128413279', 'UR92801247', 'UR110407634', 'UR8458696', 'UR123570928', 'UR125111409', 'UR5800986', 'UR45335038', 'UR104386448', 'UR51398564', 'UR120568153', 'UR101402565', 'UR113671689', 'UR128024132', 'UR47865723', 'UR124282926', 'UR124555629', 'UR54571881', 'UR120875894', 'UR66611831', 'UR51780807', 'UR128477268', 'UR122464187', 'UR121996464', 'UR14644898', 'UR119166447', 'UR123685723', 'UR69493203', 'UR16752643', 'UR21528922', 'UR100280621', 'UR103241698', 'UR121705276', 'UR5613417', 'UR73162645', 'UR103570734', 'UR64964203', 'UR16393533', 'UR39904164', 'UR77300063', 'UR87632850', 'UR66047662', 'UR61756723', 'UR21502556', 'UR117697727', 'UR124837159', 'UR80327275', 'UR51926025', 'UR28961723', 'UR60979347', 'UR121972837', 'UR12694983', 'UR121299243', 'UR81502495', 'UR126793768', 'UR100862956', 'UR6026101', 'UR107037283', 'UR52648599', 'UR101376777', 'UR51623122', 'UR129023823', 'UR122112732', 'UR62782999', 'UR44730622', 'UR28483754', 'UR47001177', 'UR6043556', 'UR49616885', 'UR122708807', 'UR47178785', 'UR92535285', 'UR66966267', 'UR7338505', 'UR95834947', 'UR39346821', 'UR120760873', 'UR121346586', 'UR60572898', 'UR122751869', 'UR120481131', 'UR124024811', 'UR7846823', 'UR124038162', 'UR35521339', 'UR13869057', 'UR83074599', 'UR111890440']
	return manual_annotation

def process_word(word):
	word = word.lower()
	if word == "n't":
		output_word = 'not'
	else:
		output_word = word
	#print(output_word, output_word.strip(string.punctuation))
	return output_word