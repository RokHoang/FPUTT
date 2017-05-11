# -*- coding: utf-8 -*-
from collections import Counter
from itertools import izip
from collections import defaultdict
def readDBrealData(database,product_price):
	uti_price = Counter()
	with open(product_price,"r") as f_price:
		for line in f_price.readlines():
			k,v = line.split()
			uti_price[k] = float(v)


	def pairwise(iterable):
		"s -> (s0, s1), (s2, s3), (s4, s5), ..."
		a = iter(iterable)
		return izip(a, a)
	def convert(x):
		x = list(x)
		x[1] = int(x[1])
		return x
	db = []
	with open(database,"r") as f_item:
		for line in f_item.readlines()[3:]:
			content = line.split()
			content = zip(content[0::2], content[1::2])
			db.append([convert(x) for x in content])
	return db,uti_price
	pass
db,uti_price = readDBrealData("utility_mine/RealData/real_data_aa","utility_mine/RealData/product_price")
def sum_uti():
	return sum([sum([int(round(uti_price[ten]*soluong)) for ten,soluong in itemset]) for itemset in db])
print sum_uti()

f = open("realData_spmf.txt","w")
for itemset in db:
	list_uti = [int(round(uti_price[ten]*soluong)) for ten,soluong in itemset]
	f.write(" ".join([item[0] for item in itemset]))
	f.write(":"+str(sum(list_uti))+":")
	f.write(" ".join(str(x) for x in list_uti))
	f.write("\n")
f.close()
#26388499.832
#26336941
