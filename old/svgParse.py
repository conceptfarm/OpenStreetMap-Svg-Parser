import xml.etree.ElementTree as ET
import sys
import os
import re


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

def childParser(ch):
	for child in ch:
		if child.attrib.get('style') != None:
			#print (ET.tostring(child))
			#print (child.attrib.get('style'))
			
			dictStyle = styleToDict(child.attrib.get('style'))
			styleStr = child.attrib.get('style')
			dCoords = child.attrib.get('d')
			for s in styleList:
				if s['fill'] == dictStyle['fill'] and s['stroke'] == dictStyle['stroke'] and s['stroke-width'] == dictStyle['stroke-width']:
					#print("match")
					xmlstr = (ET.tostring(child).decode('utf-8','ignore')) 
					fileList[s['name']].write(xmlstr)
					pathEl = ET.SubElement(groupList[s['name']],'path')
					pathEl.set('d',dCoords)
					pathEl.set('style',styleStr)
					#groupList[s['name']].text = groupList[s['name']].text + xmlstr
	if len(child) > 0:
		childParser(child)

#List of CSS styles for objects to be extracted
styleList = [
{'fill':'rgb(85.098039%,81.568627%,78.823529%)','stroke-width':'0.75','stroke':'rgb(72.54902%,66.27451%,61.176471%)', 'name':'buildings brown'},
{'fill':'rgb(72.54902%,66.27451%,61.176471%)','stroke-width':'0.75','stroke':'rgb(64.313725%,56.078431%,49.411765%)', 'name':'churches dark brown'},
{'fill':'rgb(93.333333%,93.333333%,93.333333%)','stroke-width':'0.3','stroke':'rgb(62.745098%,43.921569%,43.921569%)', 'name':'parking lots'},
{'fill':'rgb(85.098039%,81.568627%,78.823529%)', 'stroke':'none','stroke-width':'0.0','name':'buildings'},

{'fill':'none','stroke-width':'8.6','stroke':'rgb(90.980392%,57.254902%,63.529412%)', 'name':'highway red'},
{'fill':'none','stroke-width':'6.6','stroke':'rgb(90.980392%,57.254902%,63.529412%)', 'name':'highway ramp 6.6pt'},
{'fill':'none','stroke-width':'8.5','stroke':'rgb(90.980392%,57.254902%,63.529412%)', 'name':'highway bridges 8.5pt'},
{'fill':'none','stroke-width':'1.9','stroke':'rgb(90.196078%,43.137255%,53.72549%)','name':'highway pink 1.9pt'},
{'fill':'none','stroke-width':'1.8','stroke':'rgb(95.686275%,76.470588%,49.019608%)','name':'highway yellow 1.8pt'},
{'fill':'none','stroke-width':'4','stroke':'rgb(98.823529%,83.921569%,64.313725%)','name':'highway yellow 4pt'},
{'fill':'none','stroke-width':'8.6','stroke':'rgb(98.823529%,83.921569%,64.313725%)','name':'highway yellow 8.6pt'},
{'fill':'none','stroke-width':'1.9','stroke':'rgb(96.470588%,58.823529%,47.843137%)','name':'highway orange 1.9pt'},
{'fill':'none','stroke-width':'1.8','stroke':'rgb(95.686275%,76.470588%,49.019608%)','name':'highway brown 1.8pt'},
{'fill':'none','stroke-width':'6.6','stroke':'rgb(97.647059%,69.803922%,61.176471%)','name':'highway pink 6.6pt'},
{'fill':'none','stroke-width':'8.5','stroke':'rgb(97.647059%,69.803922%,61.176471%)','name':'highway pink 8.5t'},

{'fill':'none','stroke-width':'3.8','stroke':'rgb(100%,100%,100%)', 'name':'side roads'},
{'fill':'none','stroke-width':'7.8','stroke':'rgb(100%,100%,100%)', 'name':'main roads'},
{'fill':'none','stroke-width':'7.6','stroke':'rgb(96.862745%,98.039216%,74.901961%)', 'name':'major roads'},
{'fill':'none','stroke-width':'7.5','stroke':'rgb(96.862745%,98.039216%,74.901961%)', 'name':'major bridges'},
{'fill':'none','stroke-width':'5.8','stroke':'rgb(96.862745%,98.039216%,74.901961%)', 'name':'major ramp'},
{'fill':'none','stroke-width':'0.9','stroke':'rgb(100%,100%,100%)', 'name':'footpath'},
{'fill':'none','stroke-width':'1','stroke':'rgb(73.333333%,73.333333%,73.333333%)', 'name':'trail'},
{'fill':'none','stroke-width':'1','stroke':'rgb(98.039216%,50.196078%,44.705882%)', 'name':'trail'},
{'fill':'none','stroke-width':'0.9','stroke':'rgb(0%,0%,100%)', 'name':'trail'},
{'fill':'none','stroke-width':'0.7','stroke':'rgb(73.333333%,73.333333%,73.333333%)', 'name':'side roads 0.7pt'},
{'fill':'none','stroke-width':'1.1','stroke':'rgb(73.333333%,73.333333%,73.333333%)', 'name':'side roads 1.1pt'},
{'fill':'none','stroke-width':'5','stroke':'rgb(73.333333%,73.333333%,73.333333%)', 'name':'side roads 5pt'},
{'fill':'none','stroke-width':'2','stroke':'rgb(73.333333%,73.333333%,73.333333%)', 'name':'side roads 2pt'},
{'fill':'none','stroke-width':'9','stroke':'rgb(56.078431%,56.078431%,56.078431%)', 'name':'side roads 9pt'},
{'fill':'none','stroke-width':'5','stroke':'rgb(60%,60%,60%)', 'name':'side roads B 5pt'},

{'fill':'rgb(70.980392%,89.019608%,70.980392%)','stroke':'none','stroke-width':'0.0','name':'green areas A'},
{'fill':'rgb(78.431373%,98.039216%,80%)','stroke':'none','stroke-width':'0.0', 'name':'green areas B'},
{'fill':'rgb(80.392157%,92.156863%,69.019608%)', 'stroke':'none','stroke-width':'0.0','name':'green areas C'},
{'fill':'rgb(66.666667%,79.607843%,68.627451%)','stroke':'none','stroke-width':'0.0','name':'green areas D'},
{'fill':'rgb(67.843137%,81.960784%,61.960784%)','stroke':'none','stroke-width':'0.0','name':'green TreeArea'},
{'fill':'rgb(78.431373%,84.313725%,67.058824%)','stroke':'none','stroke-width':'0.0','name':'green ShrubArea'},
{'fill':'rgb(66.666667%,87.843137%,79.607843%)','stroke':'rgb(41.568627%,72.941176%,60.784314%)','stroke-width':'0.5','name':'green Recreation'},
{'fill':'rgb(81.568627%,81.568627%,81.568627%)','stroke':'none','stroke-width':'0.0','name':'residential area'},
{'fill':'rgb(71.372549%,70.980392%,57.254902%)','stroke':'none','stroke-width':'0.0','name':'dark green area'},
{'fill':'rgb(91.372549%,90.588235%,88.627451%)','stroke':'rgb(66.666667%,57.254902%,32.941176%)','stroke-width':'0.2','name':'airport area'},

{'fill':'none','stroke':'rgb(66.666667%,82.745098%,87.45098%)','stroke-width':'3', 'name':'creeks stroke'},
{'fill':'none','stroke':'rgb(66.666667%,82.745098%,87.45098%)','stroke-width':'6', 'name':'rivers stroke'},
{'stroke':'none','stroke-width':'0.0','fill':'rgb(66.666667%,82.745098%,87.45098%)', 'name':'water fill'},
{'stroke':'none','stroke-width':'0.0','fill':'rgb(96.078431%,91.372549%,77.647059%)','name':'sand area'}
]


for arg in sys.argv:
	if os.path.isfile(arg) == True:
		
		f = str(arg)
		filename, file_extension = os.path.splitext(f)

		if file_extension == '.svg':
			
			svgAll = open( (str(os.path.dirname(f)) + "\\" + (str(os.path.basename(f)).split(".")[0].strip()) + '_all.svg' ),'w',encoding='utf-8')

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
			fileList={}
			groupList={}

			for d in styleList:
				fileList[d['name']] = open( (str(os.path.dirname(f)) + "\\" + (str(os.path.basename(f)).split(".")[0].strip()) + '_' + d['name'] + '.svg' ), 'w',encoding='utf-8')
				fileList[d['name']].write(xmlProlog)
				fileList[d['name']].write(svgHeader)
				groupList[d['name']] = ET.Element('g')
				groupList[d['name']].set('id',d['name'])
				groupList[d['name']].text=""

			childParser(root)

			svgAll.write(xmlProlog) 
			svgAll.write(svgHeader)

			for e in groupList:
				xmldata = ET.tostring(groupList[e],encoding='unicode',method='xml')
				svgAll.write(xmldata)

			svgAll.write('</svg>')
			svgAll.close()

			#write closing element and close file
			for d in fileList:
			    fileList[d].write('</svg>')
			    fileList[d].close()
		else:
			print('The dropped file is not an svg file, drop only svg files.')
	else:
		print('The dropped file is not a file, drop only svg files.')

input("Done! Press ENTER to close...")
