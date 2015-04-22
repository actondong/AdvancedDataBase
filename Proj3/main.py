from __future__ import division
import copy
from collections import defaultdict
import sys


# returns an array where each element is a dict with itemsets as keys and relative support as value
def get_frequent_itemsets(filename, relative_minsup=.01):
	print('Starting frequent itemset mining')

	# reading line by line
	infile = open(filename, 'r')

	# count individual items
	basket_count = 0
	counts = defaultdict(int)
	line = infile.readline().strip()
	while len(line) > 0:
		items = frozenset(line.split(','))
		for item in items:
			counts[item] += 1
		basket_count += 1
		line = infile.readline().strip()
	infile.seek(0)

	# keep items with freq > minsup
	minsup = relative_minsup * basket_count
	L1 = { tuple([item]):(float(count)/basket_count) for item,count in counts.items() if count > minsup }
	counts.clear()

	# start building vector of sets for frequent itemsets. Itemsets are represented as tuples so they stay ordered
	# in each position of this vector there is a dict where the keys are the itemsets tuples and the values are the relative support
	L = []
	L.append(L1)
	print('Finished first pass (%i frequent items)...' % len(L1))

	# start iterating looking for larger frequent itemsets (k = size of itemsets)
	k = 2
	while True:
		# generate all candidate itemsets of size k (passing all frequent itemsets of size k-1)
		# candidate sets are retuned as ordered tuples
		candidate_sets = gen_candidate_sets(L[k-2])
		print('Got candidates... (%i candidates)' % len(candidate_sets))

		# count aparison of candidate sets
		line = infile.readline().strip()
		while len(line) > 0:
			items = frozenset(line.split(','))
			for candidate_set in candidate_sets:
				if items.issuperset(candidate_set):
					counts[candidate_set] += 1
			line = infile.readline().strip()
		infile.seek(0)

		# keep itemsets with freq > minsup
		Lk = { itemset:(float(count)/basket_count) for itemset,count in counts.items() if count >= minsup }
		counts.clear()
		
		# if found no frequent itemset of size k, stop
		if len(Lk) == 0:
			infile.close()
			break

		print('Finished first pass (%i frequent itemsets)...' % len(Lk))
		L.append(Lk)
		k += 1
		
	return L

def get_high_confidence_rules(L, minconf):
	print('Starting association rule mining')

	association_rules = []

	# start with itemsets of two items
	for k in xrange(1, len(L)):
		itemsets_support_dict = L[k]
		for itemset,relative_support in itemsets_support_dict.items():
			# in each itemset try to chose one item as 'implication'
			for i in xrange(len(itemset)):
				implication_item = itemset[i]
				precondition_set = itemset[:i] + itemset[(i+1):]
				confidence = relative_support / L[k-1][precondition_set]

				if confidence >= minconf:
					association_rules.append(tuple([confidence, relative_support, precondition_set, implication_item]))
		print('Finished pass...')

	return association_rules

def print_results(L, association_rules, relative_minsup, minconf):
	# sort all frequent itemsets in decreasing order of support
	frequent_itemsets = []
	for itemset_support_dict in L:
		frequent_itemsets += [(relative_support,itemset) for itemset,relative_support in itemset_support_dict.items()]
	frequent_itemsets.sort(reverse=True)

	f = open('output.txt', 'w')

	# print frequent itemsets to file
	f.write('==Frequent itemsets (min_sup=%.1f%%)\n' % (relative_minsup*100))
	for relative_support,itemset in frequent_itemsets:
		itemset_string = ','.join(itemset)
		f.write('[%s], %.1f%%\n' % (itemset_string, relative_support*100))
	f.write('\n')
	
	# sort all association rules in decreasing order of confidence
	association_rules.sort(reverse=True)

	# print association rules to file
	f.write('==High-confidence association rules (min_conf=%i%%)==\n' % (minconf*100))
	for association_rule in association_rules:
		confidence, support, precondition_set, implication_item = association_rule
		precondition_string = ','.join(precondition_set)
		f.write('[%s] => [%s] (Conf: %i%%, Supp: %.1f%%)\n' % (precondition_string, implication_item, confidence*100, support*100))
	
	f.close()

# generate candidate itemsets of size k
# L is the dictionary where the keys are the k-1 itemsets
def gen_candidate_sets(Lk_minus_one):
	C = []
	itemsets = Lk_minus_one.keys()
	for i in xrange(len(itemsets)):
		for j in xrange(i+1, len(itemsets)):
			itemset_1 = itemsets[i]
			itemset_2 = itemsets[j]

			# if itemsets match all items except last (or they are itemsets with 1 item)
			if len(itemset_1) == 1 or itemset_1[:-1] == itemset_2[:-1]:
				# merge two itemsets and keep items ordered
				if itemset_1[-1] < itemset_2[-1]:
					new_itemset = itemset_1 + itemset_2[-1:]
				else:
					new_itemset = itemset_2 + itemset_1[-1:]

				# check if all subsets are frequent. Since the new itemset was generated from itemset_1 and itemset_2,
				# there is no need to check whether any subset of those itemsets is frequent (they are!). Therefore,
				# we only have to check subsets that include the last two elements. We also don't need to check subsets
				# of size less than k-1. All these constraints translate to checking if k-2 subsets are frequente, where
				# these subsets are built ommiting one of the elements of the new itemset, except the last two which will
				# always be present
				veto = False
				for l in xrange(len(new_itemset)-2):
					# create subset without one element
					subset = new_itemset[:l] + new_itemset[(l+1):]
					if subset not in Lk_minus_one:
						veto = True
						break

				# only add if itemset was not 'vetoed'
				if not veto:
					C.append(new_itemset)

	return C
	

if __name__ == "__main__":
	if len(sys.argv) != 4:
		print "USAGE:  python main.py csv_file_name.csv minsup minconf"
	
	filename = sys.argv[1]
	relative_minsup = float(sys.argv[2])
	minconf = float(sys.argv[3])

	L = get_frequent_itemsets(filename, relative_minsup=relative_minsup)
	association_rules = get_high_confidence_rules(L, minconf=minconf)
	# import pdb; pdb.set_trace()
	print_results(L, association_rules, relative_minsup=relative_minsup, minconf=minconf)

