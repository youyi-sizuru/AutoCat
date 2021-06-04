import logging
import time

import click
from airtest.core.android.android import Android
from airtest.core.api import auto_setup, connect_device, find_all, Template, touch, keyevent

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
    while True:
        if go_shop():
            wait_and_back()
            continue
        if go_pack():
            wait_and_back()
            continue
        if go_gold():
            wait_and_back()
            continue
        break
    print("找不到了，请确认是否符合自己的预期")


def wait_and_back():
    for i in range(0, 10):
        count = i % 4
        print("\r等待浏览完成%s" % "..."[0:count], end="")
        time.sleep(1)
    print("\r金币GET")
    print("返回上一个页面")
    keyevent("BACK")
    # 该死的动画，等长一点
    time.sleep(4)


def go_with_target(filename, button_name) -> bool:
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


def go_gold() -> bool:
    return go_with_target("jd/gold.png", "浏览好物")


def go_shop() -> bool:
    return go_with_target("jd/shop.png", "浏览商店")


def go_pack() -> bool:
    return go_with_target("jd/pack.png", "浏览大牌")


if __name__ == '__main__':
    start()
