# -*- coding: utf-8 -*-
from collections import Counter
from itertools import izip
from collections import defaultdict
class Node:
	def __init__(self, name=None,data=None):
		self.data = data #dữ liệu về các transaction và count
		self.next = {} #dấn đến node con
		self.link = None #dẫn đến node có cùng tên kế tiếp
		self.name = name #tên node
class HeaderTable:
	def __init__(self):
		self.count = Counter() 
		self.rank = None #chứa thứ tự các item
		self.table = None #bảng
	def add(self,item):
		self.count[item] += 1
	def sort_rank(self):
		self.rank = [x[0] for x in self.count.most_common()]
		self.table = {x[0]:{"head":None,"tail":None,"count":x[1]} for x in self.count.most_common()}
	def adjust(self,itemset):
		adjusted = []
		for item in self.rank:
			if item in itemset:
				adjusted.append([item,itemset[item]])
		return adjusted
	def addLink(self,node):
		if self.table[node.name]["head"] is None:
			self.table[node.name]["head"] = node
		else:
			self.table[node.name]["tail"].link = node
		self.table[node.name]["tail"] = node
class FPTree:
	def __init__(self):
		self.root = Node(name="ROOT")
		self.htable = HeaderTable()
		self.rank = None
	def count(self,itemsets):
		for x in set([item for itemset in itemsets.keys() for item in itemset]):
			self.htable.add(x)
	def sort(self):
		self.htable.sort_rank()
		self.rank = self.htable.rank
	def getAllPath(self):
		pass
	def add(self,transaction,STT):
		visitor = self.root
		itemset = self.htable.adjust(transaction)
		for item,count in itemset:
			if item in visitor.next:
				visitor.next[item].data += [[STT,count]]
			else:
				visitor.next[item] = Node(name=item,data=[[STT,count]])
				self.htable.addLink(visitor.next[item])
			visitor = visitor.next[item]

class FPUTT:
	def __init__(self):
		self.SIT = defaultdict(lambda:list())
		self.IIT = defaultdict(lambda:list())
		self.tree = FPTree()
	def CreateTree(self,DB,SIS):
		#
		def getSIandII(itemset):
			kv = dict(itemset)
			resultSI = {}
			resultII = []
			setSI = set()
			for SI in SIS:
				flag = True
				for I in SI:
					if (I not in kv):
						flag = False
						break
				if flag:
					setSI |= set(SI)
					resultSI["".join(SI)] = [[item,kv[item]] for item in SI]
			resultII = [x for x in itemset if x[0] not in setSI]
			return resultSI,resultII
		def getSI(itemset):
			kv = dict(itemset)
			resultSI = {}
			for SI in SIS:
				flag = True
				for I in SI:
					if (I not in kv):
						flag = False
						break
				if flag:
					for item in SI:
						resultSI[item] = kv[item]
			return resultSI


		count = 1
		for transaction in db:
			SI,II = getSIandII(transaction)
			for itemset in SIS:
				if "".join(itemset) in SI:
					self.SIT["".join(itemset)] += ["T"+str(count)]
			self.IIT["T"+str(count)] = II
			self.tree.count(SI)
			count+=1
		self.tree.sort()
		
		for transaction in db:
			SI = getSI(transaction)
			self.tree.add(SI,"T"+str(count))
	def PerturbedTree(self,SIS=None,delta=None):
		pass
	def RecoverDB(self,DB=None):
		pass
	def run(self,db,SIS=None,DB=None,delta=None):
		self.CreateTree(DB,SIS)
		self.PerturbedTree(SIS,delta)
		self.RecoverDB(DB)
		pass


def readDB(database):
	db = []
	def convert(x):
		x = list(x)
		x[1] = int(x[1])
		return x
	with open(database,'r') as f:
		for line in f.readlines():
			content = line.strip().replace("(","").replace(")","").replace(" ","").split(",")
			content = zip(content[0::2], content[1::2])
			db.append([convert(x) for x in content])
	return db

db = readDB("database")
SIS = [["B","D"],["C","D"],["A","C","D"]]
UTILITY = {"A":5,"B":3,"C":1,"D":6,"E":2}
FPUTT = FPUTT()
FPUTT.CreateTree(db,SIS)
