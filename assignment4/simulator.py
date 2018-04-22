'''
CS5250 Assignment 4, Scheduling policies simulator
Sample skeleton program
Author: Minh Ho
Input file:
    input.txt
Output files:
    FCFS.txt
    RR.txt
    SRTF.txt
    SJF.txt

Apr 10th Revision 1:
    Update FCFS implementation, fixed the bug when there are idle time slices between processes
    Thanks Huang Lung-Chen for pointing out
Revision 2:
    Change requirement for future_prediction SRTF => future_prediction shortest job first(SJF), the simpler non-preemptive version.
    Let initial guess = 5 time units.
    Thanks Lee Wei Ping for trying and pointing out the difficulty & ambiguity with future_prediction SRTF.
'''
import sys
import copy

input_file = 'input.txt'

class Process:
    last_scheduled_time = 0
    def __init__(self, id, arrive_time, burst_time):
        self.id = id
        self.arrive_time = arrive_time
        self.burst_time = burst_time
        self.used_time = 0  # total excuted time 
        self.wait_time =0   # total wait time 
        self.finish_time = 0  # finish time 
        self.remain_time = burst_time # remaining time , initial value is same as burst_time
        self.predict_time = 5  # predict time, inital value is 5
   

    def setUsedTime(self, x):
        self.used_time = x
        
    def getUsedTime(self):
        return self.used_time

    def setWaitingTime(self, x):
        self.wait_time = x
        
    def getWaitingTime(self):
        return self.wait_time

    def getRestRequireTime(self):
        return self.burst_time - self.used_time
    
    #for printing purpose
    def __repr__(self):
        return ('[id %d : arrive_time %d,  burst_time %d]'%(self.id, self.arrive_time, self.burst_time))

def FCFS_scheduling(process_list):
    #store the (switching time, proccess_id) pair
    schedule = []
    current_time = 0
    waiting_time = 0
    for process in process_list:
        if(current_time < process.arrive_time):
            current_time = process.arrive_time
        schedule.append((current_time,process.id))
        waiting_time = waiting_time + (current_time - process.arrive_time)
        current_time = current_time + process.burst_time
    average_waiting_time = waiting_time/float(len(process_list))
    return schedule, average_waiting_time

#Input: process_list, time_quantum (Positive Integer)
#Output_1 : Schedule list contains pairs of (time_stamp, proccess_id) indicating the time switching to that proccess_id
#Output_2 : Average Waiting Time
def RR_scheduling(queue , time_quantum ):
    process_list =[]
    schedule = []
    startTime  =0
    finishTime  =0
    wait_queue = []
    ready_queue = []
    process_list=copy.deepcopy(queue)
    queueSize = len(process_list)
    averageWaitTime =0


    while (not (len(wait_queue) == 0 and len(ready_queue) == 0 and len(process_list) == 0)):
        
        while(len(process_list) != 0 and process_list[0].arrive_time <= finishTime ):
            ready_queue.append(process_list[0])
            process_list.pop(0)

        
        if (len(ready_queue) != 0):
            process = ready_queue[0]
            ready_queue.pop(0)
        elif(len(process_list) != 0 and len(wait_queue) == 0 ):
            process = process_list[0]
            process_list.pop(0)
        else:
            process = wait_queue[0]
            wait_queue.pop(0)


        startTime = max(process.arrive_time,finishTime);
        finishTime = startTime + time_quantum;

        process.setUsedTime(process.getUsedTime()+time_quantum);


        if(process.getRestRequireTime() > 0):
            wait_queue.append(process)
        else:
            finishTime = finishTime + process.getRestRequireTime();
            
                
        if(process.getUsedTime()>time_quantum) :  
            process.setWaitingTime(startTime-process.getUsedTime()+ time_quantum - process.arrive_time)
        else :
            process.setWaitingTime(startTime-process.arrive_time)

        schedule.append((startTime,process.id))
    
        averageWaitTime += process.getWaitingTime();

    averageWaitTime /=queueSize
        
    return schedule, averageWaitTime



def SRTF_scheduling(queue):
    schedule = []
    runtime  =0
    done_queue = []
    ready_queue = []
    averageWaitTime =0
    modified=False
    running=None
    process_list = []
    queueSize = len(queue)
    
    process_list=copy.deepcopy(queue)
    for process in process_list:
        if process.arrive_time <= runtime: # If arrival time is less/equal to runtime submit
            ready_queue.append(process) # those processes to the ready queue
            j =process_list.index(process) # Get the index of the value
            process_list.pop(j)



    ready_queue= sorted(ready_queue, key=lambda process: process.remain_time)
    #print('first process is ', ready_queue[0].id)
    while (len(done_queue) < queueSize):
        modified =False
        #print('--------start checking------------- ')
        if(len(ready_queue) == 0):
            #print('idle')
            runtime+=1
            for process in process_list:
                if process.arrive_time<= runtime: # If arrival time is less/equal to runtime submit
                    #print('ready_queue added 1 is ', process.id)
                    ready_queue.append(process) # those processes to the ready queue
                    j =process_list.index(process) # Get the index of the value
                    process_list.pop(j)
        else:
            running = ready_queue[0].id
            #print('current running process is ', ready_queue[0].id)
            while modified == False:
                #print('runtime is ',runtime)
                schedule.append((runtime,ready_queue[0].id))
                runtime+=1
                ready_queue[0].used_time +=1
                ready_queue[0].remain_time -= 1
                
                for index in range(len(ready_queue)): #Increases processes in ready queue wait times
                    if index !=0:
                        ready_queue[index].wait_time+=1

            
                if ready_queue[0].used_time==ready_queue[0].burst_time: #Process has terminated its self
                    #print('finish process is ', ready_queue[0].id,ready_queue[0].used_time )
                    ready_queue[0].finish_time=runtime 
                    done_queue.append(ready_queue[0]) #Put process in the done queue
                    #print('add process  ', ready_queue[0].id, ' to done queue')
                    ready_queue.pop(0) #Process gives up CPU
                    modified=True

                for process in process_list:
                    if process.arrive_time <= runtime: # If arrival time is less/equal to runtime submit
                        #print('ready_queue added is ', process.id)
                        ready_queue.append(process) # those processes to the ready queue
                        j = process_list.index(process) # Get the index of the value
                        process_list.pop(j)

    
                ready_queue = sorted(ready_queue, key=lambda process: process.remain_time)
                

                
                if len(ready_queue)==0:
                    #print('ready_queue  is 0  ')
                    modified=True

                elif running!=ready_queue[0].id:
                    #print('new running process  is  ',ready_queue[0].id)
                    modified=True
                #else:
                    #print('ready_queue sorted is ')
                    #for index in range(len(ready_queue)):
                        #print('------', ready_queue[index].id, 'remaining is ',ready_queue[index].remain_time)
               
 
    for index in range(len(done_queue)):
      averageWaitTime+=done_queue[index].wait_time

    averageWaitTime /= queueSize
    
    return schedule, averageWaitTime

def SJF_scheduling(queue, alpha):
    #print('----------start--SJF_scheduling------- ')
    schedule = []
    runtime  =0
    done_queue = []
    ready_queue = []
    averageWaitTime =0
    modified=False
    running=None
    process_list = []
    queueSize = len(queue)


    process_list=copy.deepcopy(queue)
    process_list = sorted(process_list, key=lambda process: process.arrive_time)
    
    #calculate the predict_time
    for index in range(len(process_list)):
        if index > 0 and index < len(process_list):
            process_list[index].predict_time = process_list[index-1].burst_time * alpha + (1- alpha)*process_list[index-1].predict_time
            #print('------', process_list[index].id, ' --- predict time is ',process_list[index].predict_time)
       
    for process in process_list:
        if process.arrive_time <= runtime: # If arrival time is less/equal to runtime submit
            ready_queue.append(process) # those processes to the ready queue
            j =process_list.index(process) # Get the index of the value
            process_list.pop(j)

    
    while (len(done_queue) < queueSize):
        
        #print('----------start--------- ')
        if(len(ready_queue) == 0):
            #print('idle')
            runtime+=1
            for process in process_list:
                if process.arrive_time<= runtime: # If arrival time is less/equal to runtime submit
                    #print('ready_queue added 1 is ', process.id)
                    ready_queue.append(process) # those processes to the ready queue
                    j =process_list.index(process) # Get the index of the value
                    process_list.pop(j)
        else:
            
            # sort by the predict time 
            ready_queue= sorted(ready_queue, key=lambda process: process.predict_time)
            
            #for index in range(len(ready_queue)):
                #print('------', ready_queue[index].id, 'predict is ',ready_queue[index].predict_time)
            #print('current running process is ', ready_queue[0].id)
            while ready_queue[0].used_time != ready_queue[0].burst_time:
                schedule.append((runtime,ready_queue[0].id))
                #print('runtime-------- ', runtime)
                runtime+=1
                ready_queue[0].used_time +=1

                
                for index in range(len(ready_queue)): #Increases processes in ready queue wait times
                    if index !=0:
                        ready_queue[index].wait_time+=1

            
                for process in process_list:
                    if process.arrive_time <= runtime: # If arrival time is less/equal to runtime submit
                        #print('ready_queue added is ', process.id)
                        ready_queue.append(process) # those processes to the ready queue
                        j = process_list.index(process) # Get the index of the value
                        process_list.pop(j)

            done_queue.append(ready_queue[0]) #Put process in the done queue
            #print('add process  ', ready_queue[0].id, ' to done queue')
            ready_queue.pop(0)
                
 
    for index in range(len(done_queue)):
      averageWaitTime+=done_queue[index].wait_time

    averageWaitTime /= queueSize
    
    return schedule, averageWaitTime



def read_input():
    result = []
    with open(input_file) as f:
        for line in f:
            array = line.split()
            if (len(array)!= 3):
                print ("wrong input format")
                exit()
            result.append(Process(int(array[0]),int(array[1]),int(array[2])))
    return result
def write_output(file_name, schedule, avg_waiting_time):
    with open(file_name,'w') as f:
        for item in schedule:
            f.write(str(item) + '\n')
        f.write('average waiting time %.2f \n'%(avg_waiting_time))


def main(argv):
    process_list = read_input()
    print ("printing input ----")
    for process in process_list:
        print (process)
    print ("simulating FCFS ----")
    FCFS_schedule, FCFS_avg_waiting_time =  FCFS_scheduling(process_list)
    write_output('FCFS.txt', FCFS_schedule, FCFS_avg_waiting_time )
    print ("simulating RR ----")
    RR_schedule, RR_avg_waiting_time =  RR_scheduling(process_list,time_quantum = 2)
    write_output('RR.txt', RR_schedule, RR_avg_waiting_time )
    print ("simulating SRTF ----")
    SRTF_schedule, SRTF_avg_waiting_time =  SRTF_scheduling(process_list)
    write_output('SRTF.txt', SRTF_schedule, SRTF_avg_waiting_time )
    print ("simulating SJF ----")
    SJF_schedule, SJF_avg_waiting_time =  SJF_scheduling(process_list, alpha = 0.5)
    write_output('SJF.txt', SJF_schedule, SJF_avg_waiting_time )

if __name__ == '__main__':
    main(sys.argv[1:])
