import xml.etree.ElementTree as ET
import sys
import os
import re

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
'''
def namespace(element):
    m = re.match(r'\{.*\}', element.tag)
    return m.group(0) if m else ''


def styleToDict(arrg):
    result = {}
    defs = arrg.split(';')
    for d in defs:
        if d != '':
            result[d.split(':')[0].strip()] = d.split(':')[1].strip()
    if result.get('fill') == None:
        result['fill'] = "none"
    if result.get('stroke') == None:
        result['stroke'] = "none"
    if result.get('stroke-width') == None:
        result['stroke-width'] = '0.0'
    return result

'''

parsedStyles = {} #dict to keep track of parsed styles

#find a way to deal with groups
def childParser(ch):
	for child in ch:
		if child.attrib.get('style') != None and child.attrib.get('d') != None:
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
			#pathEl.set('style',styleStr)


		if len(child) > 0:
			childParser(child)


for arg in sys.argv:
	if os.path.isfile(arg) == True:
		
		f = str(arg)
		filename, file_extension = os.path.splitext(f)

		if file_extension == '.svg':
			
			svgAll = open( (str(os.path.dirname(f)) + "\\" + (str(os.path.basename(f)).split(".")[0].strip()) + '_sorted.svg' ),'w',encoding='utf-8')

			xmlProlog = '' #maybe optional
			svgHeader = '' #mandatory


			svgFile = open(f,'r')
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

			#create a dict of files to write to for each style
			groupList={}

			childParser(root)

			svgAll.write(xmlProlog) 
			svgAll.write(svgHeader)

			for e in groupList:
				xmldata = ET.tostring(groupList[e],encoding='unicode',method='xml')
				svgAll.write(xmldata)
				svgAll.write("\n")

			svgAll.write('</svg>')
			svgAll.close()


		else:
			
			if file_extension != '.py':
				print('ERROR: Wrong format. The dropped file is not an svg file, drop only svg files.')
	else:
		print('ERROR: Not a file. The dropped file is not a file, drop only svg files.')

input("Done! Press ENTER to close...")
