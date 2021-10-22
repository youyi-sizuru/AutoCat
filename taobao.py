# -*- coding: UTF-8 -*-
import logging
import time

import click
import lxml.etree as ET
from airtest.core.android.android import Android

from adb_shell import AdbShell

logger = logging.getLogger("airtest")
logger.setLevel(logging.ERROR)


class TaoBao:
    def __init__(self, adb: AdbShell):
        self.adb = adb
        self.had_check_shop = False

    def check_node(self) -> bool:
        et = self.adb.dump_and_parse()
        if et is None:
            return False
        node = self.find_node(et)
        # 找不到满足条件的节点
        if node is None:
            print("笑死，根本找不到可以点击的按钮，请确认是否符合自己的预期")
            return False
        # 页面跳转
        self.adb.click_node(node)
        # 唤醒一下屏幕
        self.adb.wake()
        if node.attrib["text"] == "去搜索":
            self.adb.swipe_node(et[0])
        # 二级页面逛店已经完成，不再进行确认了，节省一点时间
        if not self.had_check_shop and node.attrib["text"] == "去浏览":
            while self.check_shop():
                self.had_check_shop = True
                self.start_wait_for_gold()
        self.start_wait_for_gold()
        return True

    def find_node(self, et: ET.Element):
        # 按钮满足条件，可以点击跳转
        nodes = et.xpath(".//node[@text='去浏览' or @text='逛一逛' or @text='去观看' or @text='去搜索' or @text='去逛逛']")
        if len(nodes) != 0:
            return nodes[0]
        nodes = et.xpath(".//node[contains(@text,'逛')]/../..//node[@text='去完成']")
        if len(nodes) != 0:
            return nodes[0]
        nodes = et.xpath(".//node[contains(@text,'浏览')]/../..//node[@text='去完成']")
        if len(nodes) != 0:
            return nodes[0]
        return None

    def check_shop(self) -> bool:
        et = self.adb.dump_and_parse()
        if et is None:
            return False
        go_shop_nodes = et.xpath(".//node[@text='逛店最多']")
        if len(go_shop_nodes) == 0:
            return False
        self.adb.click_node(go_shop_nodes[0])
        return True

    def start_wait_for_gold(self):
        for i in range(0, 16):
            print("\r正在等待喵币%s" % ("." * i), end="")
            time.sleep(1)
        print()
        print("喵币GET")
        self.adb.back()


@click.command()
@click.option('--device', '-d', required=False)
def start(device):
    if device is None:
        device = Android().get_default_device()
    if device is None:
        print("找不到设备，请用数据线连接你的手机")
        return
    taobao = TaoBao(AdbShell(device))
    while taobao.check_node():
        continue


# 条件:
# 下载adb 并加入环境变量，
# 开启Android调试模式，并允许模拟点击
# 打开淘宝活动首页，点击领喵币，开启领喵币中心
# # 然后运行脚本
if __name__ == '__main__':
    start()
