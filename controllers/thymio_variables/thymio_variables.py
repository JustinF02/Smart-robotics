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

# odométrie
ps_left = robot.getDevice("motor.left.sensor")
ps_right = robot.getDevice("motor.right.sensor")
ps_left.enable(timestep)
ps_right.enable(timestep)


print("Sampling period : ",timestep,"ms")

motor_left.setVelocity(robot_speed)
motor_right.setVelocity(robot_speed)

def wait_ms(duration_ms):
    """Remplace time.sleep par une vraie attente Webots."""
    elapsed = 0
    while elapsed < duration_ms:
        robot.step(timestep)
        elapsed += timestep
        
def turn(angle_deg, speed=1.0):
    print("turning")
    target_rad = math.radians(angle_deg)

    # Lire position initiale
    left0 = ps_left.getValue()
    right0 = ps_right.getValue()

    # Déterminer sens de rotation
    if target_rad > 0:     # tourner à droite
        motor_left.setVelocity(speed)
        motor_right.setVelocity(-speed)
    else:                  # tourner à gauche
        motor_left.setVelocity(-speed)
        motor_right.setVelocity(speed)

    # Boucle jusqu'à atteindre l’angle voulu
    while robot.step(timestep) != -1:
        left = ps_left.getValue()
        right = ps_right.getValue()

        dL = (left - left0) * wheel_radius
        dR = (right - right0) * wheel_radius

        theta = (dR - dL) / track_width   # orientation estimée

        if abs(theta) >= abs(target_rad):
            break

    # Stop
    motor_left.setVelocity(0)
    motor_right.setVelocity(0)
    
while (robot.step(timestep) != -1):
  
  #Set motors speed :
  motor_left.setVelocity(1)
  motor_right.setVelocity(1)
  wait_ms(1000)
    
  # Tourner de 90°
  turn(90, speed=1)
    
  # Tourner de -45°
  turn(-45, speed=1)
  # Process sensor data here

  # Enter here functions to send actuator commands, like:
  #command = keyboard.getKey()
  
  #print(command)

  #if command==keyboard.LEFT:
    #print('Left')
    #motor_left.setVelocity(0.0) #-robot_speed
    #motor_right.setVelocity(robot_speed)
  #elif command==keyboard.RIGHT:
    #print('right')
    #motor_left.setVelocity(robot_speed)
    #motor_right.setVelocity(0.0) #-robot_speed
  #elif command==keyboard.UP:
    #print('up')
    #if robot_speed<2:
      #robot_speed+=0.2
  #elif command==keyboard.DOWN:
    #print('down')
    #if robot_speed>-2:
      #robot_speed-=0.2
  #elif command==83: # capture S key
    #print('stop')
    #robot_speed = 0

# Enter here exit cleanup code
