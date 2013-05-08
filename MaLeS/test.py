'''
Created on May 3, 2013

@author: daniel
'''

import ConfigParser,os,sys
from readData import get_TPTP_features, get_e_features,compute_features

if __name__ == '__main__':
    newfileplus = open('FOFeligible', 'w')
    newfiledach = open('THFeligible', 'w')
    
    GuteDateienplus = []
    GuteDateiendach = []
    TolleDateien = []
    
    Ordner = os.listdir('/home/daniel/TPTP/TPTP-v5.4.0/Problems/')
    #Liste mit Ordnern
    for folder in Ordner:
        Dateipfad = '/home/daniel/TPTP/TPTP-v5.4.0/Problems/' + folder +'/'
        #print Dateipfad
    
        dateien = os.listdir(Dateipfad)
        #Liste mit Dateien in Ordner
        for datei in dateien:
            if ('+' or '^' in datei) and (not datei.endswith('.rm')) :
                tolleDatei = Dateipfad + datei
                #wenn + oder ^ vorkommt ist es eine tolle Datei :)
                TolleDateien.append(tolleDatei)
                #neue Liste mit dem ganzen Pfad zur Datei 
        
    #print TolleDateien
    weirdTHF = 0        
    for tolleDatei in TolleDateien:
        Inputfile = open(tolleDatei, 'r')
        lines = Inputfile.readlines()
        
        for line in lines:
            if (line.startswith('% Rating')):
                splits = line.split()
                rating = splits[3]
                #print rating
    
        if (rating is '?'):
            if '+' in tolleDatei:
                GuteDateienplus.append(tolleDatei)
            if '^' in tolleDatei:
                GuteDateiendach.append(tolleDatei)
                weirdTHF +=1 
        else:
            if (float(rating) > 0.21):
                #print 'Gute Datei: ' + tolleDatei
                if '+' in tolleDatei:
                    GuteDateienplus.append(tolleDatei)
                if '^' in tolleDatei:
                    GuteDateiendach.append(tolleDatei)
    
    print weirdTHF
    sys.exit()
    GuterStringplus=str(GuteDateienplus)
    GuterStringdach=str(GuteDateiendach)
    
    import random
    
    pickedFOF = random.sample(set(GuteDateienplus),1000)
    pickedTHF = random.sample(set(GuteDateiendach),1000)
    
    for x in pickedTHF:
        newfiledach.write(x+'\n')
    
    for x in pickedFOF:
        newfileplus.write(x+'\n')
        
    
    newfileplus.close()
    newfiledach.close()
    Inputfile.close()     
    
    """
    binary = '/home/daniel/TPTP/satallax-2.7/bin/satallax.opt'
    
    modes = os.listdir('../results')
    for mode in modes:
        if mode.startswith('.'):
            continue
        name = mode
        IS = open('../results/'+mode,'r')
        lines = IS.readlines()
        IS.close()
        
        print lines
        print lines[1:]
        OS = open('../resultsTmp/' + name + '.results' ,'w')
        for line in lines[1:]:
            OS.write(line)
        OS.close()
        parameters = {}
        x = lines[0][1:].split()
        print x
        for y in x:
            y = y.split('-')
            parameters[y[0]] = y[1]
        
        modeFile = '../resultsTmp/'+mode 
        OS = open(modeFile,'w')
        OS.write('['+mode+']\n')
        for param,val in parameters.items():
            OS.write(param+' = ' + str(val).lower()+'\n')            
        OS.close()
    #"""
    
    """
    stratConfig = ConfigParser.SafeConfigParser()
    stratConfig.optionxform = str
    stratConfig.read('/home/daniel/workspace/MaLeS/Satallax/strategies.ini')
    stratConfig.read('/home/daniel/workspace/MaLeS/resultsTmp/NewStrategy25')
    #"""
    
    """
    x = '/home/daniel/TPTP/TPTP-v5.4.0/Problems/PUZ/PUZ081^1.p'
    x1 = '/home/daniel/TPTP/TPTP-v5.4.0/Problems/PUZ/PUZ001+1.p'
    
    print get_TPTP_features(x)
    print get_TPTP_features(x1)
    print get_e_features(x)
    print get_e_features(x1)
    featureDict,maxVals,minVals =  compute_features([x,x1],'E')
    print featureDict
    print maxVals
    print minVals
    #"""