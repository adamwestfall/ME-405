# -*- coding: utf-8 -*-
"""
Created on Fri Oct 15 14:07:04 2021

@author: jason
"""

'''@file                       task_user.py
   @brief                      User interface task for cooperative multitasking example.
   @details                    Implements a finite state machine
'''

import utime, pyb, gc
from micropython import const

## List of possible encoder states
S0_init = const(0)
S1_waitForInput = const(1)

class Task_User():
    '''@brief                       User interface task for cooperative multitasking example.
       @details                     Implements a finite state machine
    '''
    
    def __init__(self, taskID, period, encoder_share, output_share, delta_share, motor_share, dbg=False):
        '''@brief                   Constructs an LED task.
           @details                 The LED task is implemented as a finite state
                                    machine.
           @param name              The name of the task
           @param period            The period, in microseconds, between runs of 
                                    the task.
           @param encoder_share     A shares.Share object used to hold instructions
                                    for the encoder.
           @param dbg               A boolean flag used to enable or disable debug
                                    messages printed over the VCP
        '''
        ## The name of the task
        self.taskID = taskID
        ## The period (in us) of the task
        self.period = period
        ## A shares.Share object representing encoder
        self.encoder_share = encoder_share
        
        ## A shares.Share object representing the encoder output
        self.output_share = output_share
        
        self.delta_share = delta_share
        
        self.motor_share = motor_share
        
        ## A flag indicating if debugging print messages display
        self.dbg = dbg
        
        ## A serial port to use for user I/O
        ## A virtual "bucket" in which to dump user input
        ## Reading from 'ser' is like checking the bucket for any new input, only
        ## we don't halt the program in event that none is entered
        self.ser = pyb.USB_VCP()
        
        ## The state to run on the next iteration of the finite state machine
        self.state = S0_init
        ## The number of runs of the state machine
        # self.runs = 0
        
        ## The utime.ticks_us() value associated with the next run of the FSM
        self.next_time = utime.ticks_add(utime.ticks_us(), self.period)
        
        # the list where the times are stored
        self.times = []
        self.offsetTime = 0
        
        # the list where the positions are stored
        self.positions = []
        # the list where the deltas are stored
        self.deltas = []
        
        # SHOULD NOT NEED THE GARBAGE COLLECTOR!!!!!!!!!!!
        gc.enable()
        
    def run(self):
        '''@brief                   Runs one iteration of the FSM
        '''
        gc.collect()
        current_time = utime.ticks_us()
        if (utime.ticks_diff(current_time, self.next_time) >= 0):
            if self.state == S0_init:
                
                # displaying the menu and then advancing to state 1 of the
                # task_user FSM
                self.displayMenu()
                self.transition_to(S1_waitForInput)       
                
        # we have to change the value in the VCM, otherwise the program will run in an inifinite loop
        # this is why we are reading letters and writing/sharing numbers
            elif self.state == S1_waitForInput:
                if (self.ser.any()):
                    char_in = self.ser.read(1).decode()
                    if (char_in == 'z'):
                        # passing the character to the task_encoder
                        self.encoder_share.write(1)
                            
                    elif (char_in == 'Z'):
                        self.encoder_share.write(6)
                        
                    elif(char_in == 'p'):
                        self.encoder_share.write(2)
                        
                    elif (char_in == 'P'):
                        self.encoder_share.write(7)
                        
                    elif (char_in == 'd'):
                        self.encoder_share.write(3)
                        
                    elif (char_in == 'D'):
                        self.encoder_share.write(8)
                        
                    elif (char_in == 'm'):
                        self.motor_share.write(9)
                    
                    elif (char_in == 'M'):
                        self.motor_share.write(10)
                        
                    elif (char_in == 'x' or char_in == 'X'):
                        self.motor_share.write(12)
                        
                    elif (char_in == 'y' or char_in == 'Y'):
                        self.motor_share.write(13)
                        
                    elif (char_in == 'c' or char_in == 'C'):
                        self.motor_share.write(0)
                    
                    elif (char_in == 'g'):
                        print ('Beginning encoder 1 data collection...')
                        self.start_time = current_time    
                        self.encoder_share.write(4)    
                            
                    elif (char_in == 'G'):
                        print ('Beginning encoder 2 data collection...')
                        self.start_time = current_time    
                        self.encoder_share.write(12)    
                            
                    elif (char_in == 's' or char_in == 'S'):
                        self.haltDataGathering()
                    
                    elif (char_in == 'e' or char_in == 'E'):
                        self.motor_share.write(11)
                        
                    elif (char_in == 'h' or char_in == 'H'):
                        self.displayMenu()
                    
                    # input validation done here
                    else:
                        print('Command \'{:}\' is invalid.'.format(char_in))
                
                #gathering data
                if (self.encoder_share.read() == 'k'):
                    self.gatherData(current_time, 4)
                  
                elif (self.encoder_share.read() == 'j'):
                    self.gatherData(current_time, 12)
                    
            else:
                raise ValueError('Invalid State')
            
            self.next_time = utime.ticks_add(self.next_time, self.period)
            # self.runs += 1
    
    def displayMenu(self):
        
        print()
        print('         Please select an option from the menu (case sensitive):')
        print ("+-------------------------------------------------------------------+")
        print ('| [z]     Zero encoder 1 position                                   |')
        print ('| [Z]     Zero encoder 2 position                                   |')
        print ('| [p]     Display encoder 1 position                                |')
        print ('| [P]     Display encoder 2 position                                |')
        print ('| [d]     Display delta for encoder 1                               |')
        print ('| [D]     Display delta for encoder 2                               |')
        print ('| [m]     Modify duty cycle for motor 1                             |')
        print ('| [M]     Modify duty cycle for motor 2                             |')
        print ('| [x/X]   Shortcut: Set both motors to max FWD                      |')
        print ('| [y/Y]   Shortcut: Set both motors to max REV                      |')
        print ('| [g]     Collect encoder 1 data for 30 seconds and display output  |')
        print ('| [G]     Collect encoder 2 data for 30 seconds and display output  |')
        print ('| [s/S]   End data collection prematurely                           |')
        print ('| [e/E]   Enable / Disable motors                                   |')
        print( "+-------------------------------------------------------------------+")
        print ('| [c/C]   Clear fault condition                                     |')
        print ('| [h/H]   Print this menu to the console                            |')        
        print ('| Ctrl+c  Terminate the program                                     |')
        print ("+-------------------------------------------------------------------+\n")
    
    ## this function cleans numeric output prior to printing it to the summary
    ## Rounds decimals to the two places and appends trailing zeros as necessary
    def formatNumeric(self, value, numPlaces):
        value = str(value)
        charArray = [char for char in value]
        
        decimalIndex = -1
        decimal = []
        
        for index in range(len(charArray)):
            if (charArray[index] == '.'):
                decimalIndex = index
            if (decimalIndex >= 0):
                decimal.append(charArray[index])
        
        whole = value[0:decimalIndex]
        dec = ''
                
        if (len(decimal) == 1):
            decimal.append('0')
            decimal.append('0')
        elif (len(decimal) == 2):
            decimal.append('0')
        elif (len(decimal) > 3):
            hun = decimal[2]
            thou = decimal[3]
            
            if (int(thou) >= 5):
                hun = int(hun) + 1
            dec = ''.join(decimal[0:3])
        
        value = whole + dec
        
        return value
    
    def gatherData(self, current_time, code):
        # print('adding an entry')
        gc.collect()
        self.times.append((current_time - self.start_time)/1000000)
        self.positions.append(self.output_share.read())
        self.deltas.append(self.delta_share.read())
        self.output_share.write(None)
        self.delta_share.write(None)
        # print("time diff: {0}".format((utime.ticks_diff(current_time, self.start_time)/1000000)))
        if ((utime.ticks_diff(current_time, self.start_time)/1000000) < 30.00):
            self.encoder_share.write(code)
        else:
            # print('Time is up')
            # self.encoder_share.write('s')
            self.haltDataGathering()
    
    def haltDataGathering(self):
        gc.collect()
        print('************************** Data Output ****************************')
        print('-------------------------------------------------------------------')
        print('Time [s]        Position [rad]        Delta [rad/s]')
        
        #cycling through the output list to display it on the screen
        
        for i in range(0, len(self.times)):
            print("{0} ,          {1} ,                   {2}".format(self.formatNumeric(self.times[i], 2), self.positions[i], self.deltas[i]))
                            
        print('***End of data collection\n')
        self.encoder_share.write(None) # clear the encoder share
        self.output_share.write(None) # clear the output share
        
        # clearing the arrays
        self.times = [] 
        self.positions = [] 
        self.deltas = [] 
        gc.collect()
    
    def transition_to(self, new_state):
        '''@brief                   Transitions the FSM to a new state
           @details                 Optionally a debugging message can be printed
                                    if the dbg flag is set when the task object is created.
           @param                   new_state The state to transition to.
        '''
        if (self.dbg):
            print('{:}: S{:}->S{:}'.format(self.taskID ,self.state,new_state))
        self.state = new_state