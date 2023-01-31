''' @file                       main.py
    @brief                      Main file to run the encoder and motor hardware.
    @details                    The main file instantiates necessary pins, encoder, and motor objects to interact with the hardware.
    @author                     Jason Davis
    @author                     Conor Fraser
    @author                     Adam Westfall

    @date                       January 24, 2023
'''
import motor_driver, encoder, pyb, time

def main():
        
    enable1 = pyb.Pin(pyb.Pin.cpu.A10, pyb.Pin.OUT_PP)
    enable2 = pyb.Pin(pyb.Pin.cpu.C1, pyb.Pin.OUT_PP)

    #defining motor inputs
    # refactored for ME 405 hardware
    input1 = pyb.Pin.cpu.B4
    input2 = pyb.Pin.cpu.B5
    input3 = pyb.Pin.cpu.A0
    input4 = pyb.Pin.cpu.A1

    timer1 = pyb.Timer(3, freq = 20000)
    # timer2 = pyb.Timer(5, freq = 20000)

    #creating motor driver / motor objects
    # enable pin, input1, input2, timer
    m1_driver = motor_driver.MotorDriver(enable1, input1, input2, timer1)
    m1 = m1_driver.motor(input1, input2, 1, 2, "MOTOR A")
    # m2_driver = motor_driver.MotorDriver(enable2, input3, input4, timer2)
    # m2 = m2_driver.motor(input3, input4, 1, 2, "MOTOR B")

    print("Initiating encoder hardware...")
    encoder_A = encoder.Encoder(pyb.Pin.cpu.B6, pyb.Pin.cpu.B7, 4, ID="ENCODER A")
    # encoder_B = encoder.Encoder(pyb.Pin.cpu.C6, pyb.Pin.cpu.C7, 3, ID="ENCODER B")
    print("done")

    print("Intializing motors...")
    # turning on the motor
    m1_driver.enable()
    print("done")

    print("3...")
    time.sleep(1)
    print("2...")
    time.sleep(1)
    print("1...")
    time.sleep(1)
    # setting motor
    m1.set_duty(75)

    # zero encoder
    encoder_A.zero()

    # reading encoder
    
    try:
        while True:
            encoder_A.update()
            print(encoder_A.read())
            time.sleep(.1)  # sleep for 0.1 seconds
    except KeyboardInterrupt:
            print('exiting...')
            m1.set_duty(0)

    
    '''
    encoder_A.update()
    print("Encoder position: " + str(encoder_A.read()))
    m1.set_duty(25)
    time.sleep(1)

    encoder_A.update()
    print("Encoder position: " + str(encoder_A.read()))
    time.sleep(1)
    m1.set_duty(50)
    time.sleep(1)
    encoder_A.update()
    print("Encoder position: " + str(encoder_A.read()))
    time.sleep(1)
    m1.set_duty(75)
    time.sleep(1)
    encoder_A.update()
    print("Encoder position: " + str(encoder_A.read()))
    time.sleep(1)
    m1.set_duty(100)
    time.sleep(1)
    encoder_A.update()
    print("Encoder position: " + str(encoder_A.read()))
    time.sleep(1)
    m1.set_duty(75)
    time.sleep(1)
    encoder_A.update()
    print("Encoder position: " + str(encoder_A.read()))
    time.sleep(1)
    m1.set_duty(50)
    time.sleep(1)
    encoder_A.update()
    print("Encoder position: " + str(encoder_A.read()))
    time.sleep(1)
    m1.set_duty(25)
    time.sleep(1)
    encoder_A.update()
    print("Encoder position: " + str(encoder_A.read()))
    time.sleep(1)
    m1.set_duty(0)
    time.sleep(1)
    encoder_A.update()
    print("Encoder position: " + str(encoder_A.read()))
    time.sleep(1)
    m1.set_duty(-25)
    time.sleep(1)
    encoder_A.update()
    print("Encoder position: " + str(encoder_A.read()))
    time.sleep(1)
    m1.set_duty(-50)
    time.sleep(1)
    encoder_A.update()
    print("Encoder position: " + str(encoder_A.read()))
    time.sleep(1)
    m1.set_duty(-75)
    time.sleep(1)
    encoder_A.update()
    print("Encoder position: " + str(encoder_A.read()))
    time.sleep(1)
    m1.set_duty(-100)
    time.sleep(1)
    encoder_A.update()
    print("Encoder position: " + str(encoder_A.read()))
    time.sleep(1)
    m1.set_duty(-75)
    time.sleep(1)
    encoder_A.update()
    print("Encoder position: " + str(encoder_A.read()))
    time.sleep(1)
    m1.set_duty(-50)
    time.sleep(1)
    encoder_A.update()
    print("Encoder position: " + str(encoder_A.read()))
    time.sleep(1)
    m1.set_duty(-25)
    time.sleep(1)
    encoder_A.update()
    print("Encoder position: " + str(encoder_A.read()))
    time.sleep(1)
    m1.set_duty(0)
    time.sleep(1)
    encoder_A.update()
    print("Encoder position: " + str(encoder_A.read()))
    time.sleep(1)
    '''

    # print("Motors and encoders are ready for commands")
if __name__ == '__main__':
    main()