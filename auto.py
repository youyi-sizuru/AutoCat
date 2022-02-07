# -*- coding: UTF-8 -*-
import logging
import sys
import time
from abc import abstractmethod

import click
from airtest.core.android.android import Android

from adb_shell import AdbShell
from const import jd_package_name, taobao_package_name, alipay_package_name, jdjr_package_name


class App:
    def __init__(self, adb: AdbShell, app_name: str, package_name: str):
        self.adb = adb
        self.package_name = package_name
        self.app_name = app_name

    def check_node(self) -> bool:
        self.adb.wake()
        if self.package_name != self.adb.get_current_app_package_name() and not self.adb.start_app(self.package_name):
            print("请先安装%s" % self.app_name)
            return False
        if not self.goto_event_page():
            return False
        self.adb.wake()
        if not self.touch_event_and_back():
            return False
        return True

    @abstractmethod
    def goto_event_page(self) -> bool:
        pass

    @abstractmethod
    def touch_event_and_back(self) -> bool:
        pass


class JD(App):
    def __init__(self, adb: AdbShell):
        super(JD, self).__init__(adb, "京东", jd_package_name)

    def goto_event_page(self) -> bool:
        point = self.adb.find_text("PLUS会员")
        if point is None:
            print("找不到活动界面，准备重启京东app")
            self.adb.restart_app(self.package_name)
        point = self.adb.find_text("PLUS会员")
        if point is None:
            print("活动已结束，请以后再来")
            return False
        self.adb.touch_point(point)
        time.sleep(10)
        return True

    def touch_event_and_back(self) -> bool:
        self.adb.back()
        return True


class TaoBao(App):
    def __init__(self, adb: AdbShell):
        super(TaoBao, self).__init__(adb, "淘宝", taobao_package_name)

    def goto_event_page(self) -> bool:
        pass

    def touch_event_and_back(self) -> bool:
        pass


class Alipay(App):
    def __init__(self, adb: AdbShell):
        super(Alipay, self).__init__(adb, "支付宝", alipay_package_name)

    def goto_event_page(self) -> bool:
        pass

    def touch_event_and_back(self) -> bool:
        pass


class JDJR(App):
    def __init__(self, adb: AdbShell):
        super(JDJR, self).__init__(adb, "京东金融", jdjr_package_name)

    def goto_event_page(self) -> bool:
        pass

    def touch_event_and_back(self) -> bool:
        pass


@click.command()
@click.option('--device', '-d', required=False)
def start(device):
    logger = logging.getLogger("airtest")
    is_debug = True if sys.gettrace() else False
    if is_debug:
        logger.setLevel(logging.INFO)
    else:
        logger.setLevel(logging.ERROR)
    if device is None:
        device = Android().get_default_device()
    if device is None:
        print("找不到设备，请用数据线连接你的手机")
        return
    adb = AdbShell(device)
    package_name = adb.get_current_app_package_name()
    app_list = []
    if package_name == jd_package_name:
        app_list.append(JD(adb))
    elif package_name == taobao_package_name:
        app_list.append(TaoBao(adb))
    elif package_name == jdjr_package_name:
        app_list.append(JDJR(adb))
    elif package_name == alipay_package_name:
        app_list.append(Alipay(adb))
    else:
        app_list.append(TaoBao(adb))
        app_list.append(Alipay(adb))
        app_list.append(JD(adb))
        app_list.append(JDJR(adb))
    for app in app_list:
        while app.check_node():
            continue


# 条件:
# 下载adb 并加入环境变量，
# 开启Android调试模式，并允许模拟点击
# 然后运行脚本
if __name__ == '__main__':
    start()
