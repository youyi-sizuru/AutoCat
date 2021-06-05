import os
import random
import re
import subprocess
import time

import lxml.etree as ET


def get_first_device():
    command_list = ['adb', 'devices']
    out = subprocess.Popen(command_list,
                           stdout=subprocess.PIPE,
                           stderr=subprocess.STDOUT)
    out_str = out.communicate()[0].decode("utf-8").replace("\r", "")
    keyword = "List of devices attached"
    device_info = out_str[out_str.rindex(keyword) + len(keyword) + 1:]
    device_list = device_info.split("\n")
    if len(device_list) > 0 and len(device_list[0].split("\t")) == 2:
        return device_list[0].split("\t")[0]
    return None


class AdbShell:
    def __init__(self, device_name=None):
        self.device_name = device_name

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
        for i in range(0, 5):
            command_list = ['adb', '-s', self.device_name, 'shell', 'uiautomator', "dump", android_path]
            out = subprocess.Popen(command_list,
                                   stdout=subprocess.PIPE,
                                   stderr=subprocess.STDOUT)
            print("开始获取页面信息并保存")
            try:
                stdout, error = out.communicate(timeout=20)
            except subprocess.TimeoutExpired:
                print("获取页面信息超时,正在重试")
                time.sleep(2 * (i + 1))
                continue
            if out.returncode != 0 or error is not None or "error" in stdout.decode("utf-8").lower():
                print(stdout.decode("utf-8"))
                print("获取失败,正在重试")
                if i == 2:
                    print("尝试重新连接手机")
                    os.system("adb kill-server")
                    time.sleep(1)
                    os.system("adb start-server")
                time.sleep(2 * (i + 1))
                continue
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
        print("页面动画过于频繁导致工具无法抓取信息:(")
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
        full_command = "adb -s %s %s" % (self.device_name, command)
        print("运行相关命令: %s" % full_command)
        os.system(full_command)
