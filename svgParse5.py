import xml.etree.ElementTree as ET
import sys
import os
import re
import time

'''

TODO:
- weld paths in the same group

'''

#List of CSS styles for objects to be extracted
knownStyleList = [
{'style':['fill:rgb(85.098039%,81.568627%,78.823529%)','stroke-width:0.75','stroke:rgb(72.54902%,66.27451%,61.176471%)'],'name':'buildings brown'},
{'style':['fill:rgb(72.54902%,66.27451%,61.176471%)','stroke-width:0.75','stroke:rgb(64.313725%,56.078431%,49.411765%)'],'name':'churches dark brown'},
{'style':['fill:rgb(93.333333%,93.333333%,93.333333%)','stroke-width:0.3','stroke:rgb(62.745098%,43.921569%,43.921569%)'],'name':'parking lots'},
{'style':['fill:rgb(81.960784%,77.647059%,74.117647%)', 'stroke:none'],'name':'buildings'},

{'style':['fill:none','stroke:rgb(90.980392%,57.254902%,63.529412%)'],'name':'highway red'},
{'style':['fill:none','stroke:rgb(90.196078%,43.137255%,53.72549%)'],'name':'highway pink 1.9pt'},
{'style':['fill:none','stroke:rgb(95.686275%,76.470588%,49.019608%)'],'name':'highway yellow 1.8pt'},
{'style':['fill:none','stroke:rgb(98.823529%,83.921569%,64.313725%)'],'name':'highway yellow 4pt'},
{'style':['fill:none','stroke:rgb(96.470588%,58.823529%,47.843137%)'],'name':'highway orange 1.9pt'},
{'style':['fill:none','stroke:rgb(97.647059%,69.803922%,61.176471%)'],'name':'highway pink'},

{'style':['fill:none','stroke:rgb(100%,100%,100%)'],'name':'white outline'},
{'style':['fill:rgb(100%,100%,100%)','stroke:none'],'name':'white fill'},
{'style':['fill:rgb(100%,100%,100%)','stroke:rgb(100%,100%,100%)'],'name':'white outline fill'},
{'style':['fill:none','stroke:rgb(96.862745%,98.039216%,74.901961%)'],'name':'major roads'},
{'style':['fill:none','stroke:rgb(100%,100%,100%)'],'name':'footpath'},
{'style':['fill:none','stroke:rgb(73.333333%,73.333333%,73.333333%)'],'name':'trailA'},
{'style':['fill:none','stroke:rgb(98.039216%,50.196078%,44.705882%)'],'name':'trailB'},
{'style':['fill:none','stroke:rgb(0%,0%,100%)'],'name':'trailC'},
{'style':['fill:none','stroke:rgb(56.078431%,56.078431%,56.078431%)'],'name':'side roads 9pt'},
{'style':['fill:none','stroke:rgb(60%,60%,60%)'],'name':'side roads B 5pt'},

{'style':['fill:rgb(70.980392%,89.019608%,70.980392%)','stroke:none'],'name':'green areas A'},
{'style':['fill:rgb(78.431373%,98.039216%,80%)','stroke:none'],'name':'green areas B'},
{'style':['fill:rgb(80.392157%,92.156863%,69.019608%)', 'stroke:none'],'name':'green areas C'},
{'style':['fill:rgb(66.666667%,79.607843%,68.627451%)','stroke:none'],'name':'green areas D'},
{'style':['fill:rgb(67.843137%,81.960784%,61.960784%)','stroke:none'],'name':'green TreeArea'},
{'style':['fill:rgb(78.431373%,84.313725%,67.058824%)','stroke:none'],'name':'green ShrubArea'},
{'style':['fill:rgb(66.666667%,87.843137%,79.607843%)','stroke:rgb(41.568627%,72.941176%,60.784314%)','stroke-width:0.5'],'name':'green Recreation'},
{'style':['fill:rgb(81.568627%,81.568627%,81.568627%)','stroke:none'],'name':'residential area'},
{'style':['fill:rgb(71.372549%,70.980392%,57.254902%)','stroke:none'],'name':'dark green area'},
{'style':['fill:rgb(91.372549%,90.588235%,88.627451%)','stroke:rgb(66.666667%,57.254902%,32.941176%)','stroke-width:0.2'],'name':'airport area'},

{'style':['fill:none','stroke:rgb(66.666667%,82.745098%,87.45098%)','stroke-width:3'],'name':'creeks stroke'},
{'style':['fill:none','stroke:rgb(66.666667%,82.745098%,87.45098%)','stroke-width:6'],'name':'rivers stroke'},
{'style':['stroke:none','fill:rgb(66.666667%,82.745098%,87.45098%)'],'name':'water fill'},
{'style':['stroke:none','fill:rgb(96.078431%,91.372549%,77.647059%)'],'name':'sand area'}
]

parsedStyles = {} #dict to keep track of parsed styles

#find a way to deal with groups
def groupByStyle(ch):
	for child in ch:
		if child.attrib.get('style') != None and child.attrib.get('d') != None and child.attrib.get('d') != '':
			styleStr = child.attrib.get('style')
			dCoords = child.attrib.get('d')

			#add checking known styles here, use that name instead of the number
			if parsedStyles.get(styleStr) == None:
				count = str(len(parsedStyles) + 1)
				
				for style in knownStyleList:
					if all(x in styleStr for x in style['style']):
						count = count + '_' + style['name']
						print(style['name'])

				groupList[count] = ET.Element('g')
				groupList[count].set('id',count)
				groupList[count].set('style',styleStr) #group gets the style but not inidividual paths
				groupList[count].text = ''
				parsedStyles[styleStr] = count
			
			count = parsedStyles.get(styleStr)

			pathEl = ET.SubElement(groupList[count],'path')
			pathEl.set('d',dCoords)

		#If this is already a group - process the children
		if len(child) > 0:
			groupByStyle(child)

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

def weldByGroup(items):
	
	global iters

	allWelded = False
	while allWelded == False:
		processed = []
		toDelete = []
		
		for i in range(0,len(items)):
			#print('Welding ', str(items.attrib.get('id')), ' path ' , str(i), ' out of ', str(len(items)))
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
									dCoords1 = path1.removeFirst()
									startP1 = startP2
									dCoords1 = dCoords2 + dCoords1
									path1 = PathUtil(dCoords1)
									items[i].set('d', dCoords1)
									processed.append(items[j])
									toDelete.append(items[j])
									
								
								elif endP1 == startP2:
									#print('match end->start')
									dCoords2 = path2.removeFirst()
									endP1 = endP2
									dCoords1 = dCoords1 + dCoords2
									path1 = PathUtil(dCoords1)
									items[i].set('d', dCoords1)
									processed.append(items[j])
									toDelete.append(items[j])
									
								
								elif endP1 == endP2:
									#need to revers line 2
									dCoords2 = path2.reveseCoords()
									path2 = PathUtil(dCoords2)
									endP2 = path2.getLastPoint() 
									dCoords2 = path2.removeFirst()
									endP1 = endP2
									dCoords1 = dCoords1 + dCoords2
									path1 = PathUtil(dCoords1)
									items[i].set('d', dCoords1)
									processed.append(items[j])
									toDelete.append(items[j])
									
								
								elif startP1 == startP2:
									#need to reverse line 2
									dCoords2 = path2.reveseCoords()
									tempPath2 = PathUtil(dCoords2)
									startP2 = tempPath2.getFirstPoint() 
									dCoords1 = path1.removeFirst()
									startP1 = startP2
									dCoords1 = dCoords2 + dCoords1
									path1 = PathUtil(dCoords1)
									items[i].set('d', dCoords1)
									processed.append(items[j])
									toDelete.append(items[j])


								iters = iters + 1
			
			if len(items[i]) > 0:
				allWelded = True
				weldByGroup(items[i])
		
		if len(toDelete) == 0:
			allWelded = True

		for k in reversed( range( 0, len(items) ) ):
			if items[k] in toDelete:
				items.remove(items[k])


fs = ['\\\\fs-02\\UserData\\ifloussov\\Downloads\\columbus_close.svg']

for arg in fs:
#for arg in sys.argv:
	if os.path.isfile(arg) == True:
		
		f = str(arg)
		filename, file_extension = os.path.splitext(f)

		if file_extension == '.svg':
			
			svgFile = open(f,'r')

			xmlProlog = '' #maybe optional
			svgHeader = '' #mandatory

			ET.register_namespace("", 'http://www.w3.org/2000/svg')
			tree = ET.parse(f)
			root = tree.getroot()

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
			
			svgSorted = open( (str(os.path.dirname(f)) + "\\" + (str(os.path.basename(f)).split(".")[0].strip()) + '_sorted.svg' ),'w',encoding='utf-8')
			svgWelded = open( (str(os.path.dirname(f)) + "\\" + (str(os.path.basename(f)).split(".")[0].strip()) + '_sorted_welded.svg' ),'w',encoding='utf-8')
			
			#create a dict of files to write to for each style
			groupList={}

			groupByStyle(root)

			svgSorted.write(xmlProlog) 
			svgSorted.write(svgHeader)

			for e in groupList:
				xmldata = ET.tostring(groupList[e],encoding='unicode',method='xml')
				svgSorted.write(xmldata)
				svgSorted.write("\n")

			svgSorted.write('</svg>')
			svgSorted.close()
			
			tree = ET.parse(svgSorted.name)
			root = tree.getroot()
			
			iters = 0
			tic = time.perf_counter()
			weldByGroup(root)
			toc = time.perf_counter()
			print(f"Welded verts in {toc - tic:0.4f} seconds")
			print(f"Welded verts in {iters} passes")
			
			xmldata = ET.tostring(root,encoding='unicode',method='xml')
			svgWelded.write(xmldata)
			svgWelded.close()

		else:
			
			if file_extension != '.py':
				print('ERROR: Wrong format. The dropped file is not an svg file, drop only svg files.')
	else:
		print('ERROR: Not a file. The dropped file is not a file, drop only svg files.')

#input("Done! Press ENTER to close...")
