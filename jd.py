import logging
import random
import time

import click
from airtest.core.android.android import Android
from airtest.core.api import auto_setup, connect_device, find_all, Template, touch, keyevent, exists, swipe

logger = logging.getLogger("airtest")
logger.setLevel(logging.ERROR)
screen_width = 1080
screen_height = 1920


@click.command()
@click.option('--device', '-d', required=False)
def start(device):
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
    not_find = 0
    find = 0
    while True:
        if start_mission():
            find += 1
            not_find = 0
        else:
            not_find += 1
            # 有些任务会进入到奇怪的页面，所以启动京东，然后一直点返回
            if not_find == 1:
                print("找不到任务了，尝试启动京东看看")
                android.adb.cmd("-s %s shell monkey -p com.jingdong.app.mall 1" % device)
            else:
                print("找不到任务了，尝试点击返回看看")
                keyevent("BACK")
            time.sleep(3)
        # 死循环 200次限制
        if find >= 200:
            break
        # 超过3次找不到就离开
        if not_find > 3:
            break
    print("找不到了，请确认是否符合自己的预期")


def start_mission() -> bool:
    top_point = None
    mission_name = None
    # 找到最上面那个任务
    for target in [("jd/watch.png", "浏览任务"), ("jd/shop.png", "浏览商店"), ("jd/shop_gold.png", "浏览金色商店"),
                   ("jd/game.png", "浏览活动页"), ("jd/gold.png", "浏览好物"), ("jd/pack.png", "浏览大牌")]:
        for point in find_target(target[0]):
            if top_point is None or top_point[1] > point[1]:
                top_point = point
                mission_name = target[1]
    if top_point is None:
        return False
    print("找到了 %s 对应的按钮" % mission_name)
    # 可以利用相对位置来确定去完成按钮的位置，避免不同机型去完成按钮不一致的问题
    go_y = top_point[1]
    go_x = (screen_width - top_point[0]) - random.randint(10, 50)
    touch((go_x, go_y))
    if mission_name == "浏览大牌":
        # 浏览大牌页面加载比较慢
        time.sleep(3)
        wait_and_back()
    elif mission_name == "浏览好物":
        time.sleep(3)
        if check_car():
            keyevent("BACK")
        else:
            wait_and_back()
    else:
        wait_and_back()
    return True


def wait_and_back():
    for i in range(0, 10):
        print("\r等待浏览完成%s" % ("." * i), end="")
        time.sleep(1)
    print()
    print("金币GET")
    print("返回上一个页面")
    keyevent("BACK")
    # 该死的动画，等长一点
    time.sleep(4)


def check_car() -> bool:
    if not exists(Template("jd/gold_big.png", threshold=0.9)):
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


def find_target(filename) -> [tuple]:
    template = Template(filename, threshold=0.9)
    targets = find_all(template)
    if targets is None or len(targets) == 0:
        return []
    else:
        return map(lambda target: target['result'], targets)


if __name__ == '__main__':
    start()
