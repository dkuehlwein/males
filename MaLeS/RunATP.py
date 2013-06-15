'''
Created on Aug 16, 2012

@author: daniel
'''

import shlex,subprocess,os,errno
from collections import deque
from os import kill,getpgid
from os.path import realpath,dirname
from signal import signal,setitimer,ITIMER_REAL,SIGALRM,SIGSTOP,SIGCONT,SIGKILL,SIGTERM
from time import sleep,time

class Alarm(Exception):
    pass
def alarm_handler(signum, frame):
    #print 'Alarm Raised'
    raise Alarm

class RunATP(object):
    def __init__(self,binary,strategy,timeString,time,filename,pause=False,maxTime=300):
        '''
        Constructor
        '''
        self.pause = pause
        self.binary = binary
        self.filename = filename        
        self.strategy = strategy
        self.timeString = timeString
        self.runTime = time
        self.maxTime = maxTime
        self.pid = None
        self.process = None    
        self.time = None    
    
    def run(self):
        '''
        Run a command with a timeout after which it will be forcibly
        killed.
        '''
        signal(SIGALRM, alarm_handler)
        command = '%s %s %s %s' % (self.binary,self.strategy,self.timeString,self.filename) 
        #print command
        args = shlex.split(command)
        startTime = time()
        self.process = subprocess.Popen(args,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,preexec_fn=os.setsid)
        self.pid = self.process.pid
        setitimer(ITIMER_REAL,self.runTime)
        try:
            stdout, _stderr = self.process.communicate()
            setitimer(ITIMER_REAL,0)
        except Alarm:
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
        #print output
        for line in output.split('\n'):
            # FOF - Theorem
            if line.startswith('# SZS status Theorem') or line.startswith('% SZS status Theorem') :
                    proofFound = True
            # CNF Theorem 
            if line.startswith('# SZS status Unsatisfiable'):
                    proofFound = True
            if line.startswith('# SZS status CounterSatisfiable') or line.startswith('% SZS status CounterSatisfiable'):
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
        if self.is_finished():
            return
        try:
            os.kill(-self.pid, SIGTERM)
        except OSError, e:
            if e.errno != errno.ESRCH:
                # If it's not because the process no longer exists,
                # something weird is wrong.
                raise
        sleep(0.01)
        if not self.is_finished(): # Still hasn't exited.
            try:
                os.kill(-self.pid, SIGKILL)
            except OSError, e:
                if e.errno != errno.ESRCH:
                    raise      
        """  
        queue = deque([self.pid])
        while not len(queue) == 0:
            p = queue.popleft()
            command = 'ps -o pid,ppid'
            #print command
            args = shlex.split(command)
            process = subprocess.Popen(args,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,preexec_fn=os.setsid)
            output = process.communicate()[0]
            print p,output
            #print output
            for line in output.split('\n')[1:]:
                line = line.split()
                if not len(line) == 2:
                    continue
                if int(line[1]) == p:
                    queue.append(int(line[0]))
            try: 
                kill(p,SIGTERM)
                kill(p,SIGKILL)
                queue.append(p)
                print p
            except OSError:
                pass
        """
  
if __name__ == '__main__':  
    filename = '/home/daniel/TPTP/TPTP-v5.4.0/Problems/SYO/SYO534^1.p'  
    atp = RunATP('/home/daniel/TPTP/leo2/bin/leo',
                 '--atptimeout 64 --notReplAndrewsEQ --relevancefilter 1 --atp e=/home/daniel/TPTP/E1.7/PROVER/eprover --noslices',
                 #'--atp e=/home/daniel/TPTP/E1.7/PROVER/eprover',
                 '-t 100',
                 5,filename,pause=False)
    print 'start'
    print atp.run()
    print atp.is_finished()
    i = 0
    while True:
        print i,atp.is_finished()
        sleep(1)
        if i == 0:
            atp.start_pause()
            print "Paused"
        elif i == 3:
            print atp.pid,atp.process.pid
            atp.terminate()
            print 'Killed'
            print 'Is finishes?',atp.is_finished()
        elif i == 10:
            print "Continued"
            atp.cont()
        i += 1
        if atp.is_finished():
            print atp.get_output()
            break
    print atp.is_finished()
    print 'Final Sleep'
    #sleep(10)
    #print atp.is_finished()
    
    