import motor_driver, encoder, pyb, time

enable1 = pyb.Pin(pyb.Pin.cpu.A10, pyb.Pin.OUT_PP)
enable2 = pyb.Pin(pyb.Pin.cpu.C1, pyb.Pin.OUT_PP)

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
m1 = m1_driver.motor(input1, input2, 1, 2, "MOTOR A")
m2_driver = motor_driver.MotorDriver(enable2, input3, input4, timer2)
m2 = m2_driver.motor(input3, input4, 1, 2, "MOTOR B")

# turning on the motor
m1_driver.enable()

m1.set_duty(25)
time.sleep(1)
m1.set_duty(50)
time.sleep(1)
m1.set_duty(75)
time.sleep(1)
m1.set_duty(100)
time.sleep(1)
m1.set_duty(75)
time.sleep(1)
m1.set_duty(50)
time.sleep(1)
m1.set_duty(25)
time.sleep(1)
m1.set_duty(0)
time.sleep(1)
m1.set_duty(-25)
time.sleep(1)
m1.set_duty(-50)
time.sleep(1)
m1.set_duty(-75)
time.sleep(1)
m1.set_duty(-100)
time.sleep(1)
m1.set_duty(-75)
time.sleep(1)
m1.set_duty(-50)
time.sleep(1)
m1.set_duty(-25)
time.sleep(1)
m1.set_duty(0)
time.sleep(1)

print("Motors and encoders are ready for commands")