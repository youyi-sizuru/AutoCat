# -*- coding: UTF-8 -*-
import time

import click
import lxml.etree as ET

from adb_shell import AdbShell, get_first_device


class Alipay:
    def __init__(self, adb: AdbShell):
        self.adb = adb
        self.last_happy_node = None

    def check_node(self) -> bool:
        et = self.adb.dump_and_parse()
        if et is None:
            return False
        node = self.find_node(et)
        # 找不到满足条件的节点
        if node is None:
            print("根本找不到可以点击的按钮，请确认是否符合自己的预期")
            return False
        self.adb.click_node(node)
        # 唤醒一下屏幕
        self.adb.wake()
        # 页面跳转
        self.start_wait_for_gold()
        # 等一下狗屎弹窗动画
        time.sleep(4)
        if self.last_happy_node is None:
            et = self.adb.dump_and_parse()
            if et is None:
                return False
            nodes = et.xpath(".//node[@text='开心收下']")
            if len(nodes) == 0:
                print("找不到开心收下按钮，日了狗，重试吧")
                return False
            self.last_happy_node = nodes[0]
        print("点一下该死的开心收下，根本不开心")
        self.adb.click_node(self.last_happy_node)
        time.sleep(1)
        return True

    def find_node(self, et: ET.Element):
        # 按钮满足条件，可以点击跳转
        nodes = et.xpath(".//node[@text='逛一逛']")
        if len(nodes) != 0:
            return nodes[0]
        return None

    def start_wait_for_gold(self):
        for i in range(0, 12):
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
