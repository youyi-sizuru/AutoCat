仓库转到[码云](https://gitee.com/youyi_sizruru/AutoCat)去了

## 环境

python 3.0

依赖安装：lxml, click, airtest

device_name 可以通过 adb devices 命令来获取，默认取第一个设备

在android手机上开启USB调试和模拟点击.

<img src="preview/usb_setting.jpg" alt="USB调试" width="240px"/>

打开淘宝，打开领猫币界面，运行脚本:

python taobao.py -d your_device_name

<img src="preview/taobao.jpg" alt="淘宝" width="240px"/>

打开支付宝，打开领猫币界面，运行脚本:

python alipay.py -d your_device_name

<img src="preview/alipay.png" alt="支付宝" width="240px"/>

打开京东，打开领金币中心， 运行脚本

python jd.py -d your_device_name  

<img src="preview/jd.png" alt="狗东" width="240px"/>

## 警告

运行前，最好把一些小游戏先点掉（例如喂小鸡，淘宝人生等等），该脚本无法识别这些。

