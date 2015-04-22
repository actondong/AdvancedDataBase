import urllib2
import urllib
from bs4 import BeautifulSoup
import nltk
from nltk.tokenize import RegexpTokenizer
import string
#inputs are bing return, number ID of that return, list_of_doctokens
#is a container, which has a list entry for each bing return.
def get_docvector(bing_result,result_counter,list_of_doctokens):
	i = result_counter
	URL = bing_result[i]["Url"]
	description= bing_result[i]["Description"]
	title = bing_result[i]["Title"]
	response = None
	try: 
		response = urllib2.urlopen(URL)
	except urllib2.HTTPError, e:
		print "forbidden, can't scrape the website"
	except urllib2.URLError, e:
		print "forbidden, can't scrape the website"
	except httplib.HTTPException, e:
		print "forbidden, can't scrape the website"

	lowres=""
	if response == None:
		translate_table = {ord(c): None for c in string.punctuation}#trans_table for pruning punctuation
		res = (description+title).translate(translate_table)
		for s in res:
			lowres += s.lower()
 		list_of_doctokens.append(nltk.word_tokenize(lowres))
 	else:#if html is retrievable,
		html = response.read()
		soup_obj = BeautifulSoup(html)
		if soup_obj.find("meta",{"name":"keywords"}) != None:
			keywords = soup_obj.find("meta",{"name":"keywords"})['content']
			print("scrape key words")
			print keywords
			translate_table = {ord(c): None for c in string.punctuation}
			res = (keywords+description+title).translate(translate_table)
			for s in res:
				lowres += s.lower()
 			list_of_doctokens.append(nltk.word_tokenize(lowres))
 		else:#if "keywords" meta data exists,
 			translate_table = {ord(c): None for c in string.punctuation}
			res = (description+title).translate(translate_table)
			for s in res:
				lowres += s.lower()
 			list_of_doctokens.append(nltk.word_tokenize(lowres))

if __name__ == "__main__":
	main()
