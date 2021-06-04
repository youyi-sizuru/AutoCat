import time

import click
from airtest.core.api import auto_setup, connect_device, find_all, Template, touch, keyevent


@click.command()
@click.option('--device', '-d', required=True)
def start(device):
    auto_setup(__file__)
    connect_device("Android:///%s" % device)
    while go_shop() or go_gold():
        time.sleep(11)
        keyevent("BACK")
        time.sleep(1)
        continue
    print("complete")


def go_gold() -> bool:
    goes = find_all(Template("jd/go.png", threshold=0.9))
    if goes is None:
        return False
    golds = find_all(Template("jd/gold.png", threshold=0.9))
    if golds is None:
        return False
    for gold in golds:
        gold_y = gold["result"][1]
        for go in goes:
            go_y = go["result"][1]
            if abs(go_y - gold_y) < 50:
                touch(go["result"])
                return True
    return False


def go_shop() -> bool:
    goes = find_all(Template("jd/go.png", threshold=0.9))
    if goes is None:
        return False
    shops = find_all(Template("jd/shop.png", threshold=0.9))
    if shops is None:
        return False
    for shop in shops:
        shop_y = shop["result"][1]
        for go in goes:
            go_y = go["result"][1]
            if abs(go_y - shop_y) < 50:
                touch(go["result"])
                return True
    return False


if __name__ == '__main__':
    start()
