
# reading line by line
infile = open('DOB_Complaints_Received.csv', 'r')
outfile = open('DOB_integrated_dataset.csv', 'w')

complaint_set = set()
last_building_id = None

# discard header
line = infile.readline()

line = infile.readline().strip()
while len(line) > 0:
    building_id, complaint = line.split(",")
    
    if last_building_id != None and building_id != last_building_id:
    	complaint_list = list(complaint_set)
    	complaint_list.sort()
    	outfile.write(",".join(complaint_list) + "\n")
    	last_building_id = building_id
    	complaint_set.clear()
    elif last_building_id == None:
    	last_building_id = building_id

    complaint_set.add(complaint)
    line = infile.readline().strip()


infile.close()
outfile.close()