# coding=utf-8
import time
import RPi.GPIO as GPIO

stepPin = 8
dir1Pin = 10
dir2Pin = 12
motoPin = 40
sleepTime = 0.00015
motoSleepTime = 0.1
motoUpDegree = 360

# 横向最大步进数
maxPos = 5000
# 横向最大映像范围
maxX = 1000
# 纵向最大步进数
maxDepth = 7000
# 纵向最大映像范围
maxY = 1000
# 落笔
motoDown = 0
# 抬笔
motoUp = 180


class DeviceController:
    def __init__(self):
        # 左右位置，面朝机器左为0
        self._nowPos = 0
        # 前后位置，机械臂收到最远为0
        self._nowDepth = 0
        self._nowMoto = motoUp
        self.motoPwm = None
        self._init()
        self._moto_move_to(motoUp)

    def up(self):
        self._moto_move_to(motoUp)

    def down(self):
        self._moto_move_to(motoDown)

    def _moto_move_to(self, degree):
        step = 10
        if abs(degree - self._nowMoto) < step:
            self._set_moto_degree(self._nowMoto)
        if degree - self._nowMoto < 0:
            step = -step
        for i in range(self._nowMoto, degree, step):
            self._set_moto_degree(i)
            time.sleep(motoSleepTime)
        self._nowMoto = degree

    def _set_moto_degree(self, degree):
        self.motoPwm.ChangeDutyCycle(12.5 - 20 * degree / 360)

    def go_to(self, x, y):
        pos = round(x / maxX * maxPos)
        dep = round(y / maxY * maxDepth)
        self._go_to(pos, dep)

    def _go_to(self, pos, depth):
        def need_step(delta, now, total):
            """返回是否需要步进，detla为总改变量，now为当前步数（从1开始到total），total为总步数"""
            if delta == 0:
                return False
            delta = total / delta
            return (now // delta) != ((now - 1) // delta)

        delta_pos = pos - self._nowPos
        delta_depth = depth - self._nowDepth
        steps = max(abs(delta_pos), abs(delta_depth))
        count = 0
        while count < steps:
            count += 1
            if need_step(delta_pos, count, steps):
                dir = 1 if delta_pos >= 0 else -1
                self._move_pos(dir)
            if need_step(delta_depth, count, steps):
                dir = 1 if delta_depth >= 0 else -1
                self._move_depth(dir)
        self._nowPos = pos
        self._nowDepth = depth

    def _init(self):

        GPIO.setwarnings(False)

        GPIO.setmode(GPIO.BOARD)

        GPIO.setup(stepPin, GPIO.OUT)
        GPIO.setup(dir1Pin, GPIO.OUT)
        GPIO.setup(dir2Pin, GPIO.OUT)

        GPIO.setup(motoPin, GPIO.OUT)
        self.motoPwm = GPIO.PWM(motoPin, 50)
        self.motoPwm.start(0)

        GPIO.output(dir1Pin, False)
        GPIO.output(dir2Pin, False)

    @staticmethod
    def _set_direction(pin, val):
        GPIO.output(pin, val)

    @staticmethod
    def _move_pulse(pin, times=1):
        if times < 0:
            times = -times
        while times > 0:
            GPIO.output(pin, True)
            time.sleep(sleepTime)
            GPIO.output(pin, False)
            time.sleep(sleepTime)
            times -= 1

    def _move_pos(self, times):
        # 正方向
        positive_dir = False
        if times >= 0:
            # 向右移动
            self._set_direction(dir1Pin, positive_dir)
            self._set_direction(dir2Pin, positive_dir)
        else:
            # 向左移动
            self._set_direction(dir1Pin, not positive_dir)
            self._set_direction(dir2Pin, not positive_dir)
        self._move_pulse(stepPin, times)

    def _move_depth(self, times):
        # 正方向
        positive_dir = False
        if times >= 0:
            # 向 深/面向用户 方向移动
            self._set_direction(dir1Pin, not positive_dir)
            self._set_direction(dir2Pin, positive_dir)
        else:
            # 向 浅/远离用户 方向移动
            self._set_direction(dir1Pin, positive_dir)
            self._set_direction(dir2Pin, not positive_dir)
        self._move_pulse(stepPin, times)


if __name__ == '__main__':
    dc = DeviceController()
    # dc._move_pulse(stepPin, 100)
    # dc._move_pos(100)
    # dc._move_pos(-100)
    # dc._move_depth(100)
    # dc._move_depth(-100)

    # dc.up()
    # dc.go_to(50, 100)
    # dc.down()
    # dc.go_to(100, 25)
    # dc.go_to(10, 100)
    # dc.go_to(0, 0)
    # dc.up()
    # time.sleep(2)
    # dc.down()

    # count = 0
    # while True:
    #    step = 100
    #    #dc._move_pos(step)
    #    dc._move_depth(step)
    #    count += step
    #    print(count)

    dc.down()
    dc.go_to(1000, 1000)
    dc.up()
    dc.go_to(1000, 0)
    dc.down()
    dc.go_to(0, 0)
    dc.up()

# GPIO.setup(dir1Pin, True)
# GPIO.setup(dir2Pin, True)
#
# count = 0
#
# while True:
#     GPIO.output(stepPin, True)
#     time.sleep(sleepTime)
#     GPIO.output(stepPin, False)
#     time.sleep(sleepTime)
#     count += 1
#     if count % 100 is 0:
#         print(count)
#
# GPIO.clearnup()
