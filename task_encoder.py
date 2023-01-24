# -*- coding: utf-8 -*-
"""
Created on Thu Oct 14 13:13:05 2021

@author: Jason Davis
"""

import utime, pyb, math
from micropython import const

## List of possible encoder states
S0_init = const(0)
S1_zeroEncoder = const(1)
S2_displayEncoderPosition = const(2)
S3_displayEncoderDelta = const(3)
S4_gatherEncoderData = const(4)
S5_haltDataCollection = const(5)

class Task_Encoder():
    '''@brief                               Receives input from the user interface via "main" and executes the request
       @details                             Accepts input from the user and handles the request.  Since input arrives pre-validated,
                                            no character/data validation is performed here
    '''
    
    def __init__(self, taskID, period, encoder, encoder_share, output_share, delta_share, dbg = False):
        
        ## The name of the task
        self.taskID = taskID
        ## The period (in us) of the task
        self.period = period
        self.encoder = encoder
        self.encoder_share = encoder_share
        self.output_share = output_share
        self.delta_share = delta_share
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
        
        self.runs = 0
        
    # this is called from main
    def run(self):
        ''' @brief Runs one iteration of the FSM
        '''
        
        action = self.encoder_share.read()
        current_time = utime.ticks_us()
        
        if (utime.ticks_diff(current_time, self.next_time) >= 0):
            if self.state == S0_init:
                
                # zero encoder A
                if (action == 1):
                    self.transition_to(S1_zeroEncoder)
                    if (self.encoder.get_encoder_ID() == "ENCODER A"):
                        self.encoder.zero()
                        print("{0} position zeroed".format(self.encoder.get_encoder_ID()))
                        
                        # clearing the encoder_share
                        self.encoder_share.write(None)
                        print()
                        
                # zero encoder B
                elif (action == 6):
                    self.transition_to(S1_zeroEncoder)
                    if (self.encoder.get_encoder_ID() == "ENCODER B"):
                        self.encoder.zero()
                        print("{0} position zeroed".format(self.encoder.get_encoder_ID()))
                        self.encoder_share.write(None)
                        print()
                        
                # get position encoder A        
                elif (action == 2):
                    self.transition_to(S2_displayEncoderPosition)
                    if (self.encoder.get_encoder_ID() == "ENCODER A"):
                        self.encoder.get_position()
                        print("{0} position: {1}".format(self.encoder.get_encoder_ID(), self.encoder.get_position()))
                        self.encoder_share.write(None)
                        print()
                        
                # get position encoder B        
                elif (action == 7):
                    self.transition_to(S2_displayEncoderPosition)
                    if (self.encoder.get_encoder_ID() == "ENCODER B"):
                        self.ticksToRadians(self.encoder.get_position())
                        print("{0} position: {1}".format(self.encoder.get_encoder_ID(), self.encoder.get_position()))
                        self.encoder_share.write(None)
                        print()
                
                #get delta encoder A
                elif (action == 3):
                    self.transition_to(S3_displayEncoderDelta)
                    if (self.encoder.get_encoder_ID() == "ENCODER A"):
                        self.encoder.get_delta()
                        print("{0} (delta) speed: {1}".format(self.encoder.get_encoder_ID(), self.encoder.get_delta()))
                        self.encoder_share.write(None)
                        print()
                
                # get delta encoder B
                elif (action == 8):
                    self.transition_to(S3_displayEncoderDelta)
                    if (self.encoder.get_encoder_ID() == "ENCODER B"):
                        self.encoder.get_delta()
                        print("{0} (delta) speed: {1}".format(self.encoder.get_encoder_ID(), self.encoder.get_delta()))
                        self.encoder_share.write(None)
                        print()
                
                # collect data encoder A
                elif (action == 4):
                    if (self.encoder.get_encoder_ID() == "ENCODER A"):
                        self.output_share.write(self.encoder.get_position())
                        self.delta_share.write(self.encoder.get_delta())
                        self.encoder_share.write('k')
                # collect data encoder B  
                elif (action == 12):
                    if (self.encoder.get_encoder_ID() == "ENCODER B"):
                        self.output_share.write(self.encoder.get_position())
                        self.delta_share.write(self.encoder.get_delta())
                        self.encoder_share.write('j')
                    
                elif (action == 's'):
                    self.encoder_share.write('s')
                    
            else:
                self.transition_to(S0_init)
            self.next_time = utime.ticks_add(self.next_time, self.period)
            self.runs += 1
   
    def ticksToRadians(self, ticks):
       radians = float(ticks) * (2*math.pi / 4000)
       return float(radians)
   
    def radiansPerSecond(self, dTicks):
       dRadians = self.ticksToRadians(dTicks) * (1/self.period)
       return float(dRadians)
    
    def transition_to(self, new_state):
        ''' @brief      Transitions the FSM to a new state
            @details    Optionally a debugging message can be printed
                        if the dbg flag is set when the task object is created.
            @param      new_state The state to transition to.
        '''
        if (self.dbg):
            print('{:}: S{:}->S{:}'.format(self.taskID ,self.state,new_state))
        self.state = new_state