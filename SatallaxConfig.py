#! /usr/bin/env python

import os,ConfigParser,argparse,shutil
from multiprocessing import cpu_count

parser = argparse.ArgumentParser(description='Automatically creates an INI file for Satallax given its location.')
parser.add_argument('--location', metavar='LOCATION',  
                   help='The Satallax folder. E.g. /home/daniel/TPTP/satallax-2.7')
args = parser.parse_args()

TPTP = os.getenv('TPTP')
if TPTP == None:
    TPTP = '/home/daniel/TPTP/TPTP-v5.4.0'
    print 'ERROR: TPTP Environment variable not defined. Using: %s' % TPTP
if not os.path.exists('tmp'):
    os.mkdir('tmp')    

path = os.path.realpath(os.path.dirname(os.path.abspath(__file__)))

config = ConfigParser.SafeConfigParser()
config.optionxform = str
config.add_section('Settings')
config.set('Settings','TPTP',TPTP)
config.set('Settings','TmpDir',os.path.join(path,'tmp')) 
config.set('Settings','Cores',str(cpu_count()-1))
config.set('Settings','ResultsDir',os.path.join(path,'results'))
config.set('Settings','ResultsPickle',os.path.join(path,'tmp','results.pickle'))
config.set('Settings','TmpResultsDir',os.path.join(path,'resultsTmp'))
config.set('Settings','TmpResultsPickle',os.path.join(path,'tmp','resultsTmp.pickle'))
config.set('Settings','Clear','True')
config.set('Settings','LogToFile','False')
config.set('Settings','LogFile',os.path.join(path,'tmp','satallax.log'))
config.set('Settings','THFSine','True')


config.add_section('Search')
config.set('Search','Time','10')
config.set('Search','Problems',os.path.join(path,'Satallax','data','CASC24Training'))
config.set('Search','FullTime','False')
config.set('Search','TryWithNewDefaultTime','False')
config.set('Search','Walks',str(max(50,cpu_count()-1)))
config.set('Search','WalkLength','10')

config.add_section('Learn')
config.set('Learn','Time','10')
config.set('Learn','MaxTime','300')
config.set('Learn','Features','TPTP') # or TPTP
config.set('Learn','FeaturesFile',os.path.join(path,'tmp','features.pickle'))
config.set('Learn','StrategiesFile',os.path.join(path,'tmp','strategies.pickle'))
config.set('Learn','ModelsFile',os.path.join(path,'tmp','models.pickle'))
config.set('Learn','RegularizationGrid','0.25,0.5,1,2,4,8,16,32,64')
config.set('Learn','KernelGrid','0.125,0.25,0.5,1,2,4,8,16,32,64')
config.set('Learn','CrossValidate','True')
config.set('Learn','CrossValidationFolds','10')
config.set('Learn','StartStrategies','20')
config.set('Learn','StartStrategiesTime','0.5')
config.set('Learn','CPU Bias','0.3')
config.set('Learn','Tolerance','0.1')

config.add_section('Run')
config.set('Run','CPUSpeedRatio','1.0')
config.set('Run','MinRunTime','0.1')
config.set('Run','PauseProver','False')
config.set('Run','Features','TPTP')
config.set('Run','StrategiesFile',os.path.join(path,'tmp','strategies.pickle'))
config.set('Run','FeaturesFile',os.path.join(path,'tmp','features.pickle'))
config.set('Run','OutputFile','None')

iniLocation = os.path.join(os.path.realpath(os.path.dirname(os.path.abspath(__file__))),'setup.ini')           
with open(iniLocation, 'wb') as configfile:
    config.write(configfile)  

# Copy Modes and moels
for mode in os.listdir(os.path.join('Satallax','modes')):
    shutil.copy(os.path.join('Satallax','modes',mode),os.path.join(args.location,'modes'))
for model in os.listdir(os.path.join('Satallax','models')):
    shutil.copy(os.path.join('Satallax','models',model),'tmp')

    
# Parse default flags
flagsFile = os.path.join(args.location,'src','flags.ml')
flagsStream = open(flagsFile)
config = ConfigParser.SafeConfigParser()
config.optionxform = str

config.add_section('ATP Settings')
config.set('ATP Settings','binary',os.path.realpath(os.path.join(args.location,'bin','satallax.opt')))
config.set('ATP Settings','time','-t')
config.set('ATP Settings','problem','')
config.set('ATP Settings','strategy','Satallax')
config.set('ATP Settings','default','')

config.add_section('Boolean Parameters')
config.add_section('Int Def Parameters')
config.add_section('Int Min Parameters')
config.add_section('Int Max Parameters')        
for line in flagsStream.readlines():
    line = line.split()
    if len(line) > 0 and line[0] == 'Hashtbl.add':            
        option = line[2][1:-1]
        val = line[3].strip()[:-1]
        if (line[1] == 'bool_flags'):
            # EXCEPTIONs
            if option == 'BASETYPESFINITE':
                continue
            if option == 'BASETYPESTOPROP':
                continue
            
            config.set('Boolean Parameters',option,val)
        if (line[1] == 'int_flags'):
            # EXCEPTIONs
            if option == 'BASETYPESMAXSIZE':
                continue
            
            config.set('Int Def Parameters',option,val)
            config.set('Int Min Parameters',option,val)
            config.set('Int Max Parameters',option,val)

# Parse defined modes and extract min/max values
strategies = ConfigParser.SafeConfigParser()
strategies.optionxform = str
modesPath = os.path.join(args.location,'modes')
modes = os.listdir(modesPath)
for mode in modes:
    strategies.add_section(mode)
    modeFile = os.path.join(modesPath,mode)
    lines = open(modeFile).readlines()
    option = ''
    expectingIntValue = False
    expectingBoolValue = False
    for line in lines:
        if expectingIntValue:
            expectingIntValue = False
            val = int(line.strip())
            minVal = config.getint('Int Min Parameters', option)
            maxVal = config.getint('Int Max Parameters', option)            
            if val < minVal:
                minVal = val
            if val > maxVal:
                maxVal = val
            config.set('Int Min Parameters',option,str(minVal))
            config.set('Int Max Parameters',option,str(maxVal))
            strategies.set(mode,option,str(val))                    
        if config.has_option('Int Def Parameters', line.strip()):
            expectingIntValue = True
            option = line.strip()
            
        if expectingBoolValue:
            expectingBoolValue = False
            strategies.set(mode,option,line.strip())
        if config.has_option('Boolean Parameters', line.strip()):
            expectingBoolValue = True
            option = line.strip()

config.remove_section('Int Def Parameters')
iniFile = os.path.join(os.path.realpath(os.path.dirname(os.path.abspath(__file__))),'ATP.ini')
with open(iniFile, 'wb') as configfile:
    config.write(configfile)            
iniLocation = os.path.join(os.path.realpath(os.path.dirname(os.path.abspath(__file__))),'strategies.ini')           
with open(iniLocation, 'wb') as configfile:
    strategies.write(configfile)            