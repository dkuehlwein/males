#! /usr/bin/env python


import os,sys

path = os.path.realpath(os.path.dirname(os.path.abspath(__file__)))
malesPath = os.path.join(path,'MaLeS')
if not malesPath in sys.path:
        sys.path.insert(1, malesPath)

import ConfigParser,argparse,shutil
from multiprocessing import cpu_count

parser = argparse.ArgumentParser(description='Automatically creates an INI file for LEO-II given its location.')
parser.add_argument('--location', metavar='LOCATION',  
                   help='The LEO-II folder. E.g. /home/daniel/TPTP/leo2')
args = parser.parse_args()

TPTP = os.getenv('TPTP')
if TPTP == None:
    TPTP = '/home/daniel/TPTP/TPTP-v5.4.0'
    print 'ERROR: TPTP Environment variable not defined. Using: %s' % TPTP
if not os.path.exists('tmp'):
    os.mkdir('tmp')    

config = ConfigParser.SafeConfigParser()
config.optionxform = str
config.add_section('Settings')
config.set('Settings','TPTP',TPTP)
config.set('Settings','TmpDir',os.path.join(path,'tmp')) 
config.set('Settings','Cores',str(cpu_count()-1))
config.set('Settings','ResultsDir',os.path.join(path,'Leo','results'))
config.set('Settings','ResultsPickle',os.path.join(path,'tmp','results.pickle'))
config.set('Settings','TmpResultsDir',os.path.join(path,'resultsTmp'))
config.set('Settings','TmpResultsPickle',os.path.join(path,'tmp','resultsTmp.pickle'))
config.set('Settings','Clear','True')
config.set('Settings','LogToFile','False')
config.set('Settings','LogFile',os.path.join(path,'tmp','leo.log'))
config.set('Settings','THFSine','False')


config.add_section('Search')
config.set('Search','Time','10')
config.set('Search','Problems',os.path.join(path,'Leo','data','CASC24Training'))
config.set('Search','FullTime','False')
config.set('Search','TryWithNewDefaultTime','False')
config.set('Search','Walks',str(max(50,cpu_count()-1)))
config.set('Search','WalkLength','5')

config.add_section('Learn')
#config.set('Learn','Time','10')
#config.set('Learn','MaxTime','300')
config.set('Learn','Features','TPTP') # or TPTP
config.set('Learn','FeaturesFile',os.path.join(path,'tmp','features.pickle'))
config.set('Learn','StrategiesFile',os.path.join(path,'tmp','strategies.pickle'))
config.set('Learn','KernelFile',os.path.join(path,'tmp','models.pickle'))
config.set('Learn','RegularizationGrid','0.25,0.5,1,2,4,8,16,32,64')
config.set('Learn','KernelGrid','0.125,0.25,0.5,1,2,4,8,16,32,64')
config.set('Learn','CrossValidate','True')
config.set('Learn','CrossValidationFolds','10')
config.set('Learn','StartStrategies','5')
config.set('Learn','StartStrategiesTime','1.0')
config.set('Learn','CPU Bias','0.3')
config.set('Learn','Tolerance','1.0')

config.add_section('Run')
config.set('Run','CPUSpeedRatio','1.0')
config.set('Run','MinRunTime','1.0')
config.set('Run','PauseProver','False')
config.set('Run','Features','TPTP')
config.set('Run','StrategiesFile',os.path.join(path,'tmp','strategies.pickle'))
config.set('Run','FeaturesFile',os.path.join(path,'tmp','features.pickle'))
config.set('Run','OutputFile','None')

iniLocation = os.path.join(os.path.realpath(os.path.dirname(os.path.abspath(__file__))),'setup.ini')           
with open(iniLocation, 'wb') as configfile:
    config.write(configfile)  

config = ConfigParser.SafeConfigParser()
config.optionxform = str
Eloc = raw_input('Please enter the location of E. E.g. /scratch/kuehlwein/E1.7/PROVER/eprover: ')

config.add_section('ATP Settings')
config.set('ATP Settings','binary',os.path.realpath(os.path.join(args.location,'bin','leo')))
config.set('ATP Settings','time','-t')
config.set('ATP Settings','problem','')
config.set('ATP Settings','strategy','Leo')
config.set('ATP Settings','default','--atp e='+Eloc+' --noslices')

config.add_section('Boolean Parameters')
val = 'False'
config.set('Boolean Parameters','--expand_exuni',val)
config.set('Boolean Parameters','--notReplLeibnizEQ',val)
config.set('Boolean Parameters','--notReplAndrewsEQ',val)
config.set('Boolean Parameters','--notUseChoice',val)
config.set('Boolean Parameters','--notExtuni',val)
config.set('Boolean Parameters','--notUseExtCnfCmbd',val)
config.set('Boolean Parameters','--unfolddefsearly',val)
config.set('Boolean Parameters','--unfolddefslate',val)

config.add_section('List Parameters')
config.set('List Parameters','--atptimeout','0.2 0.5 1.0 2.0 4.0 8.0 16 32 64')
config.set('List Parameters','--primsubst','0 1 2 3 4')
config.set('List Parameters','--relevancefilter','0 1 2 3 4 5 6')
config.set('List Parameters','--order','none naive')
config.set('List Parameters','--translation','kerber fully-typed fof_experiment tff_experiment fof_full fof_experiment_erased')
config.set('List Parameters','--unidepth','0 1 2 3 4 5 6 7 8 9 10 11 12 13 14 15')

# Parse defined modes and extract min/max values
strategies = ConfigParser.SafeConfigParser()
strategies.optionxform = str
strategies.add_section('defaultMode')
iniFile = os.path.join(os.path.realpath(os.path.dirname(os.path.abspath(__file__))),'ATP.ini')
with open(iniFile, 'wb') as configfile:
    config.write(configfile)            
iniLocation = os.path.join(os.path.realpath(os.path.dirname(os.path.abspath(__file__))),'strategies.ini')           
with open(iniLocation, 'wb') as configfile:
    strategies.write(configfile)            