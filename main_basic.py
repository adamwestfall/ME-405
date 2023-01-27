import motor_driver, pyb

#This is the way to set the condition of the enable pin. Since it is an input, we do not change its value in code.
# Instead, we check its value and write code to have the hardware either enable or disable based off of the input 
# pin condition.  We need to refactor the existing code to make this possible and delete methods which attempt to
# the value of the input.  Lastly, we need to connect an external power supply to the shield and apply ~ 10 volts
# to spin the motor.
enable1 = pyb.Pin(pyb.Pin.cpu.A10, pyb.Pin.IN,pull=pyb.Pin.PULL_UP)
enable2 = pyb.Pin(pyb.Pin.cpu.C1,pyb.Pin.IN,pull=pyb.Pin.PULL_UP)

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
#m1_driver.enable()
m1.set_duty(75)
print("motor driver enable state is: " + str(m1_driver.getEnableState()))
while True:
    pass