# Copyright 1996-2019 Cyberbotics Ltd.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
This controller gives to its node the following behavior:
Listen the keyboard. According to the pressed key, send a
message through an emitter or handle the position of Robot1.
"""
## Reference
## https://www.cyberbotics.com/doc/guide/thymio2?version=develop

import math
from controller import Robot

robot = Robot()
timestep = int(robot.getBasicTimeStep())
keyboard = robot.getKeyboard()
keyboard.enable(timestep)
robot_speed = 1

print(chr(27) + "[2J") # ANSI code for clearing command line
print("Initialization of thymio_variables controller")

motor_left = robot.getDevice("motor.left");
motor_right = robot.getDevice("motor.right");
motor_left.setPosition(float('inf'))
motor_right.setPosition(float('inf'))

prox_sensors = []
for i in range(7):
    name = f"prox.horizontal.{i}"
    sensor = robot.getDevice(name)
    sensor.enable(timestep)
    prox_sensors.append(sensor)


print("Sampling period : ",timestep,"ms")

def wait_ms(duration_ms):
    elapsed = 0
    while elapsed < duration_ms:
        robot.step(timestep)
        elapsed += timestep
       
    
while (robot.step(timestep) != -1):
  
  #Set motors speed :
  motor_left.setVelocity(1)
  motor_right.setVelocity(1)

  # Process sensor data here
  prox_values = [ s.getValue() for s in prox_sensors ]

  print("Proximité :", prox_values)

  #Enter here functions to send actuator commands, like:
  command = keyboard.getKey()
  
  print(command)

  if command==keyboard.LEFT:
    print('Left')
    motor_left.setVelocity(0.0) #-robot_speed
    motor_right.setVelocity(robot_speed)
  elif command==keyboard.RIGHT:
    print('right')
    motor_left.setVelocity(robot_speed)
    motor_right.setVelocity(0.0) #-robot_speed
  elif command==keyboard.UP:
    print('up')
    if robot_speed<2:
      robot_speed+=0.2
  elif command==keyboard.DOWN:
    print('down')
    if robot_speed>-2:
      robot_speed-=0.2
  elif command==83: # capture S key
    print('stop')
    robot_speed = 0

# Enter here exit cleanup code
