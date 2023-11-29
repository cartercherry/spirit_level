#####################################################################################
# spirit_level.py     Lesson 45      11/28/23                                       #
# Pitch, Roll from MPU6050 accel vectors displayed on ssd1306 as a bubble           #
# Bubble located at center of display when level                                    #
# Bubble constrained to display; pitch, roll degrees displayed as  text             #
#####################################################################################


from machine import Pin, I2C
from ssd1306 import SSD1306_I2C
from imu import MPU6050
from math import atan2, pi
import time

pitch_error = -.2  #calibrated pitch with spirit level
roll_error = -3.2  #calibrated roll with spirit level
display_cols=128   #oled ssd1306 128x64 pixels
display_rows=64
bubble_radius =5    # size of bubble on display
min_x = bubble_radius  #bubble col min value
max_x =display_cols-1-bubble_radius  #bubble col max value
min_y = bubble_radius  #bubble row min value
max_y = display_rows-1-bubble_radius  #bubble row max value
max_tilt = 20  # display bubble up to  +/- max_tilt degrees (pitch and roll)

i2c=I2C(0, scl=Pin(1), sda=Pin(0))
mpu=MPU6050(i2c)

def draw_bubble(x: int, y: int, xr: int=5, yr:int=5, color: int=1) -> None:
    '''spirit bubble size on display centered at (x,y)'''
    oled.ellipse(x,y,xr,yr,color)
   

def draw_rect(x: int=56, y: int=25, width: int=16, height: int=16, color: int=1) ->None:
    '''rect at center of display to help locate level'''
    oled.rect(x,y,width,height,color) # (x,y) left upper corner of rect

    
def draw_display(x: int, y: int) ->None:
    '''update the display with bubble center at (x,y) and check for level condition'''
    oled.fill(0)
    if is_level:
        oled.text("Level!",int(display_cols/2-15),0,1)  # level now
    draw_bubble(x,y) # bubble center at (x,y) on display
    draw_rect()  # level locating rectangle
    display_tilt_text(pitch,roll)  # update pitch and roll text on display
    oled.show()


def get_vectors():
    '''return the acceleration vectors from MPU6050'''
    return(mpu.accel.xyz)


def calculate_tilt(ax: float, ay:float, az:float) -> Tuple[float]:
    '''pitch, roll from latest accel vectors'''
    pitch=atan2(ay, az)* 180/pi # radians->degrees
    roll = atan2(ax,az)* 180/pi
    pitch +=pitch_error  # calibration, spirit level
    roll +=roll_error  #calibration, spirit level
    return (pitch,roll)


def pitch_to_display_col_coord(pitch: float, max_pitch_allowed: int) -> int:
    '''convert pitch to display col coord.   screen  resolution is +/- max_pitch_allowed'''
    if pitch > max_pitch_allowed: pitch=max_pitch_allowed
    if pitch< -max_pitch_allowed: pitch = - max_pitch_allowed
    m= (max_x - min_x)/(max_pitch_allowed*2) #slope
    pitch_display_coord = m*(pitch+max_pitch_allowed) + min_x
    return int(pitch_display_coord)


def roll_to_display_row_coord(roll: float, max_roll_allowed: int) -> int:
    '''convert roll to display row coord.   screen resolution is +/- max_roll_allowed'''
    if roll > max_roll_allowed: roll=max_roll_allowed
    if roll< -max_roll_allowed: roll = - max_roll_allowed
    m= (max_y - min_y)/(max_roll_allowed*2)  # slope 
    roll_display_coord = m*(roll+max_roll_allowed) + min_y
    return int(roll_display_coord)


def check_if_level(x: int, y: int) ->bool:
    '''is pitch and roll bubble center (x,y) nominally zero?'''
    if x in range(int(display_cols/2 - 2), int(display_cols/2+3)) and \
    y in range(int(display_rows/2 - 2), int(display_rows/2 +3)):
        return True
    else:
        return False


def display_tilt_text(pitch: float, roll: float) ->None:
    '''pitch, roll in degrees shown on display'''
    data = f'P: {pitch:<4.1f} R: {+roll:<4.1f}'
    oled.text(data, 0,54,1)


while True:
    ax,ay,az=get_vectors()
    pitch, roll = calculate_tilt(ax, ay, az)
    # print(f'{pitch=:.1f}, {roll=:.1f}')  # DEBUG
    x=pitch_to_display_col_coord(pitch, max_tilt)
    y=roll_to_display_row_coord(roll, max_tilt)
    is_level = check_if_level(x,y)
    draw_display(x, y)  # bubble centered at (x,y) on display
    time.sleep(.1)
