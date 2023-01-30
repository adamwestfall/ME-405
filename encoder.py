# -*- coding: utf-8 -*-

''' @file                       encoder.py
    @brief                      A hardware driver for reading from quadrature encoders
    @details
    @author                     Jason Davis
    @author                     Conor Fraser
    @author                     Adam Westfall

    @date                       January 24, 2023
'''
import pyb
import time

class Encoder():
    ''' @brief                  Interface with quadrature encoders
        @details
    '''
    
    def __init__(self, pinA, pinB, timNum, ID = None):
        ''' @brief              Interface with quadrature encoders
            @details            Initialize the encoder hardware with two GPIO pins, a timer, and an optional ID
        '''
        self.pinA = pinA
        self.pinB = pinB
        self.timNum = timNum
        self.position = 0     
        self.delta = 0
        self.period = 65535 + 1
        
        # Optional parameter to assign an ID to the hardware
        # Useful for debugging 
        self.ID = ID if ID is not None else None
        
        # each pair of pins gets a timer
        self.encoderTimer = pyb.Timer(timNum, prescaler = 0, period = 65535)
        
        # each pin gets a channel
        self.encoderTimer.channel(1, pyb.Timer.ENC_AB, pin = pinA)
        self.encoderTimer.channel(2, pyb.Timer.ENC_AB, pin = pinB) 
        
        self.prev_count = self.encoderTimer.counter()
        
    def update(self):
        ''' @brief              Updates encoder position and angular velocity
            @details
        '''
        current_count = self.encoderTimer.counter()
        self.delta = current_count - self.prev_count
        
        # This logic handles counter overflow
        if (self.delta >= self.period/2):
            self.delta -= self.period
        if self.delta <= (-1 * self.period/2):
            self.delta += self.period
            
        self.prev_count = current_count
        self.position += self.delta
        
    def zero(self):
        ''' @brief              Resets encoder position to zero
            @details
        '''
        self.position = 0
        
    def read(self):
        ''' @brief              Returns encoder position
            @details
            @return             The position of the encoder shaft
        '''
        return self.position
    
    
    def set_position(self, position):
        ''' @brief              Updates encoder position
            @details
            @param  position    The new position of the encoder shaft 
        '''
        self.position = position
        
    def get_delta(self):
        ''' @brief              Returns encoder shaft angular velocity
            @details
            @return             The change in position of the encoder shaft
                                between the most two recent updates
        '''
        return self.delta
        
    def get_encoder_ID(self):
        ''' @brief              Returns encoder ID
            @details
            @return             An ID tag of string type
        '''
        return self.ID
        
if __name__ == '__main__':

    # instantiating our encoders
    encoderA = Encoder(pyb.Pin.cpu.B6, pyb.Pin.cpu.B7, 4, ID="ENCODER_A")
    encoderB = Encoder(pyb.Pin.cpu.C6, pyb.Pin.cpu.C7, 3, ID="ENCODER_B")

    # runs an infinite loop where the encoder position is continuously returned until a keyboard interrupt is triggered
    while (True):

        try:
            encoderA.update()
            print(encoderA.read())
            # time.sleep(0.5)
        except KeyboardInterrupt:
            print("bye bye")
            break

