# coding=utf-8
import os
from gpioMotorsController import DeviceController

class DrawerMeta(object):
    """
    绘画的核心调用类
    """
    def __init__(self, test=False):
        self.BASE_DIR = os.path.dirname(__file__) #获取当前文件夹的绝对路径
        self._test_path = os.path.join(self.BASE_DIR, "test")
        self._test_name = ""
        self.is_test = test
        self.begin_data = [] # [(x,y)...]
        self.end_data = [] # [(x,y)...]
        self.x_edge = 0 # max x
        self.y_edge = 0 # max y
        self._drawer_device = DeviceController()

        self.pen_status = 1 # down 1 up 0

    @staticmethod
    def f(item):
        try:
            return float(item)
        except:
            raise BaseException("Data transfer Error[Float]")

    def set_test_name(self, test_name):
        self._test_name = test_name
    
    def read_test_data(self):
        with open(os.path.join(self._test_path, self._test_name)) as f:
            for line in f.readlines():
                line_data = line.split(',')
                bx = self.f(line_data[0])
                by = self.f(line_data[1])
                ex = self.f(line_data[2])
                ey = self.f(line_data[3])

                temp = (bx if bx > ex else ex)
                if self.x_edge < temp:
                    self.x_edge = temp

                temp = (by if by > ey else ey)
                if self.y_edge < temp:
                    self.y_edge = temp

                self.begin_data.append([bx, by])
                self.end_data.append([ex, ey])
            f.close()

    def output_datas(self):
        # test use
        # print(self.begin_data)
        # print(self.end_data)
        print(self.x_edge, self.y_edge)

    def pen_up(self):
        if self.pen_status == 1:
            if self.is_test:
                print("pen up")
            self._drawer_device.up()
            self.pen_status = 0
        else:
            if self.is_test:
                print("[ERROR] pen already up")
            else:
                raise BaseException("[ERROR] pen already up")

    def pen_down(self):
        if self.pen_status == 0:
            if self.is_test:
                print("pen down")
            self._drawer_device.down()
            self.pen_status = 1
        else:
            if self.is_test:
                print("[ERROR] pen already down")
            else:
                raise BaseException("[ERROR] pen already down")

    def draw_data(self, begin, end):
        print("draw from ({bx}, {by}) to ({ex}, {ey})".format(
            bx=begin[0], by=begin[1], ex=end[0], ey=end[1]
        ))
        self._drawer_device.go_to(begin[0], begin[1])
   #     self.pen_down()
        self._drawer_device.go_to(end[0], end[1])
  #      self.pen_up()

    def start_draw(self):
        blen = len(self.begin_data)
        elen = len(self.end_data)
        if blen != elen:
            raise BaseException("Data Lenght Error")
        # start draw up
 #       self.pen_up()
        for i in range(blen):
            self.draw_data(self.begin_data[i], self.end_data[i])


if __name__ == "__main__":
    draw = DrawerMeta(test=True)
    draw.set_test_name("predict_strokes.txt")
    draw.read_test_data()
    draw.start_draw()
    # draw.output_datas()
