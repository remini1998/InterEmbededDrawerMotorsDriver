# coding=utf-8
import time
import RPi.GPIO as GPIO

stepPin = 8
dir1Pin = 10
dir2Pin = 12
sensorPin = 38
motoPin = 40
pauseBtnPin = 36

sleepTime = 0.00015
motoSleepTime = 0.02
btnCheckTime = 0.2
resetTime = 5

# 横向最大步进数
maxPos = 5000
# 横向最大映像范围
maxX = 1000
# 纵向最大步进数
maxDepth = 7000
# 纵向最大映像范围
maxY = 1000
# 落笔
motoDown = 90
# 抬笔
motoUp = 180

btnPressedValue = 1

# 设置检测到人进入后是否暂停
needPause = True

# 设置检测到人进入后是否中断（优先）
needStop = False

usePauseBtn = True

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
        return self._go_to(pos, dep)

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
                self._nowPos += dir
                if not self._move_pos(dir):
                    return False
            if need_step(delta_depth, count, steps):
                dir = 1 if delta_depth >= 0 else -1
                self._nowDepth += dir
                if not self._move_depth(dir):
                    return False
        self._nowPos = pos
        self._nowDepth = depth
        return True

    def _init(self):

        GPIO.setwarnings(False)

        GPIO.setmode(GPIO.BOARD)

        GPIO.setup(sensorPin, GPIO.IN)
        GPIO.setup(pauseBtnPin, GPIO.IN)

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

    def _move_pulse(self, pin, times=1):
        if times < 0:
            times = -times
        while times > 0:
            if usePauseBtn and GPIO.input(pauseBtnPin) == btnPressedValue:
                while GPIO.input(pauseBtnPin) == btnPressedValue:
                    print("waiting for btn up")
                    time.sleep(btnCheckTime)
                while GPIO.input(pauseBtnPin) != btnPressedValue:
                    print("waiting for restart")
                    time.sleep(btnCheckTime)
                # 判断是否是长按复位
                total_time = 0
                while GPIO.input(pauseBtnPin) == btnPressedValue:
                    total_time += btnCheckTime
                    if total_time > resetTime:
                        print("start reset")
                        self.up()
                        time.sleep(btnCheckTime * 25)
                        self.go_to(0, 0)
                        time.sleep(btnCheckTime * 10)
                        return False
                    time.sleep(btnCheckTime)
                time.sleep(btnCheckTime * 10)

            if GPIO.input(sensorPin) == 1:
                print("detected people and stop")
                if needStop:
                    print("system stopped")
                    return False
                if needPause:
                    while GPIO.input(sensorPin) == 1:
                        pass
                print("continue")
            GPIO.output(pin, True)
            time.sleep(sleepTime)
            GPIO.output(pin, False)
            time.sleep(sleepTime)
            times -= 1
        return True

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
        return self._move_pulse(stepPin, times)

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
        return self._move_pulse(stepPin, times)
    
    def test_pos_length(self):
        count = 0
        step = 1000
        while True:
            count += 1
            self._move_pos(1)
            
            if count % step == 0:
                print("-----------------------------------------")
                print("  now count:" + count)
                print("  now step:" + step)
                print("    input 's' to stop,")
                print("    input '+/-' to scale step 10 times")
                print("    others to continue")
                i = input("Your choice: ")
                if i == "s":
                    return
                if i == "+":
                    step *= 10
                if i == "-":
                    step /= 10
    
    
    def test_dep_length(self):
        count = 0
        while True:
            count += 1
            self._move_depth(1)
            if count % step == 0:
                print("-----------------------------------------")
                print("  now count:" + count)
                print("  now step:" + step)
                print("    input 's' to stop,")
                print("    input '+/-' to scale step 10 times")
                print("    others to continue")
                i = input("Your choice: ")
                if i == "s":
                    return
                if i == "+":
                    step *= 10
                if i == "-":
                    step /= 10


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
    dc.up()
    
    print("move straight")
    print("1")
    dc.go_to(200, 0)
    print("2")
    dc.go_to(0, 0)
    print("3")
    dc.go_to(0, 200)
    print("4")
    dc.go_to(0, 0)

    print("test-all")
    dc.down()
    print("1")
    dc.go_to(1000, 1000)
    print("2")
    dc.up()
    dc.go_to(1000, 0)
    print("3")
    dc.down()
    dc.go_to(0, 0)
    print("4")
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
