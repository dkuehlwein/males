'''
Created on May 18, 2013

@author: Daniel Kuehlwein
'''

import shlex, subprocess,os
from os.path import dirname, realpath

def thf_sine(inFile, outFile):
    malesPath = dirname(dirname(realpath(__file__)))
    # Run fakefof.pl
    inFileName = os.path.basename(inFile)
    #inFileName = inFile.split('/')[-1]
    fakeFOFFile = os.path.join(malesPath,'tmp',inFileName+'.fakefof')
    #print fakeFOFFile
    fakeFOFStream = open(fakeFOFFile,'w')
    command = os.path.join(malesPath,'bin','fakefof.pl') + ' ' + inFile 
    #print command
    args = shlex.split(command)
    #p = subprocess.Popen(args,stdout=subprocess.PIPE,stderr=subprocess.STDOUT).stdout
    p = subprocess.Popen(args,stdout=fakeFOFStream,stderr=subprocess.STDOUT,cwd = os.path.join(malesPath,'bin'))   
    p.wait()
    
    # Run e_axfilter
    command = os.path.join(malesPath,'bin','e_axfilter') + ' ' + fakeFOFFile 
    #print command
    args = shlex.split(command)
    #p = subprocess.Popen(args,stdout=subprocess.PIPE,stderr=subprocess.STDOUT).stdout
    p = subprocess.Popen(args,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,cwd = os.path.join(malesPath,'bin')).stdout   
    lines = p.readlines()
    p.close() 
    sineFiles = []
    for line in lines[1:]:
        line = line.split()
        sineFiles.append(os.path.join(malesPath,'bin',line[-1].strip()))
    
    # Get picked axioms:
    pickedAxioms = []
    sineFile = sineFiles[0]
    IS = open(sineFile,'r')
    lines = IS.readlines()
    IS.close()
    #print lines
    for line in lines:
        line = line.split(',')
        axiomName = line[0][4:] 
        pickedAxioms.append(axiomName)
    #print pickedAxioms     
    pickedAxioms = set(pickedAxioms)
    
    # Create new problem, with only the picked axioms
    includesToProcess = []
    OS = open(outFile,'w')
    IS = open(inFile,'r')
    problemLines = IS.readlines()
    IS.close()

    foundFormula = False
    for line in problemLines:
        if line.startswith('include('):
            include = line[9:-4]
            TPTP = os.getenv('TPTP', 'ERROR')
            include = os.path.join(TPTP,include)
            includesToProcess.append(include)
                
    for includeFile in includesToProcess:
        IS = open(includeFile,'r')
        foundFormula = False
        for line in IS.readlines():
            if line.startswith('include('):
                include = line[9:-4]
                TPTP = os.getenv('TPTP', 'ERROR')
                include = os.path.join(TPTP,include)
                includesToProcess.append(include)
            if line.startswith('thf'):
                name = line.split(',')[0]
                name = name[4:]
                THFtype = line.split(',')[1]   
                #print THFtype, THFtype == 'type'             
                if name in pickedAxioms or THFtype == 'type':                
                    foundFormula = True
            if foundFormula:
                OS.write(line)
                if line.strip().endswith(').'):
                    foundFormula = False
                
        IS.close() 
        
    foundFormula = False
    for line in problemLines:
        if line.startswith('thf'):
            name = line.split(',')[0]
            name = name[4:]
            THFtype = line.split(',')[1]
            #print THFtype, THFtype == 'type'
            if name in pickedAxioms or THFtype == 'type':                
                foundFormula = True
        if foundFormula:
            OS.write(line)
            if line.strip().endswith(').'):
                foundFormula = False
                
               
    OS.close()
    # CleanUp
    os.remove(fakeFOFFile)
    for sineFile in sineFiles:
        os.remove(sineFile)

if __name__ == '__main__':
    os.environ['TPTP'] = '/home/daniel/TPTP/TPTP-v5.4.0'
    testFile = '/home/daniel/TPTP/TPTP-v5.4.0/Problems/PUZ/PUZ087^1.p'
    
    outFile = 'testTHFSine'
    thf_sine(testFile,outFile)