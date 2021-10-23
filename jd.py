import logging
import os
import random
import time

import click
import yaml
from airtest.core.android.android import Android
from airtest.core.api import auto_setup, connect_device, find_all, Template, touch, keyevent, exists, swipe

logger = logging.getLogger("airtest")
logger.setLevel(logging.ERROR)
screen_width = 1080
screen_height = 1920
config = {}


@click.command()
@click.option('--device', '-d', required=False)
def start(device):
    os.chdir(os.path.dirname(__file__))
    auto_setup(__file__)
    android = Android()
    if device is None:
        device = android.get_default_device()
    if device is None:
        print("找不到设备，请用数据线连接你的手机")
    connect_device("Android:///%s" % device)
    display_info = android.display_info
    global screen_width
    global screen_height
    screen_width = display_info['width']
    screen_height = display_info['height']
    global config
    with open("jd/config.yaml", mode='rb') as config_file:
        config = yaml.safe_load(config_file)
    not_find = 0
    find = 0
    while True:
        if start_mission():
            find += 1
            not_find = 0
        else:
            not_find += 1
            # 有些任务会进入到奇怪的页面，所以启动京东，然后一直点返回
            if not_find == 2:
                print("找不到任务了，尝试启动京东看看")
                android.adb.cmd("-s %s shell monkey -p com.jingdong.app.mall 1" % device)
            else:
                print("找不到任务了，尝试点击返回看看")
                keyevent("BACK")
            time.sleep(3)
        # 死循环 150次限制
        if find >= 150:
            break
        # 超过3次找不到就离开
        if not_find > 4:
            break
    print("找不到了，请确认是否符合自己的预期")


def start_mission() -> bool:
    result = find_target()
    if result is None:
        return False
    target = result[0]
    point = result[1]
    print("找到了 %s 对应的按钮" % target['desc'])
    go_y = point[1]
    if point[0] > screen_width / 2:
        go_x = point[0]
    else:
        go_x = (screen_width - point[0]) - random.randint(10, 50)
    touch((go_x, go_y))
    time.sleep(3)
    need_wait = target.get('needWait')
    if target.get('checkCar'):
        if check_car():
            need_wait = False
    if target.get('join'):
        if join():
            need_wait = False
    if target.get('visit'):
        visit()
    wait_and_back(need_wait)
    return True


def find_target():
    for target in config['targets']:
        point = find_point(target['image'])
        if point is not None:
            return target, point
    return None


def wait_and_back(need_wait):
    if need_wait:
        for i in range(0, 10):
            print("\r等待浏览完成%s" % ("." * i), end="")
            time.sleep(1)
    print("金币GET")
    print("返回上一个页面")
    keyevent("BACK")
    # 该死的动画，等长一点
    time.sleep(4)


def check_car() -> bool:
    if not exists(Template("jd/shop.png", threshold=0.9)):
        return False
    print("准备加入该死的购物车")
    car_count = 0
    swipe_x = random.randint(int(screen_width / 4), int(screen_width / 4 * 3))
    swipe_start_y = screen_height / 5 * 4 - random.randint(1, 10)
    swipe_end_y = screen_height / 5 * 1 + random.randint(1, 10)
    not_find_times = 0
    while True:
        cars = find_all(Template("jd/car.png", threshold=0.9))
        if cars is not None and len(cars) > 0:
            not_find_times = 0
            for car in cars:
                car_count += 1
                print("%d个加入购物车" % car_count)
                touch(car["result"])
                time.sleep(3)
                print("返回页面")
                while not exists(Template("jd/shop.png", threshold=0.9)):
                    keyevent("BACK")
                    time.sleep(2)
                if car_count > 5:
                    print("完成啦，结束后记得清空购物车，东哥不会心疼你的")
                    return True
            print("滑动到下一页")
            swipe((swipe_x, swipe_start_y), (swipe_x, swipe_end_y), duration=random.random() + 1, steps=1)
        else:
            not_find_times += 1
        if not_find_times > 30:
            print("根本找不到加入购物车啊，只能说你运气太差了")
            break
    return False


def find_point(filename):
    template = Template(filename, threshold=0.9)
    targets = find_all(template)
    if targets is None or len(targets) == 0:
        return None
    else:
        top_point = None
        points = map(lambda target: target['result'], targets)
        for point in points:
            if top_point is None or top_point[1] > point[1]:
                top_point = point
        return top_point


def join():
    join_template = Template("jd/join.png", threshold=0.9)
    if not exists(join_template):
        return False
    touch(join_template)
    touch(Template("jd/accept.png"))
    return True


def visit():
    print("准备逛该死的店铺")
    visit_count = 0
    while True:
        point = find_point("jd/visit.png")
        if point is not None:
            visit_count += 1
            print("%d个去逛逛" % visit_count)
            touch(point)
            time.sleep(3)
            print("返回页面")
            keyevent("BACK")
            time.sleep(2)
            if visit_count > 5:
                print("逛完了，去死吧，东哥")
                return True
        else:
            break
    return False


if __name__ == '__main__':
    start()
