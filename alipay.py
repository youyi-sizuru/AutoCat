# -*- coding: UTF-8 -*-
import time

import click
import lxml.etree as ET

from adb_shell import AdbShell


class Alipay:
    def __init__(self, adb: AdbShell):
        self.adb = adb

    def check_node(self) -> bool:
        et = self.adb.dump_and_parse()
        if et is None:
            return False
        node = self.find_node(et)
        # 找不到满足条件的节点
        if node is None:
            print("can't find any node that can jump to wait gold")
            return False
        self.adb.click_node(node)
        # 唤醒一下屏幕
        self.adb.wake()
        # 页面跳转
        self.start_wait_for_gold()
        et = self.adb.dump_and_parse()
        nodes = et.xpath(".//node[@text='开心收下']")
        if len(nodes) == 0:
            print("can't find any node that can close she dialog")
            return False
        self.adb.click_node(nodes[0])
        return True

    def find_node(self, et: ET.Element):
        # 按钮满足条件，可以点击跳转
        nodes = et.xpath(".//node[@text='逛一逛']")
        if len(nodes) != 0:
            return nodes[0]
        return None

    def start_wait_for_gold(self):
        print("start wait for gold")
        time.sleep(12)
        print("end wait for gold")
        self.adb.back()


@click.command()
@click.option('--device', '-d', required=False)
def start(device):
    alipay = Alipay(AdbShell(device))
    while alipay.check_node():
        continue


# 条件:
# 下载adb 并加入环境变量，
# 开启Android调试模式，并允许模拟点击
# 打开支付宝活动首页
# 然后运行脚本
if __name__ == '__main__':
    start()
