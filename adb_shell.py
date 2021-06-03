import os
import random
import re
import subprocess
import time

import lxml.etree as ET


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
        print("start swipe node")
        self.run_adb_command("shell input swipe %d %d %d %d" % (point_start_x, point_start_y, point_end_x, point_end_y))
        print("end swipe node")

    def dump_and_parse(self) -> ET.Element:
        work_dir = os.getcwd()
        dump_file_name = "baotao_ui_dump_%d.xml" % int(round(time.time() * 1000))
        android_path = "/sdcard/%s" % dump_file_name
        for i in range(0, 2):
            if self.device_name is not None:
                command_list = ['adb', '-s', self.device_name, 'shell', 'uiautomator', "dump", android_path]
            else:
                command_list = ['adb', 'shell', 'uiautomator', "dump", android_path]
            out = subprocess.Popen(command_list,
                                   stdout=subprocess.PIPE,
                                   stderr=subprocess.STDOUT)
            print("start dump ui")
            stdout, error = out.communicate()
            print("end dump ui, output:" + str(stdout))
            if error is not None or "error" in str(stdout).lower():
                print("dump error")
                continue
            print("start pull dump file to local")
            self.run_adb_command("pull %s %s" % (android_path, work_dir))
            print("end pull dump file to local")
            xml_file_path = os.path.join(work_dir, dump_file_name)
            if not os.path.exists(xml_file_path):
                print("dump file pull failed")
                continue
            et = ET.parse(xml_file_path).getroot()
            print("start remove local and remote dump file")
            self.run_adb_command("shell rm %s" % android_path)
            os.remove(xml_file_path)
            print("end remove local and remote dump file")
            return et
        print("the page ui animation too busy, uiautomator can't dump")
        return None

    def back(self):
        print("start click back")
        self.run_adb_command("shell input keyevent 4")
        time.sleep(3)
        print("end click back")

    def wake(self):
        print("start wake phone")
        self.run_adb_command("shell input keyevent 224")
        print("end wake phone")

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
        print("start click node")
        self.run_adb_command("shell input tap %d %d" % (pointx, pointy))
        time.sleep(4)
        print("end click node")

    def run_adb_command(self, command):
        if self.device_name is not None:
            full_command = "adb -s %s %s" % (self.device_name, command)
        else:
            full_command = "adb %s" % command
        print("start run adb command: %s" % full_command)
        os.system(full_command)
        print("end run adb command")
