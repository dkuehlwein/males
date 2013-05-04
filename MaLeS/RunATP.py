'''
Created on Aug 16, 2012

@author: daniel
'''

import shlex,subprocess
from os import kill
from os.path import realpath,dirname
from signal import signal,setitimer,ITIMER_REAL,SIGALRM,SIGSTOP,SIGCONT,SIGKILL
from time import sleep,time

class Alarm(Exception):
    pass
def alarm_handler(signum, frame):
    #print 'Alarm Raised'
    raise Alarm

class RunATP(object):
    def __init__(self,binary,strategy,timeParam,runTime,filename,pause=False,maxTime=300):
        '''
        Constructor
        '''
        self.pause = pause
        self.binary = binary
        self.filename = filename        
        self.strategy = strategy
        self.runTime = runTime
        self.maxTime = maxTime
        self.timeParam = timeParam
        self.pid = None
        self.process = None    
        self.time = None    
    
    def run(self):
        '''
        Run a command with a timeout after which it will be forcibly
        killed.
        '''
        signal(SIGALRM, alarm_handler)
        command = '%s %s %s %s %s' % (self.binary,self.strategy,self.timeParam,self.maxTime,self.filename) 
        #print command
        args = shlex.split(command)
        startTime = time()
        self.process = subprocess.Popen(args,stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
        self.pid = self.process.pid
        setitimer(ITIMER_REAL,self.runTime)
        #print self.runTime
        try:
            stdout, _stderr = self.process.communicate()
            setitimer(ITIMER_REAL,0)
        except Alarm:
            #print 'x'
            if self.pause:
                self.start_pause()
            else:                
                self.terminate()                
            return False,False,None,self.runTime
        endTime = time()
        usedTime = endTime-startTime
        proofFound,countersat,output = self.parse_output(stdout)
        return proofFound,countersat,output,usedTime 
    
    def parse_output(self,output):
        proofFound = False
        countersat = False
        for line in output.split('\n'):
            # FOF - Theorem
            if line.startswith('# SZS status Theorem') or line.startswith('% SZS status Theorem') :
                    proofFound = True
            # CNF Theorem 
            if line.startswith('# SZS status Unsatisfiable'):
                    proofFound = True
            if line.startswith('# SZS status CounterSatisfiable'):
                    countersat = True
            """
            if line.startswith('# Total time'):
                    tmp = line.split()
                    self.time = float(tmp[4])
            """
        return proofFound,countersat,output

       
    def is_finished(self):
        if self.process.poll() == None:
            return False
        return True        
    
    def get_output(self):
        output = self.process.communicate()[0]        
        return self.parse_output(output)
    
    def start_pause(self):
        if not self.is_finished():
            kill(self.pid, SIGSTOP)
 
    def cont(self,runTime):
        if self.is_finished():
            return False,False,None,runTime
        signal(SIGALRM, alarm_handler)
        setitimer(ITIMER_REAL,runTime)    
        kill(self.pid, SIGCONT)
        try:
            stdout, _stderr = self.process.communicate()
            setitimer(ITIMER_REAL,0) 
        except Alarm:
            if self.pause:
                self.start_pause()
            else:
                self.terminate()
            return False,False,None,runTime
        return self.parse_output(stdout)
    
    def terminate(self):        
        # TODO: There has to be a better way            
        command = 'ps h --ppid %s -o pid' % (self.pid)
        args = shlex.split(command)
        process = subprocess.Popen(args,stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
        output = process.communicate()[0]            
        pids = [int(p) for p in output.split()]
        # Grandchildren 
        for p in pids:
            command = 'ps h --ppid %s -o pid' % (p)
            args = shlex.split(command)
            process = subprocess.Popen(args,stdout=subprocess.PIPE,stderr=subprocess.STDOUT)                
            pids.extend([int(p) for p in (process.communicate()[0]).split()])
        for p in pids:
            try: 
                kill(p,SIGKILL)
            except OSError:
                pass
        if not self.is_finished():            
            self.process.kill()
        

if __name__ == '__main__':  
    filename = '/home/daniel/TPTP/TPTP-v5.4.0/Problems/SEV/SEV308^5.p'  
    atp = RunATP('/home/daniel/TPTP/satallax-2.7/bin/satallax.opt','-m mode274','-t',5,filename,pause=True)
    atp.run()
    print atp.is_finished()
    i = 0
    while True:
        print i,atp.is_finished()
        sleep(1)
        if i == 0:
            atp.start_pause()
            print "Paused"
        elif i == 3:
            atp.terminate()
            print 'Killed'
        elif i == 10:
            print "Continued"
            atp.cont()
        i += 1
        if atp.is_finished():
            print atp.get_output()
            break
    print 'Final Sleep'
    sleep(10)
    print atp.is_finished()
    
    