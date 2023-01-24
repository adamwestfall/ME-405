'''   @file                            DRV8847.py
   @brief                              Hardware driver for the DRV8847 dual H-bridge chip
   @details                            Hardware driver for the DRV8847 dual H-bridge chip.  This driver 
                                       provides functionality to the nSleep pin to enable/disable either
                                       1 stepper motor or 2 DC motors.  Driver provides fault reset functionality
                                       and internally creates virtual motor objects based on user implementation
                                       
   @author                             Jason Davis
   @author                             Conor Fraser
   @author                             Solie Grantham
   @author                             Zachary Stednitz
   @copyright                          Creative Commons CC BY: Please visit https://creativecommons.org/licenses/by/4.0/ to learn more
   @date                               October 28, 2021
'''


import pyb, time
import encoder

class DRV8847:
    
    def __init__(self, motorTimer): 
        '''   @brief                              Constructor for DRV8847 class
           @details                            
           @param motorTimer                   Defines the hardware timer used with the motorDriver
        '''
        
        ## Both nSleep and nFault are pulled high to enable and low to disable
        self.nSLEEP = pyb.Pin.cpu.A15
# =============================================================================
#       The fault detection is complicated!  Consult Lab3_README.txt for more
#       information on how to properly implement this
# =============================================================================
        self.nFAULT = pyb.Pin.cpu.B2 # or 6, or 8? 
        self.faultCondition = (pyb.ExtInt(self.nFAULT, mode=pyb.ExtInt.IRQ_FALLING,
                                         pull=pyb.Pin.PULL_UP, callback=self.fault_cb))
        self.motorTimer = motorTimer
        
        # forces the motor to begin in a disabled state
        self.nSLEEP.low()
        self.nFAULT.high()
        
    def enable (self):
        '''   @brief                              Allows the motors to spin
           @details                            Allows the motors to spin by writing the nSLEEP pin
                                               to logic high
        '''
        self.nSLEEP.high()
    
    def disable (self):
        '''   @brief                              Disables motor function
           @details                            Keeps the motors from spinning by writing the nSLEEP pin
                                               to logic low
        '''
        self.nSLEEP.low()
        
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
        print('  *** FAULT DETECTED! SUSPENDING DRV8847 HARDWARE OPERATION ***')
        self.disable()
    
    def clearFaultCondition(self):
        '''   @brief                           Tests the value of the fault pin 
           @details                            
           @return                             Returns a boolean based on the fault pin
        '''
        
        faultCondition = self.faultCondition
        print('INITIAL FAULT STATUS: {0}'.format(self.nFAULT))
        if (not self.faultCondition):
              faultCondition = True
              print('MODIFIED FAULT STATUS: {0}'.format(self.nFAULT))
              
        return faultCondition
        
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
        
        self.duty = 0
        
        self.isRunning = False
        self.direction = 0
        
    def getMotorID(self):
        return self.motorID
    
    ##also sets the direction
    def setDuty(self, duty):
        
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
                
    def getDuty(self):
        return self.duty

    def getDirection(self):
        return self.direction
    
    def getRunState(self):
        return self.isRunning
    
    def toggleRunState(self):
        self.isRunning = not(self.isRunning)  
        
    def coast(self):
        self.channel1.pulse_width_percent(0)
        self.channel2.pulse_width_percent(0)
    
    def brake(self):
        self.channel1.pulse_width_percent(100)
        self.channel2.pulse_width_percent(100)
        
if __name__ == '__main__' :
    
    #defining motor inputs
    input1 = pyb.Pin.cpu.B4
    input2 = pyb.Pin.cpu.B5
    input3 = pyb.Pin.cpu.B0
    input4 = pyb.Pin.cpu.B1
    
    #creating motor driver / motor objects
    motorDriver = DRV8847(pyb.Timer(3, freq = 20000))
    m1 = motorDriver.motor(input1, input2, 1, 2, "Motor A")
    m2 = motorDriver.motor(input3, input4, 3, 4, "Motor B")
    
    motorDriver.enable()
    