# -*- coding: utf-8 -*-
"""
Created on Fri Nov  5 21:46:00 2021

@author: jason
"""

import utime, pyb
from micropython import const

S0_init = const(0)
S1_modifyMotorOperation = const(1)
S2_clearFaultCondition = const(2)

class Task_motorDriver():
    
    def __init__(self, taskID, motorDriver, listOfMotors, motor_share, period, dbg):
        self.taskID = taskID
        self.motorDriver = motorDriver
        self.listOfMotors = listOfMotors
        
        self.motor_share = motor_share
        self.period = period
        self.dbg = dbg
        
        self.ser = pyb.USB_VCP()
        
        self.state = S0_init
        
        self.next_time = utime.ticks_add(utime.ticks_us(), self.period)
        
    def run(self):
        
        action = self.motor_share.read()
        current_time = utime.ticks_us()
        
        if (utime.ticks_diff(current_time, self.next_time) >= 0):
            if (self.state == S0_init):
                
                #clearing the fault condition
                if (action == 0):
                    faultDetected = self.motorDriver.clearFaultCondition()
                    if (faultDetected):
                        print('        *** FAULT CONDITION CLEARED, RESUME NORMAL OPERATION ***')
                    else:
                        print('                  *** NO FAULT CONDITION DETECTED ***')
                    print()
                    
                    self.motorDriver.enable()
                    self.motor_share.write(None)
                    self.transition_to(S0_init)                
                
                elif (action == 11):
                    self.transition_to(S1_modifyMotorOperation)
                    for index in range(len(self.listOfMotors)):
                        m = self.listOfMotors[index]
                        m.toggleRunState()
                        runState = m.getRunState()
                        
                        #enable motors
                        if (runState == True):
                            print('{0} is enabled'.format(self.listOfMotors[index].getMotorID()))
                            self.motorDriver.enable()
                            if (index == len(self.listOfMotors) - 1):
                                print()
                                self.motor_share.write(None)
                                self.transition_to(S0_init)
                        
                        #disable motors
                        else:
                            print('{0} is disabled'.format(self.listOfMotors[index].getMotorID()))
                            self.motorDriver.disable()
                            if (index == len(self.listOfMotors) - 1):
                                print()
                                self.motor_share.write(None)
                                self.transition_to(S0_init)
                                
        else:
            self.transition_to(S0_init)
            self.next_time = utime.ticks_add(self.next_time, self.period)
            # print('time modified')
        
    def transition_to(self, new_state):
        ''' @brief      Transitions the FSM to a new state
            @details    Optionally a debugging message can be printed
                        if the dbg flag is set when the task object is created.
            @param      new_state The state to transition to.
        '''
        if (self.dbg):
            print('{:}: S{:}->S{:}'.format(self.taskID ,self.state,new_state))
        self.state = new_state   