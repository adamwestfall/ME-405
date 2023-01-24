'''   @file                            motor_driver.py
   @brief                              Hardware driver for the L6206 dual H-bridge chip
   @details                            Hardware driver for the L6206 dual H-bridge chip.  This driver 
                                       provides functionality to the nSleep pin to enable/disable either
                                       1 stepper motor or 2 DC motors.  Driver provides fault reset functionality
                                       and internally creates virtual motor objects based on user implementation
                                       
   @author                             Jason Davis
   @author                             Conor Fraser
   @author                             Adam Westfall
   @copyright                          Creative Commons CC BY: Please visit https://creativecommons.org/licenses/by/4.0/ to learn more
   @date                               January 24, 2023
'''


import pyb, time
import encoder

class MotorDriver:
    
    def __init__(self, en_pin, in1pin, in2pin, timer): 
        '''   @brief                              Constructor for L6206 motor driver hardware
           @details                            
           @param en_pin
           @param in1pin
           @param in2pin
           @param timer                   Defines the hardware timer used with the motorDriver
        '''
        
        # enable pin
        self.en_pin = en_pin

        #input pins
        self.in1pin = in1pin
        self.in2pin = in2pin

        # initializing timer
        self.timer = timer
        
    def enable (self):
        '''   @brief                              Allows the motors to spin
           @details                            Allows the motors to spin by writing the nSLEEP pin
                                               to logic high
        '''
        self.enable.high()
    
    def disable (self):
        '''   @brief                              Disables motor function
           @details                            Keeps the motors from spinning by writing the nSLEEP pin
                                               to logic low
        '''
        self.enable.low()
        
    ## There are several fault conditions that may damage the motor / driver
    ## This function must disable the motor when a fault condition occurs
    ## Reference the button interrupt code used in lab 1  
# =============================================================================
#     5 Fault conditions possible:
#       undervoltage
#       overcurrent
#       short-circuit
#       open-load
#       overtemperature        
# =============================================================================

    def fault_cb (self, IRQ_src):
        '''   @brief                           Detects a hardware fault condition
           @details                            Detects a hardware fault condition and interrupts harware function
                                               by disabling motor function
           @param IRQ_src                      The source of the interrupt
        '''
        print('  *** FAULT DETECTED! SUSPENDING L6206 HARDWARE OPERATION ***')
        self.disable()
    
    # def clearFaultCondition(self):
    #     '''   @brief                           Tests the value of the fault pin 
    #        @details                            
    #        @return                             Returns a boolean based on the fault pin
    #     '''
        
    #     faultCondition = self.faultCondition
    #     print('INITIAL FAULT STATUS: {0}'.format(self.nFAULT))
    #     if (not self.faultCondition):
    #           faultCondition = True
    #           print('MODIFIED FAULT STATUS: {0}'.format(self.nFAULT))
              
    #     return faultCondition
    
    ##also sets the direction
    def set_duty(self, duty):
        
        if (duty > 0):
            self.duty = duty
            self.direction = 1
            #set the "reverse" channel to zero first
            self.channel2.pulse_width_percent(0)
            self.channel1.pulse_width_percent(duty)
            
        elif (duty < 0):
            duty *= -1
            self.duty = duty
            self.direction = -1
            #set the "forward channel to zero first
            self.channel1.pulse_width_percent(0)
            self.channel2.pulse_width_percent(duty)
            
        elif (duty == 0):
            self.duty = duty
            self.direction = 0
            self.brake()
            # print("{0} is stationary\n".format(self.motorID))
                    
    def motor (self, inputA, inputB, channelA, channelB, motorID):
        '''   @brief                           Constructor for Motor class
           @details                            
           @param inputA                       Input pin 1 of 2
           @param inputB                       Input pin 2 of 2
           @param motorTimer                   Timer associated with the motor
           @param channelA                     Timer channel 1 of 2
           @param channelB                     Timer channel 2 of 2
           @param motorID                      Identifier for the motor
        '''
        return Motor(inputA, inputB, self.motorTimer, channelA, channelB, motorID)
    
class Motor:
        
    def __init__ (self, inputA, inputB, motorTimer, channelA, channelB, motorID):
        '''   @brief                           Constructor for Motor class
           @details                            
           @param inputA                       Input pin 1 of 2
           @param inputB                       Input pin 2 of 2
           @param motorTimer                   Timer associated with the motor
           @param channelA                     Timer channel 1 of 2
           @param channelB                     Timer channel 2 of 2
           @param motorID                      Identifier for the motor
        '''
        self.inputA = inputA
        self.inputB = inputB
               
        self.motorTimer = motorTimer
        # establish the motor timer channels here
        self.channel1 = self.motorTimer.channel(channelA, pyb.Timer.PWM, pin = inputA)
        self.channel2 = self.motorTimer.channel(channelB, pyb.Timer.PWM, pin = inputB)
        
        self.channelA = channelA
        self.channelB = channelB
        self.motorID = motorID
        
        # initialized to zero (off)
        self.duty = 0
        
        self.isRunning = False
        self.direction = 0
        
    def getMotorID(self):
        return self.motorID
    
    def getDuty(self):
        return self.duty

    def getDirection(self):
        return self.direction
    
    def getRunState(self):
        return self.isRunning
    
    # Why do we need this? Jason - 1/24/23
    def toggleRunState(self):
        self.isRunning = not(self.isRunning)  
        
    def coast(self):
        self.channel1.pulse_width_percent(0)
        self.channel2.pulse_width_percent(0)
    
    def brake(self):
        self.channel1.pulse_width_percent(100)
        self.channel2.pulse_width_percent(100)
        
if __name__ == '__main__' :
    
    # defining motor inputs
    input1 = pyb.Pin.cpu.B4
    input2 = pyb.Pin.cpu.B5
    input3 = pyb.Pin.cpu.PA0
    input4 = pyb.Pin.cpu.PA1
    
    # creating motor driver / motor objects
    m1_driver = motor_driver(pyb.Timer(3, freq = 20000))
    m1 = motor_driver.motor(input1, input2, 1, 2, "Motor A")
    m2_driver = motor_driver(pyb.Timer(5, freq = 20000))
    m2 = motor_driver.motor(input3, input4, 1, 2, "Motor B")
    
    # turning on the motor
    m1_driver.enable()
    m1_driver.set_duty(75)