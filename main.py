# -*- coding: utf-8 -*-
"""
Created on Fri Oct 29 14:37:49 2021

@author: jason
"""

import pyb
import encoder, motor_driver, shares
import task_user, task_encoder, task_motor, task_motorDriver
    
# instantiating our encoders
# Aligns well with ME 405 structure
encoder_A = encoder.Encoder(pyb.Pin.cpu.B6, pyb.Pin.cpu.B7, 4, ID="ENCODER A")
encoder_B = encoder.Encoder(pyb.Pin.cpu.C6, pyb.Pin.cpu.C7, 3, ID="ENCODER B")

# instantiating a share object for the task_encoder
encoder_share = shares.Share(0)

# a share object for the output
output_share = shares.Share(0)

# a share object for the angular velocity
delta_share = shares.Share(0)

# defining motor driver enable pins
enable1 = pyb.Pin.cpu.A10
enable2 = pyb.Pin.cpu.C1

#defining motor inputs
# refactored for ME 405 hardware
input1 = pyb.Pin.cpu.B4
input2 = pyb.Pin.cpu.B5
input3 = pyb.Pin.cpu.A0
input4 = pyb.Pin.cpu.A1

timer1 = pyb.Timer(3, freq = 20000)
timer2 = pyb.Timer(5, freq = 20000)

#creating motor driver / motor objects
# enable pin, input1, input2, timer
m1_driver = motor_driver.MotorDriver(enable1, input1, input2, timer1)
m1 = m1_driver.motor(input1, input2, 1, 2, "Motor A")
m2_driver = motor_driver.MotorDriver(enable2, input3, input4, timer2)
m2 = m2_driver.motor(input3, input4, 1, 2, "Motor B")

#creating a share object for the motors
motor_share = shares.Share()

# instantiating the user interface
# the ui will return a character representing the desired task and pass it to task_encoder
task_1 = task_user.Task_User('USER', 10000, encoder_share, output_share, delta_share, motor_share, dbg=False)

# instantiating a task object for each task
task_2A = task_encoder.Task_Encoder('ENC_A', 10000, encoder_A, encoder_share, output_share, delta_share)
task_2B = task_encoder.Task_Encoder('ENC_B', 10000, encoder_B, encoder_share, output_share, delta_share)

task_3A = task_motorDriver.Task_motorDriver('MOTOR_A DRIVER', m1_driver, motor_share, 10000, False)
task_3B = task_motorDriver.Task_motorDriver('MOTOR_B DRIVER', m2_driver, motor_share, 10000, False)

task_4A = task_motor.Task_Motor('MOTOR_A', 10000, m1, motor_share, output_share)
task_4B = task_motor.Task_Motor('MOTOR_B', 10000, m1, motor_share, output_share)

# create a task list
taskList = [task_1, task_2A, task_2B, task_3A, task_3B, task_4A, task_4B]

while (True):
    try:
        encoder_A.update()
        encoder_B.update()
        
        for task in taskList:
            task.run()
        
    except KeyboardInterrupt:
        break
print('\n*** Program ending, have a nice day! ***\n')
  