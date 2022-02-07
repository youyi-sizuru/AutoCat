import difflib
import os
import random
import re
import time
from pathlib import Path

import lxml.etree as ET
from airtest.core.api import connect_device, auto_setup, touch, Template, snapshot
from airtest.core.error import DeviceConnectionError, AdbError
from paddleocr import PaddleOCR


class AdbShell:
    def __init__(self, device_name: str):
        auto_setup(__file__)
        self.device_name = device_name
        self.android = connect_device("android:///%s" % device_name)
        self.ocr = PaddleOCR(use_angle_cls=False, lang="ch")

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
        work_dir = Path(__file__).resolve().parent
        dump_file_name = "temp_ui_dump_%d.xml" % int(round(time.time() * 1000))
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
            except:
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
        return self.android.adb.cmd(full_command, device=False, timeout=20)

    def touch_image(self, image_file):
        touch(Template(image_file, threshold=0.8))
        time.sleep(4)
        print("完成点击")

    def get_current_app_package_name(self) -> str:
        stdout = self.run_adb_command("shell dumpsys window")
        current_focus = next(line for line in stdout.split("\n") if "mCurrentFocus" in line)
        try:
            start = current_focus.index("{")
            end = current_focus.index("}")
            result = current_focus[start + 1:end]
            splits = result.split(" ")
            end_split = splits[len(splits) - 1]
            center = end_split.index("/")
            current_package_name = end_split[:center]
            print("当前应用包名: %s" % current_package_name)
            return current_package_name
        except ValueError:
            print("找不到当前包名")
            return ""

    def start_app(self, package_name: str) -> bool:
        print("准备启动app, 包名: %s" % package_name)
        self.run_adb_command("shell monkey -p %s 1" % package_name)
        time.sleep(4)
        return self.get_current_app_package_name() == package_name

    def restart_app(self, package_name: str) -> bool:
        print("准备关闭app, 包名: %s" % package_name)
        self.run_adb_command("shell am force-stop %s" % package_name)
        time.sleep(4)
        return self.start_app(package_name)

    def find_text(self, text: str):
        """ 查找某个字符串中心点在屏幕的位置，如果存在多个，则返回相似度最高的
        :param text: 要查找的字符串
        :return: 该字符串中心在屏幕的点（x,y）, 找不到返回None
        """
        snapshot_dir = Path(__file__).parent.joinpath("temp")
        if not os.path.exists(snapshot_dir):
            os.makedirs(snapshot_dir)
        snapshot_file = snapshot_dir.joinpath("snapshot.jpg")
        snapshot(filename=snapshot_file, quality=30)
        if not os.path.exists(snapshot_file):
            return None
        result = self.ocr.ocr(str(snapshot_file), cls=False)
        if result is None or len(result) == 0:
            return None
        max_similar_point = 0.7
        max_similar_line = None
        for line in result:
            if line[1][1] < 0.7:
                continue
            similar_point = difflib.SequenceMatcher(None, text, line[1][0]).ratio() * line[1][1]
            if similar_point > max_similar_point:
                max_similar_point = similar_point
                max_similar_line = line
        if max_similar_line is not None:
            center_x = (max_similar_line[0][0][0] + max_similar_line[0][1][0]) / 2
            center_y = (max_similar_line[0][0][1] + max_similar_line[0][3][1]) / 2
            print("找到了一个相似的字符串: %s, 相似度为: %s, 中心点为: (%s, %s)" % (
                str(max_similar_line[1][0]), str(max_similar_point), str(center_x), str(center_y)))
            return center_x, center_y
        return None

    def touch_point(self, point: tuple):
        touch(point)
