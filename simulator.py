'''
CS5250 Assignment 4, Scheduling policies simulator
Sample skeleton program
Input file:
    input.txt
Output files:
    FCFS.txt
    RR.txt
    SRTF.txt
    SJF.txt
'''
import sys

input_file = 'input.txt'

class Process:
    def __init__(self, id, arrive_time, burst_time):
        self.id = id
        self.arrive_time = arrive_time
        self.burst_time = burst_time
    #for printing purpose
    def __repr__(self):
        return ('[id %d : arrival_time %d,  burst_time %d]'%(self.id, self.arrive_time, self.burst_time))

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

class ActiveProcess:
    def __init__(self, id, arrive_time, burst_time):
        self.id = id
        self.arrive_time = arrive_time
        self.burst_time = burst_time
        self.remaining_burst_time = burst_time
        self.predicted_burst_time = 5
        self.last_scheduled_time = 0

    def __repr__(self):
        return ('{id %d : arrival_time %d,  burst_time %d, remaining_burst_time %d, last_scheduled_time %d, predicted_burst_time %f}' \
            %(self.id, self.arrive_time, self.burst_time, self.remaining_burst_time, self.last_scheduled_time, self.predicted_burst_time))

    @classmethod
    def to_active_process(cls, new_process):
        temp_process = cls(new_process.id, new_process.arrive_time, new_process.burst_time)
        temp_process.last_scheduled_time = temp_process.arrive_time
        return temp_process


def find_time_quantum(process_list):
    result = [(RR_scheduling(process_list, time_slice)[1], time_slice)
        for time_slice in range(1, 31)
    ]
    return result

def RR_scheduling(process_list, time_quantum ):
    schedule = []
    current_time = 0
    waiting_time = 0
    active_queue = []
    index = 0
    cur_process = None

    while (len(active_queue) > 0 or index < len(process_list)):
        if len(active_queue) > 0:
            pre_process = cur_process
            cur_process = active_queue.pop(0)

            waiting_time += current_time - cur_process.last_scheduled_time
            # check if same process
            if pre_process is None or cur_process.id != pre_process.id:
                schedule.append((current_time, cur_process.id))
            completed = False
            if cur_process.remaining_burst_time <= time_quantum:
                completed = True
                current_time += cur_process.remaining_burst_time
                cur_process.remaining_burst_time = 0
            else:
                current_time += time_quantum
                cur_process.remaining_burst_time -= time_quantum
                cur_process.last_scheduled_time = current_time

            while (index < len(process_list) and process_list[index].arrive_time <= current_time):
                new_process = process_list[index]         
                active_queue.append(ActiveProcess.to_active_process(new_process))
                index += 1

            if not completed:
                active_queue.append(cur_process)

        else:
            next_process = process_list[index]
            active_queue.append(ActiveProcess.to_active_process(next_process))
            current_time = next_process.arrive_time
            index += 1

    average_waiting_time = waiting_time/float(len(process_list))
    return schedule, average_waiting_time


def SRTF_scheduling(process_list):
    schedule = []
    active_queue = []
    current_time = 0
    waiting_time = 0
    index = 0
    cur_process = None

    while len(active_queue) > 0 or index < len(process_list):
        if len(active_queue) > 0:
            active_queue = sorted(active_queue, key = lambda p: p.remaining_burst_time)
            pre_process = cur_process
            cur_process = active_queue.pop(0)
            
            # in case no process can be scheduled
            current_time = max(current_time, cur_process.arrive_time)
            waiting_time += current_time - cur_process.last_scheduled_time

            # check if same process
            if pre_process is None or cur_process.id != pre_process.id:
                schedule.append((current_time, cur_process.id))

            interrupt_time = process_list[index].arrive_time if index < len(process_list) else float('inf')
            
            if cur_process.remaining_burst_time <= interrupt_time - current_time:
                current_time += cur_process.remaining_burst_time
                cur_process.remaining_burst_time = 0
            else:
                cur_process.remaining_burst_time -= (interrupt_time - current_time)
                current_time = interrupt_time
                cur_process.last_scheduled_time = current_time
                # add current task first
                active_queue.append(cur_process)
                # add new one
                active_queue.append(ActiveProcess.to_active_process(process_list[index]))
                index += 1
        else:
            active_queue.append(ActiveProcess.to_active_process(process_list[index]))
            index += 1

    average_waiting_time = waiting_time/float(len(process_list))
    return schedule, average_waiting_time


def find_alpha(process_list):
    alpha_candidates = [0.05*i for i in range(21)]
    result = [(SJF_scheduling(process_list, alpha)[1], alpha)
        for alpha in alpha_candidates
    ]
    return result


def SJF_scheduling(process_list, alpha):
    schedule = []
    active_queue = []
    current_time = 0
    waiting_time = 0
    cur_process = None
    index = 0

    burst_time_hist = dict()

    while len(active_queue) > 0 or index < len(process_list):
        if len(active_queue) > 0:
            for id, pre_burst_time in burst_time_hist.items():
                for active_process in active_queue:
                    if active_process.id == id:
                        active_process.predicted_burst_time = pre_burst_time
                        break

            active_queue = sorted(active_queue, key=lambda p: p.predicted_burst_time)
            cur_process = active_queue.pop(0)

            schedule.append((current_time, cur_process.id))
            waiting_time += (current_time - cur_process.last_scheduled_time)
            # wait until cur_process run to end 
            current_time += cur_process.remaining_burst_time
            cur_process.last_scheduled_time = current_time
            # predict next burst time
            cur_process.predicted_burst_time = alpha * cur_process.remaining_burst_time + (1-alpha) * cur_process.predicted_burst_time
            burst_time_hist[cur_process.id] = cur_process.predicted_burst_time
            # check any new process to add
        
            while index < len(process_list) and process_list[index].arrive_time < current_time:
                active_queue.append(ActiveProcess.to_active_process(process_list[index]))
                index += 1     
        else:
            active_queue.append(ActiveProcess.to_active_process(process_list[index]))
            current_time = process_list[index].arrive_time
            index += 1


    average_waiting_time = waiting_time/float(len(process_list))
    return schedule, average_waiting_time

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
    
    # find optimal time slice
    print(find_time_quantum(process_list))

    # find optimal alpha
    print(find_alpha(process_list))


'''
def test(argv):
    process_list = read_input()
    print ("printing input ----")
    for process in process_list:
        print (process)
    print ("simulating FCFS ----")
    FCFS_schedule, FCFS_avg_waiting_time =  FCFS_scheduling(process_list)
    write_output('FCFS.txt', FCFS_schedule, FCFS_avg_waiting_time )
    print ("simulating RR ----")
    RR_schedule, RR_avg_waiting_time =  RR_scheduling(process_list,time_quantum = 8)
    write_output('RR.txt', RR_schedule, RR_avg_waiting_time )

    print ("simulating SRTF ----")
    SRTF_schedule, SRTF_avg_waiting_time =  SRTF_scheduling(process_list)
    write_output('SRTF.txt', SRTF_schedule, SRTF_avg_waiting_time )

    print ("simulating SJF ----")
    SJF_schedule, SJF_avg_waiting_time =  SJF_scheduling(process_list, alpha = 0.5)
    write_output('SJF.txt', SJF_schedule, SJF_avg_waiting_time )
'''

if __name__ == '__main__':
    main(sys.argv[1:])
    


