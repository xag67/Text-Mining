#!/usr/bin/python

import sys
import os
import glob
import re 
import math

#! Check input -------------------------------------------------------------------------------------------
if len(sys.argv) > 4 and len(sys.argv) < 2:
	sys.stderr.write("--Usage : tf-idf folderName \n--use  -t for trace \n \t\t -o for tresholded output \n")
	sys.exit(1)

if sys.argv == 3 and (sys.argv[1] != "-t" or sys.argv[1] != "-o"):
	sys.stderr.write("--Usage : tf-idf -t -o folderName \n--use  -t for trace \n \t\t -o for tresholded output \n")
	sys.exit(1)

if sys.argv == 4 and sys.argv[1] != "t" and sys.argv[2] != "-o" :
	sys.stderr.write("--Usage : tf-idf -t -o folderName \n--use  -t for trace \n \t\t -o for tresholded output \n")
	sys.exit(1)

#! end check input--------------------------------------------------------------------------------------

def readFolder(Folder):						#! Open a folder and return list of file path
	if(Folder[(len(Folder)-1)] != '/'):
		Folder = Folder + "/"
	Folder = Folder + "*"
	return glob.glob(Folder)

def normalize(open_file) :				#! return a word list after removing non letter.
	word_list = open_file.read()
	word_list = re.sub("[()]|,|\.|\t|\n|\r","",word_list)
	word_list = word_list.split(" ")
	if(word_list[len(word_list)-1] == "" or word_list[len(word_list)-1] == " "):
		del word_list[len(word_list)-1]
	return word_list

def normalize_trace(open_file) :	#! return call list after finding them in trace
	word_list = []
	for line in open_file :
		call = line.split("(")
		word_list.append(call[0])
	del word_list[len(word_list)-1]
	return word_list

def buildTfDico (word_list,size) :    # build term frequency dico
	tf_dico = {}
	for word in word_list :
		if word in tf_dico :
			tf_dico[word] = tf_dico[word] + 1.0 
		else : 
			tf_dico[word] = 1.0
	for element in tf_dico :
		tf_dico[element] = (tf_dico[element] / size)*100
	return tf_dico

def getTf(File):				#! term frenquency for one file
	opened_file = open(File,"r")
	if sys.argv[1] == "-t" :	
		word_list = normalize_trace(opened_file)
	else :
		word_list = normalize(opened_file)
	tf_dico = buildTfDico(word_list,len(word_list))
	opened_file.close()
	return tf_dico

def getTfAll(list_file):		#! term frequency for all file 
	list_tf = []
	for file in list_file :
		list_tf.append(getTf(file))
	return list_tf

def buildLargeDico(list_cf):		#! necessary for idf score. Build all word dico
	large_dico = {}
	for dico in list_cf:
		for word in dico :
			if word in large_dico :
				large_dico[word] = large_dico[word]+1
			else :
				large_dico[word] = 1
	return large_dico
	
def getIdf(list_tf):						#! calculate idf score
	large_dico = buildLargeDico(list_tf)
	number_doc = len(list_tf)
	dico_idf = {}
	for word in large_dico:
		dico_idf[word] = math.log10(number_doc / large_dico[word])
	return dico_idf

def getTfIdfScore(list_tf,dico_idf):    #! build final score for all
	score_list = list_tf
	i = 0
	for dico in list_tf:
		for word in dico:
			score_list[i][word] = dico[word] * dico_idf[word]
		i = i + 1
	return score_list

def threeBest(dico) :				#! bad search for bad function display :/
	to_display = { 'first' : 0 ,'nameFirst': 'default' ,'second' : 0, 'nameSecond': 'default', "third" : 0, 'nameThird': 'default' }
	for word in dico :
		if dico[word] > to_display['first'] :
			to_display['third'] = to_display['second']
			to_display['nameThird'] = to_display['nameSecond']
			to_display['second'] = to_display['first']
			to_display['nameSecond'] = to_display['nameFirst']
			to_display['first'] = dico[word]
			to_display['nameFirst'] = word
		else :
			if dico[word] > to_display['second']:
					to_display['third'] = to_display['second']
					to_display['nameThird'] = to_display['nameSecond']
					to_display['second'] = dico[word]
					to_display['nameSecond'] = word
			else :
				if dico[word] > to_display['third']:
							to_display['third'] = dico[word]
							to_display['nameThird'] = word
	return to_display

def treshold(dico):						#! take only score > 0.5
	treated = {}
	for word in dico :
		if dico[word] > 0.5 :
			treated[word] = dico[word]
	return treated

def find_best(dico):					#!search the best score for file name
	name = ""
	best = 0
	for word in dico :
		if dico[word] > best :
			best = dico[word]
			name = word
	return name

def write(dico):							#! create and write a file in output directory
	where = os.path.abspath("output/")
	name = find_best(dico)
	filee = open(where+"/"+name,"w")
	for word in dico :
		filee.write(str(word) + ":"+str(dico[word])+"\n")
	filee.close()
	return

def makeText(score_list):				#! create and write all files in ouptut directory
	treated = {}
	for dico in score_list :
		treated = treshold(dico)
		write(treated)
	return 
		
		
def affiche(score_list): 					#! Bad display function :/
	i = 1
	for dico in score_list:
		to_display = threeBest(dico)
		print("--------file"+str(i)+"-------")
		print("| "+to_display['nameFirst']+" | "+str(to_display['first']))
		print("| "+to_display['nameSecond']+" | "+str(to_display['second']))
		print("| "+to_display['nameThird']+" | "+str(to_display['third']))
		print("----------------------------")
		i = i +1
		

def main() : 
	if sys.argv[1] == "-t" :						#! need to change for a switch of sys.argv[1] , but i'm fed up
		folder = os.path.abspath(sys.argv[2])
	else:
		folder = os.path.abspath(sys.argv[1])
		
	if sys.argv[1] == "-o" :
		folder = os.path.abspath(sys.argv[2])
	else:
		folder = os.path.abspath(sys.argv[1])
	list_file = readFolder(folder)
	list_tf = getTfAll(list_file)
	dico_idf = getIdf(list_tf)
	score_list = getTfIdfScore(list_tf,dico_idf)
	if sys.argv[1] == "-o" :
		makeText(score_list)		
	if len(list_tf):
		affiche(score_list)
	return 
	



main()
	

