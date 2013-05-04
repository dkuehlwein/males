#! /usr/bin/env python

import os,ConfigParser
from multiprocessing import cpu_count

TPTP = os.getenv('TPTP')
if TPTP == None:
    TPTP = '/home/daniel/TPTP/TPTP-v5.4.0'
    print 'ERROR: TPTP Environment variable not defined using: %s' % TPTP
    

path = os.path.realpath(os.path.dirname(os.path.abspath(__file__)))

config = ConfigParser.SafeConfigParser()
config.optionxform = str
config.add_section('Settings')
config.set('Settings','TPTP',TPTP)
config.set('Settings','TmpDir',os.path.join(path,'tmp')) # '/scratch/kuehlwein/tmp/'
config.set('Settings','LogFile',os.path.join(path,'tmp','satallax.log')) 
config.set('Settings','Cores',str(cpu_count()-1))
config.set('Settings','ResultsDir',os.path.join(path,'results'))
config.set('Settings','ResultsPickle',os.path.join(path,'tmp','results.pickle'))
config.set('Settings','TmpResultsDir',os.path.join(path,'resultsTmp'))
config.set('Settings','TmpResultsPickle',os.path.join(path,'tmp','resultsTmp.pickle'))
config.set('Settings','Clear','False')

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
config.set('Learn','Features','E') # or TPTP
config.set('Learn','FeatureFile',os.path.join(path,'tmp','features.pickle'))
config.set('Learn','StrategiesFile',os.path.join(path,'tmp','strategies.pickle'))
config.set('Learn','ModelsFile',os.path.join(path,'tmp','models.pickle'))
config.set('Learn','RegularizationGrid','0.25,0.5,1,2,4,8,16,32,64')
config.set('Learn','KernelGrid','0.125,0.25,0.5,1,2,4,8,16,32,64')
config.set('Learn','CrossValidate','True')
config.set('Learn','CrossValidationFolds','10')
config.set('Learn','StartStrategies','10')
config.set('Learn','StartStrategiesTime','1.0')
config.set('Learn','CPU Bias','0.3')
config.set('Learn','Tolerance','0.3')

iniLocation = os.path.join(os.path.realpath(os.path.dirname(os.path.abspath(__file__))),'setup.ini')           
with open(iniLocation, 'wb') as configfile:
    config.write(configfile)  
