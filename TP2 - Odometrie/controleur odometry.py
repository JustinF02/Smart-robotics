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
delta_t = timestep / 1000.0
keyboard = robot.getKeyboard()
keyboard.enable(timestep)
robot_speed = 0
rotation_speed = 1

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

#state variables for odometry
x, y, theta = 0.0, 0.0, 0.0
e = 5.4
r = 2.1

print("Sampling period : ",timestep,"ms")

def wait_ms(duration_ms):
    elapsed = 0
    while elapsed < duration_ms:
        robot.step(timestep)
        elapsed += timestep
       
    
while (robot.step(timestep) != -1):
  
  #Set motors speed :
  left_speed = robot_speed
  right_speed = robot_speed
  motor_left.setVelocity(left_speed)
  motor_right.setVelocity(right_speed)
  
  
  #IR Sensors
  #prox_values = [ s.getValue() for s in prox_sensors ]
  #print("Proximité :", prox_values)

  command = keyboard.getKey()
  
  #odometry computation
  v_l = motor_left.getVelocity() 
  v_r = motor_right.getVelocity()
  
  delta_l = v_l * r * delta_t
  delta_r = v_r * r * delta_t
  
  delta_s = (delta_r + delta_l) / 2.0
  delta_theta = (delta_l - delta_r) / (2.0 * e)

  x = x + delta_s * math.cos(theta + delta_theta / 2.0)
  y = y + delta_s * math.sin(theta + delta_theta / 2.0)
  theta = theta + delta_theta

  #print results
  print(chr(27) + "[2J")
  print(f"x : {x}cm / y: {y}cm")
  print(f"left motor speed :{v_l}")
  print(f"right motor speed :{v_r}")
  #print(command)
  print(f"forward command speed: {robot_speed}")

  if command == keyboard.UP:
    robot_speed += 0.2
  if robot_speed > 6: robot_speed = 6
  elif command == keyboard.DOWN:
    robot_speed -= 0.2
    if robot_speed < -6: robot_speed = -6
  elif command == keyboard.LEFT:
    left_speed = -rotation_speed
    right_speed = rotation_speed
  elif command == keyboard.RIGHT:
    left_speed = rotation_speed
    right_speed = -rotation_speed
  elif command == 83: #S
    robot_speed = 0
    left_speed = 0
    right_speed = 0
    
    
  motor_left.setVelocity(left_speed)
  motor_right.setVelocity(right_speed)
