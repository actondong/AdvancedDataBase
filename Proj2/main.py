# -*- coding: utf-8 -*-

############################################################################################
############################################################################################
############################################################################################
##
##	COLUMBIA UNIVERSITY
##	ADVANCED DATABASE SYSTEMS - SPRING 2015 - PROF. GRAVANO - ASSIGNMENT 2
##	hs2807 Henrique Spyra Gubert
##  sd2810 Shiyu Dong
##  
##	How to run this code:
##	python main.py -key <Freebase API key> -q <query> -t <infobox/question>
##
##  Example:
##	python main.py -q Who created Microsoft? -t question
##
############################################################################################
############################################################################################
############################################################################################


# import urllib2
# import base64
# import sys
# import json
# import logging
# import nltk
# import heapq
# import pdb
# from collections import defaultdict
# from collections import deque

import argparse
import json
import urllib
import urllib2
import re
import sys
import json
import pdb

############################################################################################
## QUESTION ANSWERING
############################################################################################

DEFAULT_KEY = 'AIzaSyAWQYMpX5fPyqOfSPvfssjNY0ogbvBdyg8'
FREEBASE_MQL_URL = 'https://www.googleapis.com/freebase/v1/mqlread'
FREEBASE_SEARCH_URL = 'https://www.googleapis.com/freebase/v1/search'
FREEBASE_TOPIC_URL = 'https://www.googleapis.com/freebase/v1/topic'
QUESTION_PATTERN = "Who created (.+)\?"
CREATOR_CREATION_PAIRS = [
	('/book/author', '/book/author/works_written'), 
	('/organization/organization_founder', '/organization/organization_founder/organizations_founded')
]
I18N = {
	'/book/author': 'Author',
	'/organization/organization_founder': 'BusinessPerson'
}



def question_answering(key, query):
	# obtain entity name or substring X:
	match = re.match(QUESTION_PATTERN, query, re.IGNORECASE)
	if not match or len(match.group(1).strip()) == 0:
		print "Wrong question!!!"
		return


	# get tuples
	X = match.group(1).strip()
	creation_tuples = query_mql(key, X)

	# output
	counter = 0
	for creator, role, creations in creation_tuples:
		counter += 1
		output = ("%i. %s (as %s) created %s" % (counter, creator, role, list_to_sentence(creations)))
		print(output.encode(sys.stdout.encoding, errors='replace'))


# Converts a list of trings into a sentence joined by commas and an "and"
def list_to_sentence(phrases):
	if len(phrases) == 0:
		return ""
	elif len(phrases) == 1:
		return "<" + phrases[0] + ">"
	else:
		return ((("<" + ">, <".join(phrases[0:-1]) + ">")) + " and <" + phrases[-1] + ">")

# Query MQL API looking for authors and businesspeople that created something with the substring X
# Return tuples (creator_name, creator_role, [creation_names])
def query_mql(key, X):
	creation_tuples = []

	for creator_type, creation_type in CREATOR_CREATION_PAIRS:
		query = [{ 
			creation_type: [{
				"name": None,
				"name~=": X
			}],
			"id": None,
			"name": None,
			"type": creator_type,
			"sort": "name"
		}]
		params = { 
			'query': json.dumps(query),
			'key': key
		}
		url = FREEBASE_MQL_URL + '?' + urllib.urlencode(params)
		response = json.loads(urllib2.urlopen(url).read())

		for creator_data in response['result']:
			name = creator_data['name']
			role = I18N[creator_type]
			creations = []
			for creation_data in creator_data[creation_type]:
				creations.append(creation_data['name'])
			creation_tuples.append((name, role, creations))

	creation_tuples.sort()
	return creation_tuples

############################################################################################
## INFOBOX
############################################################################################

TYPE_ENTITY_MAPPING = {
	'/people/person': 'person',
	'/book/author': 'author',
	'/film/actor': 'actor',
	'/tv/tv_actor': 'actor',
	'/organization/organization_founder': 'business_person',
	'/business/board_member': 'business_person',
	'/sports/sports_league': 'league',
	'/sports/sports_team': 'sports_team',
	'/sports/professional_sports_team': 'sports_team'
}

ENTITY_ORDER = ['person', 'author', 'business_person', 'actor', 'league', 'sports_team']

FIELDS_TO_SHOW = {
	'person': [
		{"caption": "Name", "key": "/type/object/name"}, 
		{"caption": "Birthday", "key": "/people/person/date_of_birth"}, 
		{"caption": "Place of birth", "key": "/people/person/place_of_birth"}, 
		{"caption": "Description", "key": "/common/topic/description", "field":"value", "multiline":True},
		{"caption": "Sibling", "key": "/people/person/sibling_s", "property": "/people/sibling_relationship/sibling"},
		{"caption": "Spouses", "key": "/people/person/spouse_s", "property": "/people/marriage/spouse"},
		{"caption": "Death", "children": [
			{"caption": "Place", "key": "/people/deceased_person/place_of_death"}, 
			{"caption": "Date", "key": "/people/deceased_person/date_of_death"},
			{"caption": "Cause", "key": "/people/deceased_person/cause_of_death"}
		]}
	],
	'author':[
		{"caption": "Books", "key": "/book/author/works_written"},
		{"caption": "Books about", "key": "/book/book_subject/works"},
		{"caption": "Influenced", "key": "/influence/influence_node/influenced"},
		{"caption": "Influenced by", "key": "/influence/influence_node/influenced_by"},

	],
	'actor':[
		{"caption": "Films", "key":"/film/actor/film", "children": [
			{"caption": "Character", "property": "/film/performance/character"}, 
			{"caption": "Film name", "property": "/film/performance/film"}, 
		]},
	],
	'business_person':[
		{"caption": "Founded", "key": "/organization/organization_founder/organizations_founded"},
		{"caption": "Leadership", "key":"/business/board_member/leader_of", "children": [
			{"caption": "Organization", "property": "/organization/leadership/organization"}, 
			{"caption": "Role", "property": "/organization/leadership/role"}, 
			{"caption": "Title", "property": "/organization/leadership/title"}, 
			{"caption": "From", "property": "/organization/leadership/from"}, 
			{"caption": "To", "property": "/organization/leadership/to"}, 
		]},
		{"caption": "Board member", "key":"/business/board_member/organization_board_memberships", "children": [
			{"caption": "Organization", "property": "/organization/organization_board_membership/organization"}, 
			{"caption": "Role", "property": "/organization/organization_board_membership/role"}, 
			{"caption": "Title", "property": "/organization/organization_board_membership/title"}, 
			{"caption": "From", "property": "/organization/organization_board_membership/from"}, 
			{"caption": "To", "property": "/organization/organization_board_membership/to"}, 
		]}
	],
	'league':[
		{"caption": "Name", "key": "/type/object/name"}, 
		{"caption": "Sport", "key": "/sports/sports_league/sport"}, 
		{"caption": "Slogan", "key": "/organization/organization/slogan"}, 
		{"caption": "Offical website", "key": "/common/topic/official_website"}, 
		{"caption": "Championship", "key": "/sports/sports_league/championship"}, 
		{"caption": "Teams", "key": "/sports/sports_league/teams", "property":"/sports/sports_league_participation/team"},
		{"caption": "Description", "key": "/common/topic/description", "field":"value", "multiline":True},
	],
	'sports_team':[
		{"caption": "Name", "key": "/type/object/name"}, 
		{"caption": "Sport", "key": "/sports/sports_league/sport"},
		{"caption": "Arena", "key": "/sports/sports_team/arena_stadium"}, 
		{"caption": "Championships", "key": "/sports/sports_team/championships"},  
		{"caption": "Founded", "key": "/sports/sports_team/founded"},  
		{"caption": "Leagues", "key": "/sports/sports_team/league", "property":"/sports/sports_league_participation/league"},  
		{"caption": "Locations", "key": "/sports/sports_team/location"},  
		{"caption": "Coaches", "key":"/sports/sports_team/coaches", "children": [
			{"caption": "Name", "property": "/sports/sports_team_coach_tenure/coach"}, 
			{"caption": "Position", "property": "/sports/sports_team_coach_tenure/position"}, 
			{"caption": "From", "property": "/sports/sports_team_coach_tenure/from"}, 
			{"caption": "To", "property": "/sports/sports_team_coach_tenure/to", "default":"now"}, 
		]},
		{"caption": "PlayersRoster", "key":"/sports/sports_team/roster", "children": [
			{"caption": "Name", "property": "/sports/sports_team_roster/player"}, 
			{"caption": "Position", "property": "/sports/sports_team_roster/position"}, 
			{"caption": "Number", "property": "/sports/sports_team_roster/number"}, 
			{"caption": "From", "property": "/sports/sports_team_roster/from"}, 
			{"caption": "To", "property": "/sports/sports_team_roster/to", "default":"now"}, 
		]},
		{"caption": "Description", "key": "/common/topic/description", "field":"value", "multiline":True},
	],
}

INFOBOX_WIDTH = 100


# IMPLEMENT INFOBOX CODE HERE
def infobox(key, query):
	# REPLACE TOPICS LOADED FROM FILE WITH ACTUAL ALGORITHM

	#with open('topics/bill_gates.topic.txt', 'rb') as fp:
	#with open('topics/tolkien.topic.txt', 'rb') as fp:
	#with open('topics/robert_downey_jr.topic.txt', 'rb') as fp:
	#with open('topics/nba.topic.txt', 'rb') as fp:
	params = { 
			'query': json.dumps(query),
			'key': key
		}
		
	url = FREEBASE_SEARCH_URL + '?' + urllib.urlencode(params)
	search_resp = json.loads(urllib2.urlopen(url).read())
	result_list = search_resp['result']#a list of all freebase json returns on given query
	
	params = { 
		'key': key
		}
	topic_type = []
	for obj in result_list:
		mid = obj['mid']
		url = FREEBASE_TOPIC_URL + mid + '?' + urllib.urlencode(params)
		topic_type = []#the list of all availabe types of a returned topic json
		topic_json = json.loads(urllib2.urlopen(url).read())
		topic_property = topic_json['property']
		type_obj = topic_property["/type/object/type"]#under property, key="/type/object/type" contains type info needed
		values_list = type_obj["values"]#under "/type/object/type", key = "values" is a list which contains type info needed
		for types in values_list:
			topic_type.append(types["id"])
		for t in topic_type:
			if t in TYPE_ENTITY_MAPPING:#if any one of 9 given interesting types showed in topic return, it is valid. 
				display_infobox(topic_json)
				sys.exit()		
#	with open('topics/ny_knicks.topic.txt', 'rb') as fp:
#		topic_json = json.load(fp)

# Helper methods for infobox printing
def print_separator():
	sys.stdout.write(" " + (INFOBOX_WIDTH-2) * "-" + " \n")

def print_secondary_separator(text_width):
	sys.stdout.write((("|%%%is" % (INFOBOX_WIDTH-2)) % (text_width*"-")) + " \n")

def print_centralized_text(text):
	blanks = INFOBOX_WIDTH - 2 - len(text)
	left_spacing = right_spacing = blanks / 2
	if blanks % 2 == 1:
		right_spacing += 1
	sys.stdout.write("|" + (left_spacing)*" " + text + (right_spacing)*" " + "|\n")

# Method that prints the infobox given the topic json (parsed json)
# This methods seems like a mess, but it is actually a well organized code, it is just awfully long 
# because we chose to keep all code in a single file (because it makes submission easier) and we didn't
# want to create tens of functions here.
#
# That being said this method is really complex, because its task is really complex. 
# Get ready for many nested loops.
def display_infobox(topic_json):
	# select only the property part
	topic_json = topic_json['property']

	# get entity high-level types
	high_level_types = []
	for type_object in topic_json["/type/object/type"]["values"]:
		entity_type = type_object['id']
		if entity_type in TYPE_ENTITY_MAPPING and TYPE_ENTITY_MAPPING[entity_type] not in high_level_types:
			high_level_types.append(TYPE_ENTITY_MAPPING[entity_type])
	
	if len(high_level_types) == 0:
		raise Exception("No high-level type identified")

	# display header
	print_separator()
	header_text = topic_json["/type/object/name"]['values'][0]["text"]
	header_text += "(" + ', '.join(high_level_types).upper() + ')'
	print_centralized_text(header_text)
	print_separator()

	# for each highlevel type we will iterate through the fields we want to show and their captions, so we find the longest caption
	max_caption_length = 0
	for high_level_type in high_level_types:
		for field_struct in FIELDS_TO_SHOW[high_level_type]:
			if len(field_struct['caption']) > max_caption_length:
				max_caption_length = len(field_struct['caption'])
				text_space = INFOBOX_WIDTH - max_caption_length - 5;

	# for each field, let's print it!
	for entity_type in ENTITY_ORDER:
		if entity_type not in high_level_types:
			continue
		high_level_type = entity_type

		for field_struct in FIELDS_TO_SHOW[high_level_type]:
			
			# if it is a shallow field
			if 'children' not in field_struct:
				# check if field exists
				if field_struct['key'] not in topic_json:
					continue

				# print one line per value, addind a caption to the first line
				values_json = topic_json[field_struct['key']]['values']
				for i in xrange(len(values_json)):
					# write left indented part (either with some text or whitespace)
					sys.stdout.write('| ')
					if i == 0:
						sys.stdout.write(('%%-%is ' % (max_caption_length+1)) % (field_struct['caption'] + ':'))
					else:
						sys.stdout.write(' ' * (max_caption_length+2))

					# get value (according to 'property' and 'field' configs)
					try:
						if 'property' in field_struct:
							if 'field' in field_struct:
								value = values_json[i]['property'][field_struct['property']]['values'][0][field_struct['field']]
							else:
								value = values_json[i]['property'][field_struct['property']]['values'][0]['text']
						else:   
							if 'field' in field_struct:
								value = values_json[i][field_struct['field']]
							else:
								value = values_json[i]['text']
					except Exception:
						value = ''

					# correct possible charmap errors 
					value = value.encode(sys.stdout.encoding, errors='replace')

					if 'multiline' not in field_struct or not field_struct['multiline']:
						# remove line breaks
						value = value.replace("\n",'')
						
						# if value does not fit, ellipsize it
						if len(value) > text_space:
							value = value[0:(text_space-3)] + '...'
						
						sys.stdout.write(('%%-%is|\n' % text_space) % value)
					
					else:
						# if it is multiline, start breaking the value by line break
						values = value.split('\n')

						first_paragraph = True
						for paragraph in values:
							# print spacing, unless it is the first line and first paragraph
							if i != 0 or not first_paragraph:
								sys.stdout.write('| ' + ' ' * (max_caption_length+2))
							first_paragraph = False

							# if paragraph fits, print it and go on to next paragraph
							if len(paragraph) <= text_space:
								sys.stdout.write(('%%-%is|\n' % text_space) % paragraph)
							else:
								# if does not fit, let's loop
								lines_remaining = (len(paragraph) / text_space) + 1
								for j in xrange(lines_remaining-1):
									sys.stdout.write('%s|\n' % paragraph[j*text_space:(j+1)*text_space])
									sys.stdout.write('| ' + ' ' * (max_caption_length+2))
								
								# print last line
								sys.stdout.write(('%%-%is|\n' % text_space) % paragraph[(lines_remaining-1)*text_space:])	

				# final separator
				print_separator()

			# if there are children, lets split our box equally.
			else:
				# check if any of the field exists
				if 'key' not in field_struct:
					any_exists = False
					for child_struct in field_struct['children']:
						if child_struct['key'] in topic_json:
							any_exists = True
							break
					if not any_exists:
						continue
				else:
					if field_struct['key'] not in topic_json:
						continue

				# print left indent part
				sys.stdout.write(('| %%-%is ' % (max_caption_length+1)) % (field_struct['caption'] + ':'))
				
				# calculate how much space there is for each child. Try to divide equaly and distribute extra space from left to right
				child_count = len(field_struct['children'])
				each_child_base_space = text_space / child_count
				child_spaces = [each_child_base_space-3] * child_count
				for i in xrange(each_child_base_space*child_count - text_space):
					child_spaces[i] += 1

				# print header
				for i in xrange(child_count):
					header = field_struct['children'][i]['caption']
					if len(header) > child_spaces[i]:
						header = header[0:child_spaces[i]-3] + '...'
					sys.stdout.write(('| %%-%is ' % child_spaces[i]) % header)
				sys.stdout.write(' |\n')
				print_secondary_separator(text_space)

				# if we are just printing a group (one line)
				if 'key' not in field_struct:
					sys.stdout.write('| ' + ' ' * (max_caption_length+2))
					for i in xrange(child_count):
						child_struct = field_struct['children'][i]
						sys.stdout.write('| ')

						# get value (according to 'property' and 'field' configs)
						if child_struct['key'] in topic_json:
							values_json = topic_json[child_struct['key']]['values']
							if len(values_json) > 0:
								if 'property' in child_struct:
									if 'field' in child_struct:
										value = values_json[0]['property'][child_struct['property']]['values'][0][child_struct['field']]
									else:
										value = values_json[0]['property'][child_struct['property']]['values'][0]['text']
								else:   
									if 'field' in child_struct:
										value = values_json[0][child_struct['field']]
									else:
										value = values_json[0]['text']
							else:
								value = ''
						else:
							value = ''

						if len(value) == 0 and 'default' in child_struct:
								value = child_struct['default']

						# correct possible charmap errors 
						value = value.encode(sys.stdout.encoding, errors='replace')

						if len(value) > child_spaces[i]:
							sys.stdout.write(value[0:child_spaces[i]-3] + '... ')
						else:
							sys.stdout.write(('%%-%is ' % child_spaces[i]) % value)

					sys.stdout.write('|\n')
					print_separator()

				# if we are printing a secondary table
				else:
					entries_json = topic_json[field_struct['key']]['values']
					for json_entry in entries_json:
						sys.stdout.write('| ' + ' ' * (max_caption_length+2))
						for i in xrange(child_count):
							child_struct = field_struct['children'][i]
							sys.stdout.write('| ')

							# get value (according to 'property' and 'field' configs)
							if child_struct['property'] in json_entry['property']:
								values_json = json_entry['property'][child_struct['property']]['values']
								if len(values_json) > 0:
									if 'field' in child_struct:
										value = values_json[0][child_struct['field']]
									else:
										value = values_json[0]['text']
								else:
									value = ''
							else:
								value = ''

							if len(value) == 0 and 'default' in child_struct:
								value = child_struct['default']

							# correct possible charmap errors 
							value = value.encode(sys.stdout.encoding, errors='replace')

							if len(value) > child_spaces[i]:
								sys.stdout.write(value[0:child_spaces[i]-3] + '... ')
							else:
								sys.stdout.write(('%%-%is ' % child_spaces[i]) % value)

						sys.stdout.write(' |\n')
					print_separator()

# Hook to run main() method
if __name__ == "__main__": 
	parser = argparse.ArgumentParser(description='Answers question of the format "Who created [X]?"')
	parser.add_argument('-key', default=DEFAULT_KEY, metavar='FREEBASE_API_KEY', help='Freebase API key')
	parser.add_argument('-q', required=True, metavar='QUERY', help='Query to be issued (between quotes if multiword)')
	parser.add_argument('-t', required=True, choices=['infobox', 'question'], metavar='ACTION', help='Action to be done with the query. Either "infobox" or "question"')

	arguments = parser.parse_args()

	if arguments.t.lower() == 'infobox':
		infobox(key=arguments.key, query=arguments.q)
	elif arguments.t.lower() == 'question':
		question_answering(key=arguments.key, query=arguments.q)

