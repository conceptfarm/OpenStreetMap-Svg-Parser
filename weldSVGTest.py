from __future__ import absolute_import
import sys
import os
import copy
import re
import xml.etree.ElementTree as ET
import itertools
import operator
import json

svg_ns = '{http://www.w3.org/2000/svg}'

# Regex commonly used
number_re = r'[-+]?(?:\d+(?:\.\d*)?|\.\d+)(?:[eE][-+]?\d+)?'
unit_re = r'em|ex|px|in|cm|mm|pt|pc|%'

COMMANDS = 'MmZzLlHhVvCcSsQqTtAa'

f = '\\\\fs-02\\UserData\\ifloussov\\Downloads\\columbus_close_sorted.svg'
svgAll = open( (str(os.path.dirname(f)) + "\\" + (str(os.path.basename(f)).split(".")[0].strip()) + '_welded.svg' ),'w',encoding='utf-8')

tree = ET.parse(f)
root = tree.getroot()


xmlProlog = '' #maybe optional
svgHeader = '' #mandatory

svgFile = open(f,'r')
ET.register_namespace("", 'http://www.w3.org/2000/svg')


#get the xmlProlog and svg root from existing file
for line in svgFile:
    if (xmlProlog == ''):
        if (str(line).find('<?xml') != -1):
            xmlProlog = line
    elif (svgHeader == ''):
        if(str(line).find('<svg') != -1):
            svgHeader = line
    elif (svgHeader != ''):
        break

svgFile.close()


class PathUtil():

	number_re = r'[-+]?(?:\d+(?:\.\d*)?|\.\d+)(?:[eE][-+]?\d+)?'
	COMMANDS = 'MmZzLlHhVvCcSsQqTtAa'
	command_dic = {'M':2,'m':2,'Z':0,'z':0,'L':2,'l':2,'H':1,'h':1,'V':1,'v':1,'C':6,'c':6,'S':4,'s':4,'Q':4,'q':4,'T':2,'t':2,'A':7,'a':7}

	#num=[]
	#ops=[]

	def __init__(self, coords):
		self.num = re.findall(self.number_re, coords)
		self.ops = re.findall(r"[%s]" % self.COMMANDS, coords)
		#print(self.num)
		#print(self.ops)


	def reveseCoords(self):
		num_rev = []
		for i in reversed(range(1,len(self.num),2)):
			num_rev.append(self.num[i-1])
			num_rev.append(self.num[i])
			
		ops_rev = ['M']
		for i in reversed(range(1,len(self.ops))):
			if self.ops[i] != 'Z' and self.ops[i] != 'z':
				ops_rev.append(self.ops[i])

		if 'z' in self.ops:
			ops_rev.append('z')
		if 'Z' in self.ops:
				ops_rev.append('Z')

		result = ''
		cur = 0
		for o in range(0,len(ops_rev)):
			result = result + ops_rev[o] + ' '
			for j in range(cur, cur+self.command_dic[ops_rev[o]]):
				result = result + num_rev[j] + ' '
				cur = cur + 1

		return (result)

	def removeFirst(self):
		result = ''
		cur = 2
		for o in range(1,len(self.ops)):
			result = result + self.ops[o] + ' '
			for j in range(cur, cur + self.command_dic[self.ops[o]]):
				result = result + self.num[j] + ' '
				cur = cur + 1

		return (result)

	def removeLast(self):
		result = ''
		cur = 0
		for o in range(0,len(self.ops)-1):
			result = result + self.ops[o] + ' '
			for j in range(cur, cur+self.command_dic[self.ops[o]]):
				result = result + self.num[j] + ' '
				cur = cur + 1

		return (result)

	def isClosed(self):
		result = False
		if 'z' in self.ops or 'Z' in self.ops:
			result = True
		return result

	def getFirstPoint(self):
		return [self.num[0],self.num[1]]

	def getLastPoint(self):
		if self.isClosed():
			return [self.num[0],self.num[1]]
		else:
			return [self.num[-2],self.num[-1]]

def childParser(items):
	
	allWelded = False
	while allWelded == False:
		processed = []
		toDelete = []
		
		for i in range(0,len(items)):
			dCoords1 = items[i].attrib.get('d')
			if dCoords1 != None and dCoords1 != '' and i < len(items) and items[i] not in processed:
				
				path1 = PathUtil(dCoords1)
				
				#will not weld closed paths
				if path1.isClosed() == False:
					
					startP1 = path1.getFirstPoint()
					endP1 = path1.getLastPoint()

					for j in range(i+1,len(items)):
						dCoords2 = items[j].attrib.get('d')
						if dCoords2 != None and dCoords2 != '' and items[j] not in processed:
							
							
							path2 = PathUtil(dCoords2)
													
							if path2.isClosed() == False:

								startP2 = path2.getFirstPoint()
								endP2 = path2.getLastPoint() 

								if startP1 == endP2:
									#print('match start->end')
									#print('1 ', dCoords1)
									#print('2 ', dCoords2)
									#dCoords1 = dCoords1.replace('M','L')
									dCoords1 = path1.removeFirst()
									#print('3 ', dCoords1)
									startP1 = startP2
									dCoords1 = dCoords2 + dCoords1
									#print('f ', dCoords1)
									path1 = PathUtil(dCoords1)
									items[i].set('d', dCoords1)
									processed.append(items[j])
									toDelete.append(items[j])
								
								elif endP1 == startP2:
									#print('match end->start')
									#dCoords2 = dCoords2.replace('M','L')
									#print('1 ', dCoords1)
									#print('2 ', dCoords2)
									dCoords2 = path2.removeFirst()
									#print('3 ', dCoords2)
									endP1 = endP2
									dCoords1 = dCoords1 + dCoords2
									path1 = PathUtil(dCoords1)
									#print('f ', dCoords1)
									items[i].set('d', dCoords1)
									processed.append(items[j])
									toDelete.append(items[j])
									#groupList[count].set('id',count)
								
								elif endP1 == endP2:
									#need to revers line 2
									#print('match end->end')
									#print('1 ', dCoords1)
									#print('2 ', dCoords2)
									dCoords2 = path2.reveseCoords()
									path2 = PathUtil(dCoords2)
									endP2 = path2.getLastPoint() 
									dCoords2 = path2.removeFirst()
									#print('3 ', dCoords2)
									endP1 = endP2
									dCoords1 = dCoords1 + dCoords2
									#print('f ', dCoords1)
									path1 = PathUtil(dCoords1)
									items[i].set('d', dCoords1)
									processed.append(items[j])
									toDelete.append(items[j])
								
								elif startP1 == startP2:
									#need to reverse line 2
									#print('match start->start')
									#print('1 ', dCoords1)
									#print('2 ', dCoords2)
									dCoords2 = path2.reveseCoords()
									tempPath2 = PathUtil(dCoords2)
									startP2 = tempPath2.getFirstPoint() 
									dCoords1 = path1.removeFirst()
									#print('3 ', dCoords1)
									startP1 = startP2
									dCoords1 = dCoords2 + dCoords1
									path1 = PathUtil(dCoords1)
									#print('f ', dCoords1)
									items[i].set('d', dCoords1)
									processed.append(items[j])
									toDelete.append(items[j])
									#print(items[j].attrib.get('d'))
			
			if len(items[i]) > 0:
				allWelded = True
				childParser(items[i])
		
		if len(toDelete) == 0:
			allWelded = True

		for k in reversed( range( 0, len(items) ) ):
			if items[k] in toDelete:
				#print('del ', items[k].attrib.get('d'))
				items.remove(items[k])

childParser(root)


#svgAll.write(xmlProlog) 
#svgAll.write(svgHeader)

xmldata = ET.tostring(root,encoding='unicode',method='xml')
svgAll.write(xmldata)


svgAll.close()


#print('items ', len(items))
#print(items)

'''
for item in items:

	for lastItem to currentItem by -1
		compare start point
		compare end point
		if one of those is equal to start point or end point of item then
			get attribute d
			if start points match
				replace M with L for the item
				prepend currentItem
			if last point match
				replace M with L for the currentItem
				append currentItem to end of item

			remove current items from items


'''
'''
processed = []
weldedElements = []

for i in range(len(items)):
	startP1 = items[i][1][0]
	endP1 = items[i][1][1]
	dCoords1 = items[i][0].attrib.get('d')

	
	for j in reversed( range( i+1, len(items) ) ):
		if items[j][0] not in processed:
			startP2 = items[j][1][0]
			endP2 = items[j][1][1]
			dCoords2 = items[j][0].attrib.get('d')

			if startP1 == endP2:
				#print('match start->end')
				dCoords1=dCoords1.replace("M","L")
				startP1 = startP2
				dCoords1 = dCoords2 + dCoords1
				processed.append(items[j][0])
			
			elif endP1 == startP2:
				#print('match end->start')
				dCoords2=dCoords2.replace('M','L')
				endP1 = endP2
				dCoords1 = dCoords1 + dCoords2
				processed.append(items[j][0])
				#groupList[count].set('id',count)
			
			elif endP1 == endP2:
				#need to revers line 2
				#print('match end->end')
				processed.append(items[j][0])
			
			elif startP1 == startP2:
				#need to reverse line 2
				#print('match start->start')
				processed.append(items[j][0])

	weldedElements.append(dCoords1)

print(weldedElements)
'''

'''
arr = [3,1,2,3,4,5,6,7,8]

for i in range(len(arr)):
	print('index is: ', i)
	print('i is: ', arr[i])
	for num in reversed( range( i+1, len(arr) ) ) : 
		print (arr[num])
'''