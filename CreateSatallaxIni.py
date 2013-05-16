#! /usr/bin/env python
'''
CreateSatallaxIni

Automatically creates an INI file for Satallax given its location. 

Created on May 2, 2013

@author: Daniel Kuehlwein
'''

import argparse,os,ConfigParser,sys

def create_ini(location,iniFile = '../ATP.ini'):
    # Parse default flags
    flagsFile = os.path.join(location,'src','flags.ml')
    flagsStream = open(flagsFile)
    config = ConfigParser.SafeConfigParser()
    config.optionxform = str
    
    config.add_section('ATP Settings')
    config.set('ATP Settings','binary',os.path.realpath(os.path.join(location,'bin','satallax.opt')))
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
    modesPath = os.path.join(location,'modes')
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
                config.set('Int Min Parameters',option,str(val))
                config.set('Int Max Parameters',option,str(val))
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
    with open(iniFile, 'wb') as configfile:
        config.write(configfile)            
    iniLocation = os.path.join(os.path.realpath(os.path.dirname(os.path.abspath(__file__))),'strategies.ini')           
    with open(iniLocation, 'wb') as configfile:
        strategies.write(configfile)            

parser = argparse.ArgumentParser(description='Automatically creates an INI file for Satallax given its location.')
parser.add_argument('location', metavar='LOCATION',  
                   help='The Satallax folder. E.g. /home/daniel/TPTP/satallax-2.7')
if __name__ == '__main__':
    args = parser.parse_args()
    iniFile = os.path.join(os.path.realpath(os.path.dirname(os.path.abspath(__file__))),'ATP.ini')
    sys.exit(create_ini(args.location,iniFile))




