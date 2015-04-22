import time
import re

# reading line by line
infile = open('311_Complaints_Received.csv', 'r')
outfile = open('311_integrated_dataset.csv', 'w')
    
complaint_id_map = dict()
current_zip = None
complaints_by_month = dict()

# discard header
line = infile.readline()

line = infile.readline().strip()
# import pdb; pdb.set_trace()
while len(line) > 0:
    date_string, complaint, zipcode = line.split(",")
    complaint = complaint.lower()

    # if new zipcode, print last one to file and reset sets
    if zipcode != current_zip:
        for year_month,complaint_set in complaints_by_month.items():
            complaint_list = list(complaint_set)
            complaint_list.sort()
            outfile.write(",".join(complaint_list) + "\n")

        if current_zip:
            print("Zip: " + current_zip)
        current_zip = zipcode
        complaints_by_month = dict()

    # ignore some zip codes (just don't count them)
    if not re.match('^\d{5}', zipcode) or zipcode[:5] == '00000':
        line = infile.readline().strip()
        continue

    # ignore some complaint types
    if complaint == ['Customer Complaint', 'Street Condition']:
        line = infile.readline().strip()
        continue        

    # ensure complaint is mapped to integer
    if complaint not in complaint_id_map:
        complaint_id_map[complaint] = len(complaint_id_map)
    
    # get year and month of complaint
    date = time.strptime(date_string, "%m/%d/%Y %I:%M:%S %p")
    year_month = str(date.tm_year) + '-' + str(date.tm_mon) + str(date.tm_mday)

    # update set
    if year_month not in complaints_by_month:
        complaints_by_month[year_month] = set([str(complaint_id_map[complaint])])
    else:
        complaints_by_month[year_month].add(str(complaint_id_map[complaint]))

    line = infile.readline().strip()

# print things about last zip
for year_month,complaint_set in complaints_by_month.items():
    complaint_list = list(complaint_set)
    complaint_list.sort()
    outfile.write(",".join(complaint_list) + "\n")

infile.close()
outfile.close()

# print complaint mapping
outfile = open('311_complaint_mapping.txt', 'w')
complaints_mappings = [(number, complaint) for complaint,number in complaint_id_map.items()]
complaints_mappings.sort()
for number, complaint in complaints_mappings:
    outfile.write("%i    %s\n" % (number, complaint.capitalize()))
outfile.close()