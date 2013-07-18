#! /usr/bin/env python

import os,sys,shutil

path = os.path.realpath(os.path.dirname(os.path.abspath(__file__)))
malesPath = os.path.join(path,'MaLeS')
if not malesPath in sys.path:
        sys.path.insert(1, malesPath)

import ConfigParser,argparse
from multiprocessing import cpu_count

parser = argparse.ArgumentParser(description='Automatically creates an INI file for E given its location.')
parser.add_argument('--location', metavar='LOCATION',  
                   help='The E folder. E.g. /home/daniel/TPTP/E')
args = parser.parse_args()

TPTP = os.getenv('TPTP')
if TPTP == None:
    TPTP = '/home/daniel/TPTP/TPTP-v5.4.0'
    print 'ERROR: TPTP Environment variable not defined. Using: %s' % TPTP
if not os.path.exists('tmp'):
    os.mkdir('tmp')    

Eresults = os.path.join('E','results')
if not os.path.exists(Eresults):
    os.mkdir(Eresults)    

shutil.copy(os.path.join(args.location,'classify_problem'),os.path.join(path,'bin'))


config = ConfigParser.SafeConfigParser()
config.optionxform = str
config.add_section('Settings')
config.set('Settings','TPTP',TPTP)
config.set('Settings','TmpDir',os.path.join(path,'tmp')) 
config.set('Settings','Cores',str(cpu_count()-1))
config.set('Settings','ResultsDir',os.path.join(path,'E','results'))
config.set('Settings','ResultsPickle',os.path.join(path,'tmp','results.pickle'))
config.set('Settings','TmpResultsDir',os.path.join(path,'E','resultsTmp'))
config.set('Settings','TmpResultsPickle',os.path.join(path,'tmp','resultsTmp.pickle'))
config.set('Settings','Clear','True')
config.set('Settings','LogToFile','False')
config.set('Settings','LogFile',os.path.join(path,'tmp','satallax.log'))
config.set('Settings','THFSine','False')

config.add_section('Search')
config.set('Search','Time','10')
config.set('Search','Problems',os.path.join(path,'E','data','CASC24Training'))
config.set('Search','FullTime','False')
config.set('Search','TryWithNewDefaultTime','False')
config.set('Search','Walks',str(max(50,cpu_count()-1)))
config.set('Search','WalkLength','10')

config.add_section('Learn')
#config.set('Learn','Time','10')
#config.set('Learn','MaxTime','300')
config.set('Learn','Features','E') # or TPTP
config.set('Learn','FeaturesFile',os.path.join(path,'tmp','features.pickle'))
config.set('Learn','StrategiesFile',os.path.join(path,'tmp','strategies.pickle'))
config.set('Learn','KernelFile',os.path.join(path,'tmp','models.pickle'))
config.set('Learn','RegularizationGrid','0.25,0.5,1,2,4,8,16,32,64')
config.set('Learn','KernelGrid','0.125,0.25,0.5,1,2,4,8,16,32,64')
config.set('Learn','CrossValidate','True')
config.set('Learn','CrossValidationFolds','10')
config.set('Learn','StartStrategies','10')
config.set('Learn','StartStrategiesTime','1.0')
config.set('Learn','CPU Bias','0.3')
config.set('Learn','Tolerance','15.0')

config.add_section('Run')
config.set('Run','CPUSpeedRatio','1.0')
config.set('Run','MinRunTime','1.0')
config.set('Run','PauseProver','False')
config.set('Run','Features','E')
config.set('Run','StrategiesFile',os.path.join(path,'tmp','strategies.pickle'))
config.set('Run','FeaturesFile',os.path.join(path,'tmp','features.pickle'))
config.set('Run','OutputFile','None')

iniLocation = os.path.join(os.path.realpath(os.path.dirname(os.path.abspath(__file__))),'setup.ini')           
with open(iniLocation, 'wb') as configfile:
    config.write(configfile)  

# E Ini
config = ConfigParser.SafeConfigParser()
config.optionxform = str

if not os.path.isfile(os.path.realpath(os.path.join(args.location,'eproof_ram'))):
    print 'Cannot find file: %s' % os.path.realpath(os.path.join(args.location,'eproof_ram'))
    sys.exit(-1)

config.add_section('ATP Settings')
config.set('ATP Settings','binary',os.path.realpath(os.path.join(args.location,'eproof_ram')))
config.set('ATP Settings','time','--cpu-limit=')
config.set('ATP Settings','problem','')
config.set('ATP Settings','strategy','E')
config.set('ATP Settings','default','-s --memory-limit=Auto --tstp-format')

config.add_section('Boolean Parameters')
config.set('Boolean Parameters','--split-aggressive','False')
config.set('Boolean Parameters','--oriented-simul-paramod','False')
config.set('Boolean Parameters','--forward-context-sr','False')
config.set('Boolean Parameters','--destructive-er-aggressive','False')
config.set('Boolean Parameters','--destructive-er','False')
config.set('Boolean Parameters','--split-reuse-defs','False')
config.set('Boolean Parameters','--simul-paramod','False')
config.set('Boolean Parameters','--forward-context-sr-aggressive','False')
config.set('Boolean Parameters','--prefer-initial-clauses','False')
config.set('Boolean Parameters','--presat-simplify','False')
config.set('Boolean Parameters','--sos-uses-input-types','False')

config.add_section('List Parameters')
config.set('List Parameters','--split-clauses','0 1 2 3 4 5 6 7 8 9 10 11 12 13 14 15 16 17 18 19 20 21 22 23 24 25 26 27 28 29 30 31')
config.set('List Parameters','--delete-bad-limit','1500000 150000000 512000000 1024000000')
config.set('List Parameters','--definitional-cnf','0 12 16 24 48')
config.set('List Parameters','-G','unary_first unary_freq arity invarity const_max const_min freq invfreq invconjfreq invfreqconjmax invfreqconjmin invfreqconstmin invfreqhack arrayopt orient_axioms')
config.set('List Parameters','-t','LPO LPO4 KBO KBO6')
config.set('List Parameters','-F','0 1 2')
config.set('List Parameters','-x','Weight StandardWeight RWeight FIFO LIFO Uniq UseWatchlist')
config.set('List Parameters','-c','False 1 2 4 8')
config.set('List Parameters','-w','firstmaximal0 arity aritymax0 modarity modaritymax0 aritysquared aritysquaredmax0 invarity invaritymax0 invaritysquared invaritysquaredmax0 precedence invprecedence precrank5 precrank10 precrank20 freqcount invfreqcount freqrank invfreqrank invconjfreqrank freqranksquare invfreqranksquare invmodfreqrank invmodfreqrankmax0 constant')
config.set('List Parameters','--subsumption-indexing','None Direct Perm PermOpt')
config.set('List Parameters','--fp-index','FP7 NoIndex')
config.set('List Parameters','--sine','False Auto gf200_h_gu_RUU_F100_L20000 gf600_h_gu_R05_F100_L20000 gf120_h_gu_RUU_F100_L00100 gf150_h_gu_RUU_F100_L20000 gf500_h_gu_R04_F100_L20000 gf500_gu_R04_F100_L20000 gf120_gu_RUU_F100_L00500 gf120_gu_R02_F100_L20000 gf150_gu_RUU_F100_L20000 gf120_gu_RUU_F100_L00100 gf600_gu_R05_F100_L20000 gf200_gu_RUU_F100_L20000 gf120_h_gu_RUU_F100_L00500 gf120_h_gu_R02_F100_L20000')
config.set('List Parameters','-H'," ".join(["'(10*ConjectureRelativeSymbolWeight(ConstPrio,0.5,100,100,100,50,1.5,1.5,1.5),1*FIFOWeight(ConstPrio))'",\
             "'(10*ConjectureSymbolWeight(ConstPrio,10,10,5,5,5,1.5,1.5,1.5),1*FIFOWeight(ConstPrio))'",
             "'(1*Clauseweight(PreferProcessed,1,1,1),2*FIFOWeight(PreferProcessed))'",\
             "'(4*ConjectureGeneralSymbolWeight(SimulateSOS,100,100,100,50,50,50,50,1.5,1.5,1),3*ConjectureGeneralSymbolWeight(PreferNonGoals,100,100,100,50,50,1000,100,1.5,1.5,1),1*Clauseweight(PreferProcessed,1,1,1),1*FIFOWeight(PreferProcessed))'",\
             "'(10*ConjectureRelativeSymbolWeight(ConstPrio,0.1,100,100,100,100,1.5,1.5,1.5),1*FIFOWeight(ConstPrio))'",\
             "'(1*FIFOWeight(ConstPrio),1*FIFOWeight(PreferProcessed),1*ConjectureRelativeSymbolWeight(PreferNonGoals,0.5,100,100,100,100,1.5,1.5,1),3*ConjectureRelativeSymbolWeight(SimulateSOS,0.5,100,100,100,100,1.5,1.5,1),10*Refinedweight(SimulateSOS,1,1,2,1.5,2))'",\
             "'(4*ConjectureRelativeSymbolWeight(SimulateSOS,0.5,100,100,100,100,1.5,1.5,1),1*ConjectureRelativeSymbolWeight(PreferNonGoals,0.5,100,100,100,100,1.5,1.5,1),10*Refinedweight(SimulateSOS,1,1,2,1.5,2),1*Refinedweight(PreferNonGoals,1,1,2,1.5,1.5),1*Clauseweight(PreferProcessed,1,1,1),2*FIFOWeight(PreferProcessed))'",\
             "'(6*ConjectureRelativeSymbolWeight(ConstPrio,0.1,100,100,100,100,1.5,1.5,1.5),1*FIFOWeight(ConstPrio),1*FIFOWeight(PreferProcessed),1*ConjectureRelativeSymbolWeight(PreferNonGoals,0.5,100,100,100,100,1.5,1.5,1))'",\
             "'(4*Refinedweight(SimulateSOS,1,1,2,1.5,2),3*Refinedweight(PreferNonGoals,1,1,2,1.5,1.5),1*Clauseweight(PreferProcessed,1,1,1),1*FIFOWeight(PreferProcessed))'",\
             "'(1*FIFOWeight(PreferProcessed),1*FIFOWeight(ConstPrio),2*ConjectureRelativeSymbolWeight(ConstPrio,0.1,100,100,100,100,1.5,1.5,1.5))'",\
             "'(1*FIFOWeight(ConstPrio),8*ConjectureRelativeSymbolWeight(ConstPrio,0.1,100,100,100,100,1.5,1.5,1.5),2*FIFOWeight(PreferProcessed))'",\
             "'(1*FIFOWeight(ConstPrio),4*ConjectureRelativeSymbolWeight(ConstPrio,0.1,100,100,100,100,1.5,1.5,1.5),1*Refinedweight(PreferNonGoals,1,1,2,1.5,1.5),2*FIFOWeight(PreferProcessed))'",\
             "'(1*Refinedweight(PreferNonGoals,1,1,2,1.5,1.5),10*Refinedweight(SimulateSOS,1,1,2,1.5,2),2*FIFOWeight(PreferProcessed),8*ConjectureRelativeSymbolWeight(SimulateSOS,0.5,100,100,100,100,1.5,1.5,1),1*ConjectureRelativeSymbolWeight(ConstPrio,0.1,100,100,100,100,1.5,1.5,1.5),1*FIFOWeight(ConstPrio))'",
             "'(4*ConjectureRelativeSymbolWeight(SimulateSOS,0.5,100,100,100,100,1.5,1.5,1),3*ConjectureRelativeSymbolWeight(PreferNonGoals,0.5,100,100,100,100,1.5,1.5,1),1*Clauseweight(PreferProcessed,1,1,1),1*FIFOWeight(PreferProcessed))'",\
             "'(1*ConjectureRelativeSymbolWeight(SimulateSOS,0.5,100,100,100,100,1.5,1.5,1),1*Clauseweight(PreferProcessed,1,1,1),2*FIFOWeight(PreferProcessed))'",\
             "'(1*FIFOWeight(ConstPrio),2*FIFOWeight(PreferProcessed),1*ConjectureRelativeSymbolWeight(ConstPrio,0.1,100,100,100,100,1.5,1.5,1.5))'",\
             "'(6*ConjectureRelativeSymbolWeight(SimulateSOS,0.5,100,100,100,100,1.5,1.5,1),1*FIFOWeight(ConstPrio),2*Refinedweight(SimulateSOS,1,1,2,1.5,2),2*Refinedweight(PreferNonGoals,1,1,2,1.5,1.5),2*FIFOWeight(PreferProcessed),10*ConjectureRelativeSymbolWeight(ConstPrio,0.1,100,100,100,100,1.5,1.5,1.5),3*ConjectureRelativeSymbolWeight(PreferNonGoals,0.5,100,100,100,100,1.5,1.5,1))'",\
             "'(4*ConjectureGeneralSymbolWeight(SimulateSOS,100,100,100,50,50,10,50,1.5,1.5,1),3*ConjectureGeneralSymbolWeight(PreferNonGoals,200,100,200,50,50,1,100,1.5,1.5,1),1*Clauseweight(PreferProcessed,1,1,1),1*FIFOWeight(PreferProcessed))'",\
             "'(10*ConjectureGeneralSymbolWeight(PreferGroundGoals,100,100,100,50,50,10,50,1.5,1.5,1),1*Clauseweight(ConstPrio,1,1,1),1*Clauseweight(ByCreationDate,2,1,0.8))'",\
             "'(4*Refinedweight(SimulateSOS,1,1,2,1.5,2),3*Refinedweight(PreferNonGoals,1,1,2,1.5,1.5),2*Clauseweight(PreferProcessed,1,1,1),1*FIFOWeight(PreferProcessed))'",
             "'(1*RelevanceLevelWeight(ConstPrio,2,2,0,2,100,100,100,100,1.5,1.5,1))'",\
             "'(4*PNRefinedweight(PreferNonGoals,4,5,5,4,2,1,1),8*PNRefinedweight(PreferGoals,5,2,2,5,2,1,0.5),1*FIFOWeight(ConstPrio))'",\
             "'(10*Refinedweight(PreferGoals,1,2,2,2,0.5),10*Refinedweight(PreferNonGoals,2,1,2,2,2),3*OrientLMaxWeight(ConstPrio,2,1,2,1,1),2*ClauseWeightAge(ConstPrio,1,1,1,3))'",\
             "'(5*Clauseweight(PreferProcessed,1,1,1),1*FIFOWeight(PreferProcessed))'",\
             "'(8*Refinedweight(PreferGoals,1,2,2,2,2),8*Refinedweight(PreferNonGoals,2,1,2,2,0.5),1*Clauseweight(PreferUnitGroundGoals,1,1,1),1*FIFOWeight(ConstPrio))'",\
             "'(10*Refinedweight(PreferGroundGoals,2,1,2,1.0,1),1*Clauseweight(ConstPrio,1,1,1),1*Clauseweight(ByCreationDate,2,1,0.8))'",\
             "'(10*PNRefinedweight(PreferGoals,1,1,1,2,2,2,0.5),10*PNRefinedweight(PreferNonGoals,2,1,1,1,2,2,2),5*OrientLMaxWeight(ConstPrio,2,1,2,1,1),1*FIFOWeight(ConstPrio))'",\
             "'(10*Refinedweight(PreferGoals,1,2,2,2,0.5),10*Refinedweight(PreferNonGoals,2,1,2,2,2),5*OrientLMaxWeight(ConstPrio,2,1,2,1,1),1*FIFOWeight(ConstPrio))'",\
             "'(10*Refinedweight(PreferGoals,1,2,2,2,0.5),10*Refinedweight(PreferNonGoals,2,1,2,2,2),1*Clauseweight(ConstPrio,1,1,1),1*FIFOWeight(ConstPrio))'",\
             "'(8*Refinedweight(PreferGoals,1,2,2,1,0.8),8*Refinedweight(PreferNonGoals,2,1,2,3,0.8),1*Clauseweight(ConstPrio,1,1,0.7),1*FIFOWeight(ByNegLitDist))'",\
             "'(12*Clauseweight(ConstPrio,3,1,1),1*FIFOWeight(ConstPrio))'",\
             "'(4*RelevanceLevelWeight2(PreferGoals,1,2,1,2,100,100,100,400,1.5,1.5,1),3*RelevanceLevelWeight2(PreferNonGoals,0,2,1,2,100,100,100,400,1.5,1.5,1),1*Clauseweight(PreferProcessed,1,1,1),1*FIFOWeight(PreferProcessed))'",\
             "'(4*RelevanceLevelWeight2(SimulateSOS,0,2,1,2,100,100,100,400,1.5,1.5,1),3*ConjectureGeneralSymbolWeight(PreferNonGoals,200,100,200,50,50,1,100,1.5,1.5,1),1*Clauseweight(PreferProcessed,1,1,1),1*FIFOWeight(PreferProcessed))'",\
             "'(10*RelevanceLevelWeight2(SimulateSOS,1,2,1,2,100,100,100,400,1.5,1.5,1),3*ConjectureGeneralSymbolWeight(PreferNonGoals,200,100,200,50,50,1,100,1.5,1.5,1),1*Clauseweight(PreferProcessed,1,1,1),1*FIFOWeight(PreferProcessed))'",\
             "'(4*RelevanceLevelWeight2(SimulateSOS,1,2,0,2,100,100,100,400,1.5,1.5,1),3*ConjectureGeneralSymbolWeight(PreferNonGoals,200,100,200,50,50,1,100,1.5,1.5,1),1*Clauseweight(PreferProcessed,1,1,1),1*FIFOWeight(PreferProcessed))'",\
             "'(4*ConjectureGeneralSymbolWeight(SimulateSOS,100,100,100,50,50,10,50,1.5,1.5,1),3*RelevanceLevelWeight2(ConstPrio,1,2,1,2,100,100,100,400,1.5,1.5,1),1*Clauseweight(PreferProcessed,1,1,1),1*FIFOWeight(PreferProcessed))'",\
             "'(4*RelevanceLevelWeight2(ConstPrio,1,2,1,2,100,100,100,300,1.5,1.5,1),3*ConjectureGeneralSymbolWeight(PreferNonGoals,200,100,200,50,50,1,100,1.5,1.5,1),1*Clauseweight(PreferProcessed,1,1,1),1*FIFOWeight(PreferProcessed))'",\
             "'(10*ConjectureRelativeSymbolWeight(ConstPrio,0.2,100,100,100,100,1.5,1.5,1.5),1*FIFOWeight(ConstPrio))'",\
             "'(7*ConjectureRelativeSymbolWeight(ConstPrio,0.5,100,100,100,100,1.5,1.5,1),1*Clauseweight(PreferProcessed,1,1,1),1*FIFOWeight(PreferProcessed))'",\
             "'(7*ConjectureRelativeSymbolWeight(ConstPrio,0.5,100,100,100,100,1.5,1.5,1),3*OrientLMaxWeight(ConstPrio,2,1,2,1,1),1*FIFOWeight(PreferProcessed))'",\
             "'(5*RelevanceLevelWeight2(ConstPrio,1,2,2,2,100,100,100,300,1.5,1.5,1.5),1*FIFOWeight(PreferProcessed))'",\
             "'(5*RelevanceLevelWeight2(ConstPrio,1,2,1,2,100,100,100,300,1.5,1.5,1),1*FIFOWeight(PreferProcessed))'",\
             "'(5*RelevanceLevelWeight2(SimulateSOS,2,2,0,2,100,100,100,100,1.5,1.5,1),1*FIFOWeight(PreferProcessed))'",\
             "'(20*ConjectureRelativeSymbolWeight(ConstPrio,0.1,100,100,100,100,1.5,1.5,1.5),1*Refinedweight(PreferNonGoals,2,1,2,3,0.8),1*FIFOWeight(ConstPrio))'",\
             "'(10*ConjectureRelativeSymbolWeight(ConstPrio,0.1,100,100,100,100,1.5,1.5,1.5),3*ConjectureRelativeSymbolWeight(ConstPrio,0.3,100,100,100,100,2.5,1,1),1*FIFOWeight(ConstPrio))'",\
             "'(4*ConjectureGeneralSymbolWeight(SimulateSOS,100,100,100,50,50,0,50,1.5,1.5,1),3*ConjectureGeneralSymbolWeight(PreferNonGoals,100,100,100,50,50,0,100,1.5,1.5,1),1*Clauseweight(PreferProcessed,1,1,1),1*FIFOWeight(PreferProcessed))'"]))
config.set('List Parameters','-W'," ".join(["NoSelection","NoGeneration","SelectNegativeLiterals","PSelectNegativeLiterals","SelectPureVarNegLiterals","PSelectPureVarNegLiterals",\
             "SelectLargestNegLit","PSelectLargestNegLit","SelectSmallestNegLit","PSelectSmallestNegLit","SelectLargestOrientable","PSelectLargestOrientable",\
             "MSelectLargestOrientable","SelectSmallestOrientable","PSelectSmallestOrientable","MSelectSmallestOrientable","SelectDiffNegLit","PSelectDiffNegLit",\
             "SelectGroundNegLit","PSelectGroundNegLit","SelectOptimalLit","PSelectOptimalLit","SelectMinOptimalLit","PSelectMinOptimalLit",\
             "SelectMinOptimalNoTypePred","PSelectMinOptimalNoTypePred","SelectMinOptimalNoXTypePred","PSelectMinOptimalNoXTypePred","SelectMinOptimalNoRXTypePred",\
             "PSelectMinOptimalNoRXTypePred","SelectCondOptimalLit","PSelectCondOptimalLit","SelectAllCondOptimalLit","PSelectAllCondOptimalLit",\
             "SelectOptimalRestrDepth2","PSelectOptimalRestrDepth2","SelectOptimalRestrPDepth2","PSelectOptimalRestrPDepth2","SelectOptimalRestrNDepth2",\
             "PSelectOptimalRestrNDepth2","SelectNonRROptimalLit","PSelectNonRROptimalLit","SelectNonStrongRROptimalLit","PSelectNonStrongRROptimalLit",\
             "SelectAntiRROptimalLit","PSelectAntiRROptimalLit","SelectNonAntiRROptimalLit","PSelectNonAntiRROptimalLit","SelectStrongRRNonRROptimalLit",\
             "PSelectStrongRRNonRROptimalLit","SelectUnlessUniqMax","PSelectUnlessUniqMax","SelectUnlessPosMax","PSelectUnlessPosMax","SelectUnlessUniqPosMax",\
             "PSelectUnlessUniqPosMax","SelectUnlessUniqMaxPos","PSelectUnlessUniqMaxPos","SelectComplex","PSelectComplex","SelectComplexExceptRRHorn",\
             "PSelectComplexExceptRRHorn","SelectLComplex","PSelectLComplex","SelectMaxLComplex","PSelectMaxLComplex","SelectMaxLComplexNoTypePred",\
             "PSelectMaxLComplexNoTypePred","SelectMaxLComplexNoXTypePred","PSelectMaxLComplexNoXTypePred","SelectComplexPreferNEQ","PSelectComplexPreferNEQ",\
             "SelectComplexPreferEQ","PSelectComplexPreferEQ","SelectComplexExceptUniqMaxHorn","PSelectComplexExceptUniqMaxHorn","MSelectComplexExceptUniqMaxHorn",\
             "SelectNewComplex","PSelectNewComplex","SelectNewComplexExceptUniqMaxHorn","PSelectNewComplexExceptUniqMaxHorn","SelectMinInfpos","PSelectMinInfpos",\
             "HSelectMinInfpos","GSelectMinInfpos","SelectMinInfposNoTypePred","PSelectMinInfposNoTypePred","SelectMin2Infpos","PSelectMin2Infpos",\
             "SelectComplexExceptUniqMaxPosHorn","PSelectComplexExceptUniqMaxPosHorn","SelectUnlessUniqMaxSmallestOrientable","PSelectUnlessUniqMaxSmallestOrientable",\
             "SelectDivLits","SelectDivPreferIntoLits","SelectMaxLComplexG","SelectMaxLComplexAvoidPosPred","SelectMaxLComplexAvoidPosUPred","SelectComplexG",\
             "SelectComplexAHP","PSelectComplexAHP","SelectNewComplexAHP","PSelectNewComplexAHP","SelectComplexAHPExceptRRHorn","PSelectComplexAHPExceptRRHorn",\
             "SelectNewComplexAHPExceptRRHorn","PSelectNewComplexAHPExceptRRHorn","SelectNewComplexAHPExceptUniqMaxHorn","PSelectNewComplexAHPExceptUniqMaxHorn",\
             "SelectNewComplexAHPNS","SelectVGNonCR"]))

iniLocation = os.path.join(os.path.realpath(os.path.dirname(os.path.abspath(__file__))),'ATP.ini')           
with open(iniLocation, 'wb') as configfile:
    config.write(configfile) 
#"""
# Parse defined modes and extract min/max values
strategiesConfig = ConfigParser.SafeConfigParser()
strategiesConfig.optionxform = str
modesPath = os.path.join('E','resultsTmp')
modes = os.listdir(modesPath)
for mode in modes:
    # TODO: ONLY FOR CASC SETUP
    localStrategiesConfig = ConfigParser.SafeConfigParser()
    localStrategiesConfig.optionxform = str
    
    strategiesConfig.add_section(mode)
    localStrategiesConfig.add_section(mode)       
    params = open(os.path.join(modesPath,mode)).readlines()[0][1:]
    option = ''
    resultsLocation = os.path.join(os.path.realpath(os.path.dirname(os.path.abspath(__file__))),'E','results',mode+'.results')
    OS = open(resultsLocation,'w')
    lines = open(os.path.join(modesPath,mode)).readlines()
    OS.write("".join(lines[1:]))
    OS.close()
    for param in params.split():
        if param.startswith('--'):
            if len(param.split('=')) == 1:
                option = param
                value = 'True'
                if param == '--tstp-in':
                    continue
            else:
                option = param.split('=')[0]
                value = param.split('=')[1]
        elif param.startswith('-'):
            option = param[:2]
            value = param[2:]
            if param == '-s':
                continue
        else:
            print 'Unknown parameter in %s' % mode
        strategiesConfig.set(mode, option, value)
        localStrategiesConfig.set(mode, option, value)
    iniLocation = os.path.join(os.path.realpath(os.path.dirname(os.path.abspath(__file__))),'E','results',mode)           
    with open(iniLocation, 'wb') as configfile:
        localStrategiesConfig.write(configfile)           
iniLocation = os.path.join(os.path.realpath(os.path.dirname(os.path.abspath(__file__))),'strategies.ini')           
with open(iniLocation, 'wb') as configfile:
    strategiesConfig.write(configfile)            
#"""
   
