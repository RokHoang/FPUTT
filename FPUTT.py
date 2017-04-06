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
	def getAllNode(self,TIDS):
		for TID in TIDS:
			node = self.root
			flag = True
			while (node.next and flag):
				#print node.name
				flag = False
				for name,child in node.next.iteritems():
					#print name, child.data
					for d in child.data:
						if TID == d[0]:
							yield [d,child.name]
							node = child
							flag = True
							break


			
		pass	
	def getUtil(self,item,TIDS):
		head = self.htable.table[item]["head"]
		tail =self.htable.table[item]["tail"]
		node = head
		sumUtil = 0
		while (True):
			sumUtil += sum([transaction[1] for transaction in node.data if transaction[0] in TIDS])
			node = node.link
			if (node == None):
				return sumUtil*UTILITY[item]
	def getSumUtil(self,itemset,TIDS):

		return sum([self.getUtil(item,TIDS) for item in itemset])

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
		count = 1
		for transaction in db:
			SI = getSI(transaction)
			self.tree.add(SI,"T"+str(count))
			count+=1
	def RemoveItem(self,item,delta,itemset):
		TIDS = self.SIT["".join(itemset)]
		def removeItem(item,delta,itemset,TIDS):
			head = self.tree.htable.table[item]["head"]
			tail =self.tree.htable.table[item]["tail"]
			node = head
			maxnode = None
			maxvalue = 0
			while(True):
				for transaction in node.data:
					if (transaction[1]>maxvalue):
						maxvalue=transaction[1]
						maxnode = transaction
				if (node == tail):
					break
				node = node.link
			print maxnode
			total_util = self.tree.getSumUtil(itemset,TIDS)
			reduction = (total_util-delta+1)/UTILITY[item]
			if (reduction<maxnode[1]):
				maxnode[1] = maxnode[1] - reduction
			else:
				maxnode[1] = 0
			print maxnode
			print total_util
			print self.tree.getSumUtil(itemset,TIDS)			
		removeItem(item,delta,itemset,TIDS)
		pass
	def RemoveRemain(self,itemset,delta):
		rankItem = []
		print sorted(UTILITY.most_common(), key=lambda (x,y): (y,x))
		for item in UTILITY.most_common():
			if item[0] in itemset:
				rankItem+=item[0]
		print rankItem
		TIDS = self.SIT["".join(itemset)]
		for item in rankItem:
			print "[+]"+item
			while (self.tree.getSumUtil(itemset,TIDS) > delta):
				self.RemoveItem(itemset,delta,itemset)
				if (self.tree.getSumUtil(item,TIDS) == 0):
					break

		return
		pass

	def PerturbedTree(self,SIS=None,delta=None):
		rankIS = Counter({" ".join(itemset):self.tree.getSumUtil(itemset,self.SIT["".join(itemset)]) for itemset in SIS})
		print rankIS.most_common()
		for key in rankIS.most_common():
			print key[0]
			itemset = key[0].split()
			TIDS = self.SIT["".join(itemset)]
			targetUtil = self.tree.getSumUtil(itemset,TIDS)-delta
			maxUtil = 0
			targetNode = None
			while(targetUtil>0):
				print TIDS
				maxUtil = 0
				targetNode = None
				for node in self.tree.getAllNode(TIDS):
					#print node
					currentUtil = UTILITY[node[1]] * node[0][1]
					if (maxUtil<currentUtil):
						maxUtil = currentUtil
						targetNode = node
				
				print targetNode
				if(maxUtil<=targetUtil):
					targetNode[0][1] = 0
					targetUtil -= maxUtil
				else:
					targetNode[0][1] = targetNode[0][1] - (targetUtil/UTILITY[targetNode[1]])
					targetUtil = 0
				print targetNode
				print "===="
				#for P in self.tree.getAllPath(TIDS):
				#	print P
					#if ()
				
			#while (self.tree.getSumUtil(itemset,TIDS) > delta):
				#self.RemoveRemain(itemset,delta)
				
				pass
		return
		pass
	def RecoverDB(self,DB=None):
		count = 1
		for transaction in DB:
			TID = "T"+str(count)
			node = self.tree.root
			flag = True
			path = []
			while (node.next and flag):
				#print node.name
				flag = False
				for name,child in node.next.iteritems():
					#print name, child.data
					for d in child.data:
						if TID == d[0]:
							node = child
							path.append([name,d[1]])
							flag = True
							break
			
			print TID,path+self.IIT[TID]
			count+=1
		pass
	def run(self,SIS=None,DB=None,delta=None):
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
UTILITY = Counter({"A":5,"B":3,"C":1,"D":6,"E":2})
FPUTT = FPUTT()
FPUTT.run(SIS,db,102)

#tìm max của các utility 
