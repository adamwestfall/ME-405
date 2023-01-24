# -*- coding: utf-8 -*-
"""
Created on Fri Oct 29 14:37:49 2021

@author: jason
"""

import pyb
import encoder, DRV8847, shares
import task_user, task_encoder, task_motor, task_motorDriver
    
# instantiating our encoders
encoder_A = encoder.Encoder(pyb.Pin.cpu.B6, pyb.Pin.cpu.B7, 4, ID="ENCODER A")
encoder_B = encoder.Encoder(pyb.Pin.cpu.C6, pyb.Pin.cpu.C7, 3, ID="ENCODER B")

# instantiating a share object for the task_encoder
encoder_share = shares.Share(0)

# a share object for the output
output_share = shares.Share(0)

delta_share = shares.Share(0)

#defining motor inputs
input1 = pyb.Pin.cpu.B4
input2 = pyb.Pin.cpu.B5
input3 = pyb.Pin.cpu.B0
input4 = pyb.Pin.cpu.B1

#creating motor driver / motor objects
motorDriver = DRV8847.DRV8847(pyb.Timer(3, freq = 20000))
motor_A = motorDriver.motor(input1, input2, encoder_A, 1, 2, "MOTOR A")
motor_B = motorDriver.motor(input3, input4, encoder_B, 3, 4, "MOTOR B")

listOfMotors = [motor_A, motor_B]

#creating a share object for the motors
motor_share = shares.Share()

# instantiating the user interface
# the ui will return a character representing the desired task and pass it to task_encoder
task_1 = task_user.Task_User('USER', 10000, encoder_share, output_share, delta_share, motor_share, dbg=False)

# instantiating a task object for each task
task_2A = task_encoder.Task_Encoder('ENC_A', 10000, encoder_A, encoder_share, output_share, delta_share)
task_2B = task_encoder.Task_Encoder('ENC_B', 10000, encoder_B, encoder_share, output_share, delta_share)

task_3 = task_motorDriver.Task_motorDriver('MOTOR DRIVER', motorDriver, listOfMotors, motor_share, 10000, False)

task_4A = task_motor.Task_Motor('MOTOR_A', 10000, motor_A, motor_share, output_share)
task_4B = task_motor.Task_Motor('MOTOR_B', 10000, motor_B, motor_share, output_share)

# create a task list
taskList = [task_1, task_2A, task_2B, task_3, task_4A, task_4B]

while (True):
    try:
        encoder_A.update()
        encoder_B.update()
        
        for task in taskList:
            task.run()
        
    except KeyboardInterrupt:
        break
print('\n*** Program ending, have a nice day! ***\n')
  