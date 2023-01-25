# -*- coding: utf-8 -*-
"""
Created on Fri Oct 29 09:28:55 2021

@author: jason
"""

import utime, pyb
from micropython import const

## List of possible motor states
# Definitely not implemented properly
S0_init = const(0)
S1_modifyDutyCycle = const(1)

class Task_Motor:
    
    def __init__(self, taskID, period, motor, motor_share, output_share, dbg = False):
        self.taskID = taskID
        self.period = period
        self.motor = motor
        self.motor_share = motor_share
        self.output_share = output_share
        self.dbg = dbg
        
        self.ser = pyb.USB_VCP()
        self.state = S0_init
        self.next_time = utime.ticks_add(utime.ticks_us(), self.period)
        
    def run(self):

        action = self.motor_share.read()
        # debugging only
        
        current_time = utime.ticks_us()
        # self.duty = self.motor.getDuty()
        
        if (utime.ticks_diff(current_time, self.next_time) >= 0):
            if (self.state == S0_init):
                
                if (action == 9):
                    print("action == 9")
                    self.transition_to(S1_modifyDutyCycle)
                    print(self.motor.getMotorID())
                    if (self.motor.getMotorID() == "MOTOR A"):
                        duty = self.collectBufferedInput("MOTOR A")
                        self.modifyMotorOperation("MOTOR A", duty)
                
                elif (action == 10):
                    self.transition_to(S1_modifyDutyCycle)
                    if (self.motor.getMotorID() == "MOTOR B"):
                        duty = self.collectBufferedInput("MOTOR B")
                        self.modifyMotorOperation("MOTOR B", duty)
                
                # Both motors max fwd    
                elif (action == 12):
                    self.transition_to(S1_modifyDutyCycle)
                    if (self.motor.getMotorID() == "MOTOR A"):
                        self.modifyMotorOperation("MOTOR A", 100)
                        self.motor_share.write(12)
                        self.transition_to(S0_init)
                                           
                    elif (self.motor.getMotorID() == "MOTOR B"):
                        self.modifyMotorOperation("MOTOR B", 100)
                        self.motor_share.write(None)
                        self.transition_to(S0_init)
                
                # Both motors max reverse        
                elif (action == 13):
                    self.transition_to(S1_modifyDutyCycle)
                    
                    if (self.motor.getMotorID() == "MOTOR A"):
                        self.modifyMotorOperation("MOTOR A", -100)
                        self.motor_share.write(13)
                        self.transition_to(S0_init)
                        
                    elif (self.motor.getMotorID() == "MOTOR B"):
                        self.modifyMotorOperation("MOTOR B", -100)
                        self.motor_share.write(None)
                        self.transition_to(S0_init)
                        
            else:
                self.transition_to(S0_init)
            self.next_time = utime.ticks_add(self.next_time, self.period)
    
    def collectBufferedInput(self, motorID):
        print('Enter a duty cycle for {0}: '.format(motorID), end = '')
        
        userInput = str(self.ser.read(2))
        if (len(userInput) > 4):
            t = userInput[2:4]
        else:
            t = userInput[2:3]
        temp = list([])
        
        # hitting the 'enter' key sends \r character to the VCP
        while (t != '\\r'):
            
            # append the information in the VCP to "duty" only if it is a digit
            if (t.isdigit() or t == '-'):
                # print('t is a digit')
                print ('{0}'.format(t), end = '')
                temp.append(t)
            
            userInput = str(self.ser.read(2))
            if (len(userInput) > 4):
                t = userInput[2:4]
            else:
                t = userInput[2:3]
            
            # NOTE: everytime we read values from the VCP, it then EMPTIES the VCP
            # We need to store the value of the VCP in a temp variable if we wish to use it later
        duty = ''.join(map(str, temp))
        # print('duty is: |{0}|'.format(duty))
        if (duty == ''):
            duty = self.motor.getDuty() * self.motor.getDirection()
        # handling the case of duty > 100
        elif (int(duty) > 100):
            duty = 100
            
        # handling the case of duty < 0
        elif (int(duty) < -100):
            duty = -100
        return duty
    
    def modifyMotorOperation(self, motorID, duty):
        t = int(duty)
        d = abs(t)
        
        if (t == int(self.motor.getDuty()*self.motor.getDirection())):
            direction = int(self.motor.getDirection())
            if (len(str(duty)) > 0):
                print()
            print ('{0} duty cycle unchanged...'.format(motorID))
            if (direction > 0):
                print("{0} is running forwards at {1}%\n".format(motorID, self.motor.getDuty()))
            elif (direction < 0):
                print("{0} is running in reverse at {1}%\n".format(motorID, self.motor.getDuty()))
            else:
                print("{0} is stationary\n".format(motorID))
        
        else:
            self.motor.setDuty(t)
            direction = int(self.motor.getDirection())
            print ('\nSetting motor duty cycle to {0}%'.format(d))
            if (direction > 0):
                print("{0} is running forwards at {1}%\n".format(motorID, d))
            elif (direction < 0):
                print("{0} is running in reverse at {1}%\n".format(motorID, d))
            else:
                print("{0} is stationary\n".format(motorID))
        
        self.motor_share.write(None)
        self.transition_to(S0_init)
                    
    def transition_to(self, new_state):
        ''' @brief      Transitions the FSM to a new state
            @details    Optionally a debugging message can be printed
                        if the dbg flag is set when the task object is created.
            @param      new_state The state to transition to.
        '''
        if (self.dbg):
            print('{:}: S{:}->S{:}'.format(self.taskID ,self.state,new_state))
        self.state = new_state
    