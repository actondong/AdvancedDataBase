

############################################################################################
##
##	COLUMBIA UNIVERSITY
##	ADVANCED DATABASE SYSTEMS - SPRING 2015 - PROF. GRAVANO - ASSIGNMENT 3
##	hs2807 Henrique Spyra Gubert
## 	sd2810 Shiyu Dong
##
##  
############################################################################################



Dataset 1 - Department of Buildings (DOB) Complaints
######################################################

ABOUT THE DATASET
- Name: Department of Buildings (DOB) Complaints
- Around 500,000 complaints about buildings in NYC from 2012 to 2015
- https://data.cityofnewyork.us/Housing-Development/DOB-Complaints-Received/eabe-havv

ABOUT PREPROCESSING
- Select only columns "BIN" and "Complaint Category" (hide all the others), and order it by "BIN". Download the data as CSV.
- Create sets of "Complaint Category" per "BIN" (Building Identification Number).
- The code that does this preprocessing is in "DOB_preprocess.py" file, but you don't need to run that because we are providing the
file "DOB_integrated_dataset.csv" already, which is the preprocessing output.

HOW TO RUN
- How to run program for this dataset (minsup=.5%, minconf=50%):
	python main.py DOB_integrated_dataset.csv .005 .5

RESULTS
- You can find the results of the association rule mining in the file "DOB_output.txt"

ANALISYS
 - This dataset was relatively sparse, in the sense that usually one basket would have only a few items. This comes from the fact that buildings don't usually have many different problems at the same time (just a few like 1-5). Because of that the support chosen had to be relatively low (.5%)
 - Using this dataset only 3 rules were mined:
 	[04,83] => [05] (Conf: 69%, Supp: 0.5%)
		Meaning: Illegal After Hours Work + Construction Beyond Approved Plans => Missing Permit
	[86] => [05] (Conf: 68%, Supp: 0.9%)
		Meaning: Work Contrary to Stop Work Order => Missing Permit
	[45,83] => [05] (Conf: 65%, Supp: 0.5%)
		Meaning: Illegal Conversion + Construction Beyond Approved Plans => Missing Permit

CONCLUSION
- Since the rules obtained from the analisys of this dataset were few, we decided to try another dataset (see next section)



Dataset 2 - 311 Complaints
#############################

ABOUT THE DATASET
- Name: 311 Complaints
- Around 9,000,000 complaints about security, noise, street problems in NYC from 2010 to 2015.
- There are 222 different complaint types
- https://data.cityofnewyork.us/Social-Services/311-Service-Requests-from-2010-to-Present/erm2-nwe9
- These are the same complaints that can be viewed in the site: http://nyc-311.wegotdata.com/

ABOUT PREPROCESSING
- Select only columns "Created Date", "Complaint Type" and "Incident Zip"
- Create sets grouped by "Incident Zip" and day of creation (from jan-2010 to apr-2015), where the items are the "Complaint Types"
- Replace actual names of "Complaint Types" by integers. This reduced the output data file size from 392MB to 11MB. 
- In the preprocessing step we considered only complaints with zip code starting in 5 digits, except when the zipcode started woth "00000". This eliminated zip code values like: "?", "*", "0", "00000" or "UNKNOWN".
- The 222 complaint categories and their mapping to integers can be viewed in the file "311_complaint_mapping.txt"

HOW TO RUN
- How to run program for this dataset (minsup=10%, minconf=50%):
	python main.py 311_integrated_dataset.csv 0.1 0.5

RESULTS
- You can find the results of the association rule mining in the file "311_output.txt"

ANALISYS
- The goal of doing association rule mining in this dataset is to identify related problems in city regions. We want to understand which problems should be investigated when there is one complaint. For example, in the interesting rules listed below, we see that when there is a complaint about illegal parking, there is 55% chance a driveway is being blocked. Another example is: when there is a problem with a street signal, it is very likely that the street lighting is also problematic.
- This kind of data could be used by the city to better repair those problems, although the results would be most insightful if the complaint categories were refactored to avoid big intersection between categories.
- Interesting Rules Mined:
	- [55,65,68,69] => [85] (Conf: 94%, Supp: 10.0%)
	  Meaning: Nonconst + Paint + Heating + Plumbing => Construction complaint
	  Comments: obvious association, as when we have complaints about the 4 types listed here, 94% of the times there is also construction complaint. Rules involving these 5 categories also appear with different categories on the right hand side.
	- [63,65,85] => [69] (Conf: 93%, Supp: 10.7%)
	  Meaning: Electric + Heating + Construction => Plumbing
	- [1] => [25] (Conf: 55%, Supp: 18.8%)
	  Meaning: Illegal parking => Blocked driveway
	- [89] => [69] (Conf: 50%, Supp: 12.3%)
	  Meaning: Sanitation condition => Plumbing
	- [6] => [11] (Conf: 52%, Supp: 12.4%)
	  Meaning: Rodent => Street condition
	- [4] => [11] (Conf: 56%, Supp: 10.8%) and [4] => [25] (Conf: 56%, Supp: 10.8%)
	  Meaning: Damaged tree => Street condition and Damaged tree => Blocked driveway
	- [118] => [102] (Conf: 58%, Supp: 12.2%)
	  Meaning: Street signal condition => Street light condition
- Interesting frequent itemsets mined:
	- [39,6], 10.2%
	  Meaning: Rodent and water systems complaints often happen in the same day in the same region
	- [45,67], 10.4%
	  Meaning: Noise and construction complaints often happen in the same day in the same region
	- [39,50], 13.5%
	  Meaning: Water system and sewer complaints often happen in the same day in the same region
	- [8], 16.6%
	  Meaning: Taxi complaints are very common, but they appear unrelated to other complaints

CONCLUSION
- This dataset provided many interesting association and itemset, that could even be useful for the city plan to address many of the complaints.


Association Rule Mining Implementation
########################################

FREQUENT ITEMSET MINING
- We followed the implementation of the section 2.1.1 of the paper, with one additional improvement (described below)
- In the original algorithm, after you do a JOIN between the frequent itemsets of size k-1, you also have to go over all the itemsets to discard the ones that have some subset that is not frequent. This is a rather costly task, and you can do two improvement to make this step faster (we implemented both):
	1. Instead of checking if all subsets are frequent, it suffices to check if all subsets of size k-1 are frequent. The reason is that these subsets include all other smaller subsets, which by the a priori theorem should also be frequent if the itemset that contains them is frequent.
	2. It turns out you don't even have to check all itemsets of size k-1. Since the candidate itemset was build from a joint of two smaller itemsets that had only the largest element different, then, by the apriori theorem all subsets that do not include both highest elements of the original itemsets are also frequent. Basically this translates to not checking again the two itemsets that generated the larger itemset.

ASSOCIATION RULE MINING
- In our case we are only interested in association rules with one element on the right-hand side and one or more elements in the left-hand side. This means we don't have to iterate through frequent itemsets of size 1 to look for association rules, and also means that for frequent itemsets of size k, we only have to check k association rules (i.e. trying to put each element in the right-hand side at a time)



Final Remarks
#####################

After initial implementation our algorithm was rather slow, but after we refactored the code using the appropriate data structures (sets, tuples, dicts) we achieved a speedup of around 2.5x in our running time.

The function gen_candidate_sets() implements (1) Join & (2)Prune of the Apriori Candidate Generation algorithm. Return a candiate set, based on which, expanded large k-itemset is generated.

The calculation of conf. score uses a dum method to scan over database 

