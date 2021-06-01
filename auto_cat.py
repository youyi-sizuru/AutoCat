import os
import random
import re
import subprocess
import sys
import time

import lxml.etree as ET

# -*- coding: UTF-8 -*-
device_name = None


def check_node() -> bool:
    et = dump_and_parse()
    if et is None:
        return False
    node = find_node(et)
    # 找不到满足条件的节点
    if node is None:
        print("can't find any node that can jump to wait gold")
        return False
    click_node(node)
    time.sleep(4)
    # 唤醒一下屏幕
    run_adb_command("shell input keyevent 224")
    # 页面跳转
    check_shop()
    return True


def find_node(et: ET.Element):
    # 按钮满足条件，可以点击跳转
    nodes = et.xpath(".//node[@text='去浏览']")
    if len(nodes) != 0:
        return nodes[0]
    nodes = et.xpath(".//node[@text='去搜索']")
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
    nodes = et.xpath(".//node[@text='去完成']")
    if len(nodes) != 0:
        return nodes[0]
    return None


def check_shop():
    has_shop = False
    while True:
        et = dump_and_parse()
        if et is None:
            print("can't check gold state, we just wait for gold")
            break
        go_shop_nodes = et.xpath(".//node[@text='逛店最多']")
        if len(go_shop_nodes) == 0:
            break
        has_shop = True
        click_node(go_shop_nodes[0])
        time.sleep(2)
        # 唤醒一下屏幕
        run_adb_command("shell input keyevent 224")
        start_wait_for_gold()
    if not has_shop:
        start_wait_for_gold()
    else:
        run_adb_command("shell input keyevent 4")
        time.sleep(2)


def start_wait_for_gold():
    max_check_time = 3
    print("wait for gold")
    time.sleep(16)
    while max_check_time > 0:
        et = dump_and_parse()
        if et is None:
            # # 节点抓不到，我们就走个流程
            # print("can't check gold state, we just wait for gold")
            # time.sleep(15)
            break
        mission_complete_nodes = et.xpath(".//node[@text='任务完成']")
        all_complete_nodes = et.xpath(".//node[@text='任务已经']")
        if len(mission_complete_nodes) != 0 or len(all_complete_nodes) != 0:
            # 找到完成的字样就结束了
            print("Congratulations! your mission is complete!!")
            break
        # count_down_nodes = et.xpath(".//node[@text='得喵币']")
        # if len(count_down_nodes) != 0:
        #     swipe_node(et[0])
        #     print("wait for gold")
        #     time.sleep(16)
        #     break
        max_check_time = max_check_time - 1
        if max_check_time == 0:
            print("oh no, the page can't start the mission")
        # else:
        #     # 尝试去滑动页面去激活倒计时，部分页面需要滑动触发
        #     print("try to swipe page")
        #     swipe_node(et[0])
    print("back to activity page")
    run_adb_command("shell input keyevent 4")
    time.sleep(2)


def dump_and_parse() -> ET.Element:
    work_dir = os.getcwd()
    dump_file_name = "baotao_ui_dump_%d.xml" % int(round(time.time() * 1000))
    android_path = "/sdcard/%s" % dump_file_name
    for i in range(0, 2):
        if device_name is not None:
            command_list = ['adb', '-s', device_name, 'shell', 'uiautomator', "dump", android_path]
        else:
            command_list = ['adb', 'shell', 'uiautomator', "dump", android_path]
        out = subprocess.Popen(command_list,
                               stdout=subprocess.PIPE,
                               stderr=subprocess.STDOUT)
        stdout, error = out.communicate()
        print("dump finish, output:" + str(stdout))
        if error is not None or "error" in str(stdout).lower():
            print("dump error")
            continue
        run_adb_command("pull %s %s" % (android_path, work_dir))
        xml_file_path = os.path.join(work_dir, dump_file_name)
        if not os.path.exists(xml_file_path):
            print("dump file pull failed")
            continue
        et = ET.parse(xml_file_path).getroot()
        run_adb_command("shell rm %s" % android_path)
        os.remove(xml_file_path)
        return et
    print("the page ui animation too busy, uiautomator can't dump")
    return None


def click_node(node):
    bounds = str(node.get("bounds"))
    pattern = '^\\[([0-9]+),([0-9]+)\\]\\[([0-9]+),([0-9]+)\\]$'
    match_result = re.match(pattern, bounds, re.M)
    left = int(match_result.group(1))
    right = int(match_result.group(3))
    top = int(match_result.group(2))
    bottom = int(match_result.group(4))
    pointx = random.randint(left + 1, right - 1)
    pointy = random.randint(top + 1, bottom - 1)
    click_command = "shell input tap %d %d" % (pointx, pointy)
    print("start click node, the commnad: %s" % click_command)
    run_adb_command(click_command)


def swipe_node(node):
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
    click_command = "shell input swipe %d %d %d %d" % (point_start_x, point_start_y, point_end_x, point_end_y)
    print("start swipe node, the commnad: %s" % click_command)
    run_adb_command(click_command)


def run_adb_command(command):
    if device_name is not None:
        os.system("adb -s %s %s" % (device_name, command))
    else:
        os.system("adb %s" % command)


# 条件:
# 下载adb 并加入环境变量，
# 开启Android调试模式，并允许模拟点击
# 打开淘宝活动首页，点击领喵币，开启领喵币中心
# 然后允许脚本
if __name__ == '__main__':
    if len(sys.argv) > 1:
        device_name = sys.argv[1]
    while check_node():
        continue
