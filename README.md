[码云](https://gitee.com/youyi_sizruru/AutoCat)

## 警告

~~京东是基于图像识别的（京东活动似乎是个网页，dump下来的信息很少），目前只适配了1080p分辨率的图像，有需求可以fork该仓库，基于自己的手机截图改掉对应的图像~~

**京东图像识别适配性太差，可以去找找其他人更好的写法。**

运行前，最好把一些小游戏先点掉（例如喂小鸡，淘宝人生等等），该脚本无法识别这些。

本项目的所有脚本以及软件仅用于个人学习开发测试,勿用于商业及非法用途，如产生法律纠纷与本人无关。

## 环境

python 3.3以上

依赖安装：lxml, click, airtest, yaml

airtest=1.12.3 修改的获取屏幕截图的方式，运行过程中需要安装yosemite的应用

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



