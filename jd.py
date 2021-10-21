import logging
import time

import click
from airtest.core.android.android import Android
from airtest.core.api import auto_setup, connect_device, find_all, Template, touch, keyevent

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
    top_point = None
    mission_name = None
    # 找到最上面那个去完成
    for point in find_target():
        if top_point is None or top_point[1] > point[1]:
            top_point = point
    if top_point is None:
        return False
    touch(top_point)
    wait_and_back()
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


def find_target() -> [tuple]:
    template = Template("jd/go_complete.png", threshold=0.9)
    targets = find_all(template)
    if targets is None or len(targets) == 0:
        return []
    else:
        return map(lambda target: target['result'], targets)


if __name__ == '__main__':
    start()
