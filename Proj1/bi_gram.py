import nltk
# the description_sentence_list is a list whose entry is the description of each bing return
def bi_gram_train(description_sentence_list):
	all_description=""
	for des in description_sentence_list:
		all_description+=des
	all_sentence=[]
	all_sentence = outitem.split('.'):#first split description into sentences.
	for sentence in all_sentence:
#		sentence_tokens.append(nltk.word_tokenize(sentence.strip()))
		uni_sentence_tokens.append(nltk.word_tokenize(outitem.strip()+ " STOP"))
		bi_sentence_tokens.append(nltk.word_tokenize("* "+outitem.strip()+" STOP")
		
				
				
				
#It looks like no necessary to consider "*" and "STOP" in our purpose
	uni_gram=[t for outitem in uni_sentence_tokens for item in outitem ]
	bi_gram=[t for outitem in bi_sentence_tokens for item in outitem]
	uni_c={}
	bi_c={}
	for item in uni_gram:
		try:
			uni_c[item]+=1
		except:
			uni_c[item]=1
	uni_c['*']=len(all_sentence)		
	for item in bi_gram:
		try:
			bi_c[(item)]+=1
		except:
			bi_c[(item)]=1
 	bi_p={}
	for bi in bi_gram:
		try bi_gram[]





