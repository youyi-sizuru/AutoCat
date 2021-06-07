import os
import random
import re
import time

import lxml.etree as ET
from airtest.core.api import connect_device, auto_setup
from airtest.core.error import DeviceConnectionError, AdbError


class AdbShell:
    def __init__(self, device_name: str):
        auto_setup(__file__)
        self.device_name = device_name
        self.android = connect_device("android:///%s" % device_name)

    def swipe_node(self, node):
        bounds = str(node.get("bounds"))
        pattern = '^\\[([0-9]+),([0-9]+)\\]\\[([0-9]+),([0-9]+)\\]$'
        match_result = re.match(pattern, bounds, re.M)
        left = int(match_result.group(1))
        right = int(match_result.group(3))
        top = int(match_result.group(2))
        bottom = int(match_result.group(4))
        point_start_x = random.randint(left + 100, right - 100)
        point_start_y = random.randint(0, 100) + top + (bottom - top) * 3 / 5
        point_end_x = point_start_x
        point_end_y = random.randint(0, 100) + top + (bottom - top) / 5
        print("开始滑动页面去触发倒计时")
        self.run_adb_command("shell input swipe %d %d %d %d" % (point_start_x, point_start_y, point_end_x, point_end_y))

    def dump_and_parse(self) -> ET.Element:
        work_dir = os.getcwd()
        dump_file_name = "baotao_ui_dump_%d.xml" % int(round(time.time() * 1000))
        android_path = "/sdcard/%s" % dump_file_name
        for i in range(0, 3):
            print("开始获取页面信息并保存")
            try:
                stdout = self.run_adb_command("shell uiautomator dump %s" % android_path)
                if "error" in stdout.lower():
                    print(stdout)
                    print("获取失败,正在重试")
                else:
                    print("正在将手机端页面信息拉取到本地")
                    self.run_adb_command("pull %s %s" % (android_path, work_dir))
                    xml_file_path = os.path.join(work_dir, dump_file_name)
                    if not os.path.exists(xml_file_path):
                        print("页面信息拉取失败，信息文件根本不存在")
                        continue
                    print("成功拉取到本地")
                    et = ET.parse(xml_file_path).getroot()
                    print("解析成功，开始移除本地和手机端多余的信息文件")
                    self.run_adb_command("shell rm %s" % android_path)
                    os.remove(xml_file_path)
                    print("完成移除")
                    return et
            except DeviceConnectionError:
                print("获取页面信息超时,正在重试")
            except AdbError as e:
                print(e.stderr)
                print("运行出错，正在重试")
            time.sleep(2 * (i + 1))
        print("有问题导致无法抓取信息:(")
        return None

    def back(self):
        print("返回上一个页面")
        self.run_adb_command("shell input keyevent 4")
        time.sleep(3)
        print("完成返回")

    def wake(self):
        print("唤醒手机屏幕防止息屏")
        self.run_adb_command("shell input keyevent 224")
        print("完成唤醒")

    def click_node(self, node):
        bounds = str(node.get("bounds"))
        pattern = '^\\[([0-9]+),([0-9]+)\\]\\[([0-9]+),([0-9]+)\\]$'
        match_result = re.match(pattern, bounds, re.M)
        left = int(match_result.group(1))
        right = int(match_result.group(3))
        top = int(match_result.group(2))
        bottom = int(match_result.group(4))
        pointx = random.randint(left + 1, right - 1)
        pointy = random.randint(top + 1, bottom - 1)
        print("开始点击对应的按钮")
        self.run_adb_command("shell input tap %d %d" % (pointx, pointy))
        time.sleep(4)
        print("完成点击")

    def run_adb_command(self, command):
        full_command = "-s %s %s" % (self.device_name, command)
        print("运行相关命令: %s" % full_command)
        return self.android.adb.cmd(full_command, timeout=10)
