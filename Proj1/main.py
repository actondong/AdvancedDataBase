# -*- coding: utf-8 -*-

############################################################################################
############################################################################################
############################################################################################
##
##	COLUMBIA UNIVERSITY
##	ADVANCED DATABASE SYSTEMS - SPRING 2015 - PROF. GRAVANO - ASSIGNMENT 1
##	hs2807 Henrique Spyra Gubert
##  sd2810 Shiyu Dong
##
##	Getting started:
##		- Create your bing search api account in http://datamarket.azure.com/dataset/bing/search
##		- issue command:
##			python main.py <your_bing_api_key> 0.9 gates
##
##	Getting finished:
##		- Implement method computeNewQuery and chill out because the assignment is finished
##  
############################################################################################
############################################################################################
############################################################################################
from __future__ import division 
import urllib2
import base64
import sys
import json
import logging
import doc_vector as dv
import urllib
from bs4 import BeautifulSoup
from collections import Counter ,deque, defaultdict



BING_URL = 'https://api.datamarket.azure.com/Bing/Search/Web?Query=%%27%s%%27&$top=10&$format=json'

def main(argv):
	if len(argv[1:]) != 3 :
		raise ValueError('Need 3 arguments: <bing account key> <precision> <query>')

	# unpack parameters
	account_key = argv[1]
	target_precision = float(argv[2])
	query = [argv[3].lower()]

	# setup transcript logging
	logging.basicConfig(filename='transcript.txt', format='%(message)s', level=logging.INFO)

	# main loop
	round_num = 0
	while True:
		round_num += 1

		# execute query
		results = query_bing(account_key, target_precision, query)

		# if query returned less than 10 results, stop now
		if len(results) != 10:
			raise RuntimeError('Query "%s" returned less than 10 results' % "+".join(query))

		# go over each result asking feedback
		print ""
		print "Bing Search Results:"
		print "======================"
		
		relevant_results = [] #results will be list of doc_token_vector
		irrelevant_results = []
		list_of_doctokens = []#list of tokens of a bing return(if all retrievable, it consists of <meta name="description">
			#<meta name="title"> and <meta name="keywords">)
		for i in xrange(len(results)):
			dv.get_docvector(results,i,list_of_doctokens)#process the result, retireve more info from the url and 
			#store return in list_of_doctokens
			print "Result %i" % (i+1)
			print "["
			print "    URL: " + results[i]["Url"]
			print "    Title: " + results[i]["Title"].encode(sys.stdout.encoding, errors='replace')
			print "    Summary: " + results[i]["Description"].encode(sys.stdout.encoding, errors='replace')
			print "]"
			input_success = False
			while not input_success:
				relevant_char = raw_input("Relevant (Y/N)? ").lower()
				if relevant_char == 'y':
				    relevant_results.append(list_of_doctokens[i])
				    input_success = True
				elif relevant_char == 'n':
				    irrelevant_results.append(list_of_doctokens[i])
				    input_success = True
				else:
					print "Invalid input, try again."

		precision = float(len(relevant_results))/10

		print '======================'
		print 'FEEDBACK SUMMARY'
		print 'Query: %s' % " ".join(query)
		print 'Precision: %s' % format(precision, '.1f')
		
		log_round(round_num, query, results, relevant_results, irrelevant_results, precision)

		# check if at least one document was relevant, else stop now
		if len(relevant_results) == 0:
			raise RuntimeError('No relevant results for query "%s"' % "+".join(query))

		# check if precision achieved target
		if precision > target_precision:
			break

		print 'Still below the desired precision of %s' % format(target_precision, '.1f')
		query = computeNewQuery(query, relevant_results, irrelevant_results) 

	print 'Desired precision reached, done'

def query_bing(account_key, target_precision, query):
	url = BING_URL % "+".join(query)

	print 'Parameters:'
	print 'Client key  = ' + account_key
	print 'Query       = ' + " ".join(query)
	print 'Precision   = ' + format(target_precision, '.1f')
	print 'URL: ' + BING_URL % "+".join(query)
	print 'Total no of results : 10'

	# run query
	headers = {'Authorization': 'Basic ' + base64.b64encode(account_key + ':' + account_key)}
	request = urllib2.Request(url, headers = headers)
	response = urllib2.urlopen(request)
	content = response.read()	

	# parse JSON into array of dicts, each one with three keys: "Title", "Description" and "Url"
	return parse_response_content(content)

def parse_response_content(content):
	json_parsed = json.loads(content)

	results = []
	for result in json_parsed["d"]["results"]:
		results.append(dict())
		results[-1]["Title"] = result["Title"]
		results[-1]["Description"] = result["Description"]
		results[-1]["Url"] = result["Url"]

	return results

def log_round(round_num, query, results, relevant_results, irrelevant_results, precision):
	logging.info('=====================================')
	logging.info('ROUND %i' % round_num)
	logging.info('QUERY %s' % " ".join(query))
	logging.info('')

	for i in xrange(len(results)):
		logging.info('')
		logging.info('Result %i' % (i+1))
		
		if results[i] in relevant_results:
			logging.info('Relevant: YES')
		else:
			logging.info('Relevant: NO')

		logging.info("[")
		logging.info("    URL: " + results[i]["Url"])
		logging.info("    Title: " + results[i]["Title"])
		logging.info("    Summary: " + results[i]["Description"])
		logging.info("]")

	logging.info('')	
	logging.info('PRECISION ' + format(precision, '.1f'))
	logging.info('')

# Method to compute 2 new words to be added to the query
# 	query: array of words. E.g. ['bill', 'gates', 'willian', 'microsoft']
# 	relevant results and irrelevant_results: arrays of dicts, each dict has keys 'Title', 'Url' and 'Description'
#
#	return: query array (array of strings) with no more than 2 extra words in respect to query. Feel free to reorder the array
def computeNewQuery(query, relevant_results, irrelevant_results):
	sum_results = relevant_results + irrelevant_results
	sum_results_one_list = [e for L in sum_results for e in L ]#combine two classes of results to make the collection/dic of words
	collection = sorted(list(set(sum_results_one_list)))
	irrelevant_df = [1 for term in collection]#init the container for irrelevant_df
	for i,term in enumerate(collection):
		for NRL in irrelevant_results:
			if term in NRL:
				irrelevant_df[i] += 1
		for RL in relevant_results:
			if term in RL:
				irrelevant_df[i] -= 0.1
	###Generate document vectors
	list_of_R_doc_vec = []
	list_of_NR_doc_vec = []
	tf_vec = [0 for i in collection]

	for RL in relevant_results:
		for term in RL:
			i = collection.index(term)
			tf_vec[i]+=1
		list_of_R_doc_vec.append([tf/nr_df for tf,nr_df in zip(tf_vec,irrelevant_df)])#tf/nr_df : term frequency divided by irrelevant documnet frequency,this could and should be modified to imporve.
		tf_vec = [0 for i in collection]
	for NRL in irrelevant_results:
		for term in NRL:
			i = collection.index(term)
			tf_vec[i]+=1
		list_of_NR_doc_vec.append([tf/(nr_df) for tf,nr_df in zip(tf_vec,irrelevant_df)])
		tf_vec = [0 for i in collection]
	goal_vec = [0 for i in collection]



	for R_doc_vec in list_of_R_doc_vec:
		beta_R_doc_vec = [0.75*n for n in R_doc_vec]#beta = 0.75
		goal_vec=[a+b for a,b in zip(goal_vec,beta_R_doc_vec)]
	for NR_doc_vec in list_of_NR_doc_vec:
		gamma_NR_doc_vec = [0.15*n for n in NR_doc_vec]#gamma = 0.15
		goal_vec=[a-b for a,b in zip(goal_vec,gamma_NR_doc_vec)]
	print goal_vec
	#shouldn't inlucde the same word more than once
	prevword = []
	for i,w in enumerate(query):
		previndex = collection.index(query[i])#record which word occured before
		goal_vec[previndex] = 0#change their score to zero to prevent from selecting again
	new_word_index = goal_vec.index(max(goal_vec))
	if type(new_word_index) == int:
		new_word_index2 = goal_vec.index(max([i for i in goal_vec if i != max(goal_vec)]))
		word1 = collection[new_word_index]
		if type(new_word_index2) == int:
			word2 = collection[new_word_index2]
		else:
			word2 = collection[new_word_index2[0]]
	else:
		word1 = collection[new_word_index[0]]
		word2 = collection[new_word_index[1]]
	query.append(word1)
	query.append(word2)
	print query
	#Take the order into account
	window_ridus=3
	pairs = defaultdict(int)
        for record in relevant_results:
			record_tokens = deque(record)
			record_tokens.extendleft(['*','*','*'])
			record_tokens.extend(['*','*','*'])
			for i,token in enumerate(record_tokens):
				if token not in query:
					continue
		
				window=[]
				for j in xrange(i-window_ridus,i+window_ridus+1):
					token_nearby = record_tokens[j]
					if token_nearby not in query or i == j:
						continue
					if i > j:
						pairs[(token_nearby,token)]+=1
					else:
						pairs[(token,token_nearby)]+=1


	
	pairs_score =[(score,pair[0],pair[1])for pair, score in  pairs.items()]
	pairs_score.sort(reverse=True)
	pair_word = []
	if pairs_score == None:
		return query
	for item in pairs_score:
		pair_word.extend([item[1],item[2]])
	pair_word = set(pair_word)	
	order_query = deque([pairs_score[0][1],pairs_score[0][2]])
 	word_single = [word for word in query if word not in pair_word]
 	for pair in pairs_score:
		if pair[1] in order_query and pair[2] not in order_query:
			order_query.append(pair[2])
		if pair[2] in order_query and pair[1] not in order_query:
			order_query.appendleft(pair[1])
		if pair[1] not in order_query and pair[2] not in order_query:
			order_query.extend([pair[1],pair[2]])
	order_query.extend(word_single)
	print order_query
	return list(order_query)




# Hook to run main() method
if __name__ == "__main__": main(sys.argv)

