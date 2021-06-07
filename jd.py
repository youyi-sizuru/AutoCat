import logging
import random
import time

import click
from airtest.core.android.android import Android
from airtest.core.api import auto_setup, connect_device, find_all, Template, touch, keyevent, exists, swipe

logger = logging.getLogger("airtest")
logger.setLevel(logging.ERROR)


@click.command()
@click.option('--device', '-d', required=False)
def start(device):
    auto_setup(__file__)
    if device is None:
        device = Android().get_default_device()
    if device is None:
        print("找不到设备，请用数据线连接你的手机")
    connect_device("Android:///%s" % device)
    not_find = 0
    while True:
        if start_mission():
            not_find = 0
        else:
            not_find += 1
            # 有些任务会进入到奇怪的页面，所以需要一直点返回
            print("找不到任务了，尝试点击返回看看")
            keyevent("BACK")
            time.sleep(3)
        if not_find > 3:
            break
    print("找不到了，请确认是否符合自己的预期")


def start_mission() -> bool:
    if go_with_target("jd/watch.png", "浏览任务"):
        wait_and_back()
    elif go_with_target("jd/shop.png", "浏览商店"):
        wait_and_back()
    elif go_with_target("jd/shop_gold.png", "浏览金色商店"):
        wait_and_back()
    elif go_with_target("jd/game.png", "浏览活动页"):
        wait_and_back()
    elif go_with_target("jd/pack.png", "浏览大牌"):
        # 大牌页面加载比较慢
        time.sleep(3)
        wait_and_back()
    elif go_with_target("jd/gold.png", "浏览好物"):
        time.sleep(3)
        if check_car():
            keyevent("BACK")
        else:
            wait_and_back()
    else:
        return False
    return True


def wait_and_back():
    for i in range(0, 12):
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
    display_info = Android().get_display_info()
    width = display_info['width']
    height = display_info['height']

    swipe_x = random.randint(width / 4, width / 4 * 3)
    swipe_start_y = height / 5 * 4 - random.randint(1, 10)
    swipe_end_y = height / 5 * 1 + random.randint(1, 10)
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
                print("我看都不看就返回页面，打我呀")
                keyevent("BACK")
                time.sleep(2)

                if car_count > 5:
                    print("完成啦，结束后记得清空购物车，东哥不会心疼你的")
                    return True
            print("战术滑动到下一页，不要怕，技术性调整")
            swipe((swipe_x, swipe_start_y), (swipe_x, swipe_end_y), duration=random.random() + 1, steps=1)
        else:
            not_find_times += 1
        if not_find_times > 30:
            print("根本找不到加入购物车啊，只能说你运气太差了")
            break
    return False


def go_with_target(filename, button_name) -> bool:
    if "浏览金色商店" == button_name:
        goes = find_all(Template("jd/go_gold.png", threshold=0.9))
    else:
        goes = find_all(Template("jd/go.png", threshold=0.9))
    if goes is None:
        print("找不到去完成按钮")
        return False
    targets = find_all(Template(filename, threshold=0.9))
    if targets is None:
        return False
    for target in targets:
        target_y = target["result"][1]
        for go in goes:
            go_y = go["result"][1]
            if abs(go_y - target_y) < 50:
                print("找到了 %s 对应的去完成按钮" % button_name)
                touch(go["result"])
                return True
    return False


if __name__ == '__main__':
    start()
