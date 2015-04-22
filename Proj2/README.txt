



############################################################################################
##
##	COLUMBIA UNIVERSITY
##	ADVANCED DATABASE SYSTEMS - SPRING 2015 - PROF. GRAVANO - ASSIGNMENT 2
##	hs2807 Henrique Spyra Gubert
## 	sd2810 Shiyu Dong
##
##  
############################################################################################


List of all files submitted
############################################################################################

	- main.py
	- README.txt
   - transcript_infobox_bill_gates.txt
   - transcript_infobox_robert_downey_jr.txt
   - transcript_infobox_jackson.txt
   - transcript_infobox_nfl.txt
   - transcript_infobox_nba.txt
   - transcript_infobox_ny_knicks.txt
   - transcript_infobox_miami_heat.txt
	- transcript_question_google.txt
   - transcript_question_lord_of_the_rings.txt
	- transcript_question_microsoft.txt
	- transcript_question_romeo_and_juliet.txt


How to run the program
############################################################################################

Go to the directory where the main.py file is and run:

   python main.py -key <Freebase API key> -q <query> -t <infobox/question>

An example using my Freebase api key (please keep it safe):

   python main.py -key AIzaSyAWQYMpX5fPyqOfSPvfssjNY0ogbvBdyg8 -q "Bill Gates" -t infobox
	python main.py -key AIzaSyAWQYMpX5fPyqOfSPvfssjNY0ogbvBdyg8 -q "Who created Microsoft?" -t question


INFOBOX - Solution General Structure
############################################################################################

1)Send a freebase search request and store return 'result' in a result list.

2)Iterate over the result list, for each result, select its 'mid' and use it to send a freebase topic request.

3)For each topic_json return, examine all its types, if it satisfied the condition that it has at least one out of the nine given interesting types, stop the iteration and use the topic_json as the input to display_infobox() function.

4)The display_infobox() function together with print_separator(), print_secondary_separator and print_centralized_text will print
out a well-formatted information box for the chosen topic_json.

QUESTION ANSWERING - Solution General Structure
############################################################################################

   1) Receive a query q and try to match it with the pattern "Who created [X]?". If the query does not match this pattern or [X] is nothing, dismiss the query like in the reference implementation (print "Wrong query!!!" and finish execution)

   2) Query Freebase MQL API (https://developers.google.com/freebase/v1/mqlread) for all creators (authors or businesspeople) of entities (books or organizations, respectively) that contain [X] as a substring of their names. Select only the creators that relate to [X] through the relations "is author" or "is founder". We will only answer cases where [X] is either a book title or organization. See example of the MQL if [X] = Microsoft. The first query is to get authors of books, the second to get founders:

      QUERY 1 (authors):
      [{
        "/book/author/works_written": [{
          "name": null,
          "name~=": "microsoft"
        }],
        "id": null,
        "name": null,
        "type": "/book/author",
        "sort": "name"
      }]

      QUERY 2 (founders):
      [{
        "/organization/organization_founder/organizations_founded": [{
          "name": null,
          "name~=": "microsoft"
        }],
        "id": null,
        "name": null,
        "type": "/organization/organization_founder",
        "sort": "name"
      }]      

   3) Generate an output of the format: "Bill Gates (as BusinessPerson) created <Microsoft Corporation> and <Microsoft Research>". With one of those statements per line. There should be one line for each combination of creator/role. All the lines are sorted by the creator name.
