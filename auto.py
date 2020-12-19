import RPi.GPIO as GPIO
import wiringpi as w
import time

# init
GPIO.setmode(GPIO.BCM)
w.wiringPiSetup()

iwamoto_1 = 2
iwamoto_2 = 3
iwamoto_3 = 4

iwamoto_east = 9
iwamoto_west = 17

motoyahata_1 = 11
motoyahata_2 = 10

kudanshita_1 = 27
kudanshita_2 = 22

sasazuka_1 = 5

is_iwamoto2_direction_east = True

gp_outs = [iwamoto_1,iwamoto_2,iwamoto_3,iwamoto_east,iwamoto_west,motoyahata_1,motoyahata_2,kudanshita_1,kudanshita_2,sasazuka_1]

areas = [0,1,2,3,4,5,6]
area_is_rapid = {}
stops = [iwamoto_1,iwamoto_2,iwamoto_3,motoyahata_1,motoyahata_2,kudanshita_1,kudanshita_2]
area = {}
area_time = {
  0:50,
  1:20,
  2:30,
  3:30,
  4:55,
  5:50,
  6:100
}
stop_time = {}
stop_time_local = {
  kudanshita_1:100,
  iwamoto_3:80,
  motoyahata_1:80,
  motoyahata_2:80,
  iwamoto_1:80,
  iwamoto_2:150,
  kudanshita_2:100
}
stop_time_rapid = {
  kudanshita_1:5,
  iwamoto_3:5,
  motoyahata_1:80,
  motoyahata_2:100,
  iwamoto_1:5,
  kudanshita_2:5
}

servos = {}
for i in gp_outs:
  GPIO.setup(i, GPIO.OUT)
  servos[i] = GPIO.PWM(i, 50)

for i in gp_outs:
  print(i)
  servos[i].start(0)
  servos[i].ChangeDutyCycle(2.5)
  time.sleep(0.5)
  servos[i].ChangeDutyCycle(7.25)
  time.sleep(0.5)

for i in areas:
  area[i] = 0
  area_is_rapid[i] = -1

for i in stops:
  stop_time[i] = -1

def up(j):
  servos[j].start(0)
  servos[j].ChangeDutyCycle(7.25)
  time.sleep(0.5)

def down(j):
  servos[j].start(0)
  servos[j].ChangeDutyCycle(2.5)
  time.sleep(0.5)

is_now_newtrain=0
is_first=0
c=0
while True:
  time.sleep(0.1)
  c=c+1
  for i in areas:
    area[i] = area[i]-1
  for i in stops:
    stop_time[i] = stop_time[i]-1
  
  is_now_newtrain = is_now_newtrain -1

  # Load New Train
  if is_now_newtrain < 0:
    if(w.digitalRead(29)==0):
      print("new train")
      up(sasazuka_1)
      is_now_newtrain = 80
  elif is_now_newtrain == 0:
    if(w.digitalRead(29)==0):
      print("rapid")

      if area[1] < 0 and stop_time[kudanshita_1] < 0:
        area[1] = area_time[1]
        down(sasazuka_1)
        up(kudanshita_1)
        stop_time[kudanshita_1] = stop_time_rapid[kudanshita_1]
        area_is_rapid[1] = 1
      else:
        is_now_newtrain = 1
    else:
      print("local")
      if area[1] < 0 and stop_time[kudanshita_1] < 0:
        area[1] = area_time[1]
        area_is_rapid[1] = 0
        down(sasazuka_1)
        up(kudanshita_1)
        stop_time[kudanshita_1] = stop_time_local[kudanshita_1]
      else:
        is_now_newtrain = 1
  # kudanshita 1
  if stop_time[kudanshita_1] == 0:
    if area_is_rapid[1] == 1:
      # rapid
      if area[2] < 0 and stop_time[iwamoto_3] < 0:
        print("kudanshita_1 rapid")
        down(kudanshita_1)
        up(iwamoto_3)
        down(iwamoto_west)
        stop_time[iwamoto_3] = stop_time_rapid[iwamoto_3]
        area[2] = area_time[2]
        area_is_rapid[2] = 1
      else:
        area[1] = area[1]+1
        stop_time[kudanshita_1]=1
    else:
      # local
      if area[2] < 0 and stop_time[iwamoto_3] < 0:
        if is_now_newtrain > 0 and w.digitalRead(29)==0:
          # wait rapid
          if area[2] < 0 and area[0] < 0 and stop_time[iwamoto_2] < 0:
            print("kudanshita_1 local")
            print("east wait rapid")
            down(kudanshita_1)
            up(iwamoto_west)
            up(iwamoto_2)
            area_is_rapid[0] = area_is_rapid[2] = 0
            stop_time[iwamoto_2] = stop_time_local[iwamoto_3]
            is_iwamoto2_direction_east = True
            area[2] = area_time[2]
            area[0] = area_time[0]
          else:
            area[1] = area[1] + 1
            stop_time[kudanshita_1] = 1
        else:
          if area[2] < 0 and stop_time[iwamoto_3] < 0:
            print("kudanshita_1 local")
            print("east not wait rapid")
            down(kudanshita_1)
            up(iwamoto_3)
            down(iwamoto_west)
            area_is_rapid[2] = 0
            stop_time[iwamoto_3] = stop_time_local[iwamoto_3]
          else:
            area[1] = area[1] + 1
            stop_time[kudanshita_1] = 1
  
  # iwamoto_3
  if stop_time[iwamoto_3]==0:
    if area_is_rapid[2]==1:
      # rapid
      if area[3] < 0 and stop_time[motoyahata_2] < 0:
        print("start iwamoto_3 rapid")
        area_is_rapid[3] = 1
        down(iwamoto_3)
        up(motoyahata_2)
        stop_time[motoyahata_2] = stop_time_rapid[motoyahata_2]
        area[3] = area_time[3]
      else:
        stop_time[iwamoto_3] = 1
        area[2] = area[2]+1
    else:
      # local
      if area[3] < 0 and stop_time[motoyahata_2]<0:
        print("start iwamoto_3 local")
        area_is_rapid[3] = 0
        down(iwamoto_3)
        up(motoyahata_2)
        stop_time[motoyahata_2] = stop_time_local[motoyahata_2]
        area[3] = area_time[3]
      else:
        stop_time[iwamoto_3] = 1
        area[2] = area[2]+1

  # iwamoto_2
  if stop_time[iwamoto_2]==0:
    if is_iwamoto2_direction_east:
      # to east
      if area[3] < 0 and stop_time[motoyahata_2] < 0:
        area_is_rapid[3] = 0
        down(iwamoto_2)
        up(motoyahata_2)
        stop_time[motoyahata_2] = stop_time_local[motoyahata_2]
        area[3] = area_time[3]
      else:
        stop_time[iwamoto_2] = 1
        area[0] = area[0]+1
    else:
      # to west
      if area[6] < 0 and stop_time[kudanshita_2] < 0 and area[5] < 0 and stop_time[iwamoto_1] < 0:
        area_is_rapid[6] = 0
        down(iwamoto_2)
        up(kudanshita_2)
        stop_time[kudanshita_2] = stop_time_local[kudanshita_2]
        area[6] = area_time[6]

      else:
        stop_time[iwamoto_2] = 1
        area[0] = area[0]+1

  # motoyahata_2
  if stop_time[motoyahata_2]==0:
    if area[4] < 0 and stop_time[motoyahata_1] < 0:
      area_is_rapid[4] = area_is_rapid[3]
      down(motoyahata_2)
      up(motoyahata_1)
      stop_time[motoyahata_1] = stop_time_local[motoyahata_1]
      area[4] = area_time[4]
    else:
      stop_time[motoyahata_2] = 1
      area[3] = area[3]+1

  # motoyahata_1
  if stop_time[motoyahata_1]==0:
    if area_is_rapid[4]==1:
      # rapid
      if area[5] < 0 and stop_time[iwamoto_1] < 0:
        area[5] = area_time[5]
        down(motoyahata_1)
        down(iwamoto_east)
        up(iwamoto_1)
        stop_time[iwamoto_1] = stop_time_rapid[iwamoto_1]
        area_is_rapid[5] = 1
      else:
        area[4] = area[4]+1
        stop_time[motoyahata_1] = stop_time_rapid[motoyahata_1]
    else:
      # local
      if area_is_rapid[3]==1 and stop_time[iwamoto_2] < 0 and area[0] < 0:
        # wait for rapid
        print("wait for rapid east")
        if area[5] < 0 and area[0] < 0 and stop_time[iwamoto_2] < 0:
          area[0] = area_time[0]
          area[5] = area_time[5]
          down(motoyahata_1)
          up(iwamoto_east)
          up(iwamoto_2)
          area_is_rapid[5] = area_is_rapid[0] = 0
          stop_time[iwamoto_2] = stop_time_local[iwamoto_2]
          is_iwamoto2_direction_east=False
        else:
          area[4] = area[4]+1
          stop_time[motoyahata_1] = stop_time_local[motoyahata_1]
      else:
        # not wait for rapid
        if area[5] < 0 and stop_time[iwamoto_1] < 0:
          print("not wait for rapid west")
          area[5] = area_time[5]
          down(motoyahata_1)
          down(iwamoto_east)
          up(iwamoto_1)
          area_is_rapid[5] = 0
          stop_time[iwamoto_1] = stop_time_local[iwamoto_1]
        else:
          area[4] = area[4]+1
          stop_time[motoyahata_1] = stop_time_local[motoyahata_1]

  # iwamoto_1
  if stop_time[iwamoto_1]==0:
    if area[6] < 0 and stop_time[kudanshita_2] < 0:
      area_is_rapid[6] = area_is_rapid[5]
      down(iwamoto_1)
      up(kudanshita_2)
      if area_is_rapid[5]==1:
        stop_time[kudanshita_2] = stop_time_rapid[kudanshita_2]
        if is_iwamoto2_direction_east==False and stop_time[iwamoto_2] >= 0:
          stop_time[iwamoto_2] = stop_time[iwamoto_2]
      else:
        stop_time[kudanshita_2] = stop_time_local[kudanshita_2]
      area[6] = area_time[6]
    else:
      stop_time[iwamoto_1] = 1
      area[5] = area[5]+1

  # kudanshita_2
  if stop_time[kudanshita_2]==0:
    down(kudanshita_2)
