# -*- coding: UTF-8 -*-
import time

import click
import lxml.etree as ET

from adb_shell import AdbShell, get_first_device


class TaoBao:
    def __init__(self, adb: AdbShell):
        self.adb = adb

    def check_node(self) -> bool:
        et = self.adb.dump_and_parse()
        if et is None:
            return False
        node = self.find_node(et)
        # 找不到满足条件的节点
        if node is None:
            print("笑死，根本找不到可以点击的按钮，请确认是否符合自己的预期")
            return False
        self.adb.click_node(node)
        # 唤醒一下屏幕
        self.adb.wake()
        if node.attrib["text"] == "去搜索":
            self.adb.swipe_node(et[0])
        # 页面跳转
        while self.check_shop():
            self.start_wait_for_gold()
        self.start_wait_for_gold()
        return True

    def find_node(self, et: ET.Element):
        # 按钮满足条件，可以点击跳转
        nodes = et.xpath(".//node[@text='去浏览']")
        if len(nodes) != 0:
            return nodes[0]
        nodes = et.xpath(".//node[@text='逛一逛']")
        if len(nodes) != 0:
            return nodes[0]
        nodes = et.xpath(".//node[contains(@text,'逛一逛')]/../..//node[@text='去完成']")
        if len(nodes) != 0:
            return nodes[0]
        nodes = et.xpath(".//node[@text='去观看']")
        if len(nodes) != 0:
            return nodes[0]
        nodes = et.xpath(".//node[@text='去搜索']")
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
            count = i % 4
            print("\r正在等待喵币%s" % "..."[0:count], end="")
            time.sleep(1)
        print("\r喵币GET")
        self.adb.back()


@click.command()
@click.option('--device', '-d', required=False)
def start(device):
    if device is None:
        device = get_first_device()
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
