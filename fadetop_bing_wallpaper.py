# -*- coding: utf-8 -*-
import datetime
import re
import os
import time
from multiprocessing import Process
import ssl

try:
    from urllib.request import Request
except ImportError:
    from urllib2 import Request


def urlopen(req):
    try:
        from urllib.request import urlopen as f
        return f(req, context=ssl._create_unverified_context())
    except:
        from urllib2 import urlopen as f
        return f(req)


def urlretrieve(url, path):
    try:
        from urllib.request import urlretrieve as f
        print(3)
        return f(url, path)
    except:
        with open(path, 'wb') as f:
            f.write(urlopen(url).read())


headers = {
    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
    'accept-language': 'en-US,en;q=0.9,zh-CN;q=0.8,zh;q=0.7',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.138 Safari/537.36',
}


def get_config():
    config_file_path = os.path.join(os.path.split(
        os.path.realpath(__file__))[0], 'config.txt')
    exe_dir, motto, other = r'C:\Program Files (x86)\FadeTop', '请在config.txt文件中配置', '第一行为FadeTop.exe所在目录, 第二行为格言内容, FadeTop所在目录示例:C:\Program Files (x86)\FadeTop'
    if os.path.exists(config_file_path):
        with open(config_file_path, 'r') as m:
            exe_dir, motto = m.read().split('\n')[:2]
        if not os.path.exists(os.path.join(exe_dir, 'FadeTop.exe')):
            motto = 'config.txt文件中, FadeTop所在目录有错'
            exe_dir = ''
    else:
        if os.path.exists(os.path.join(exe_dir, 'FadeTop.exe')):
            exe_dir = 'C:\Program Files (x86)\FadeTop'
        else:
            exe_dir = ''
        with open(config_file_path, 'w') as m:
            m.write(exe_dir + '\n' + motto + '\n' + other)
    return exe_dir, motto


def change_wallpaper(motto, image_path):
    setting_xml_path = os.path.join(
        os.environ['USERPROFILE'], 'AppData\\Local\\FadeTop\\Settings.xml')

    if not os.path.exists(setting_xml_path):
        return
    with open(setting_xml_path, 'r+') as f:
        setting_xml_str = f.read()
        if not setting_xml_str:
            return
        f.seek(0)
        f.truncate()
        setting_xml_str = setting_xml_str.replace(
            re.search('(bg_image_file=".*?")', setting_xml_str).group(),
            'bg_image_file="{}"'.format(image_path)
        ).replace(
            re.search('(bg_image_enabled=".*?")', setting_xml_str).group(),
            'bg_image_enabled="1"'
        ).replace(
            re.search('(<Foreground.*?fg_message.*?/>)',
                      setting_xml_str).group(),
            '<Foreground fg_color="#FFFFFF" fg_position="center" fg_offset_x="0" fg_offset_y="0" fg_time_format="auto" fg_message="{}" />'.format(
                motto)
        )
        f.write(setting_xml_str)


def kill_FadeTop():
    os.system('taskkill /F /im FadeTop.exe')


def start_FadeTop(exe_dir):
    os.system('"{}"'.format(os.path.join(exe_dir, 'FadeTop.exe')))


def get_bing_image():
    image_path = get_dynamic_bing_image()
    if image_path:
        return image_path
    url = 'https://cn.bing.com'
    req = Request(url)
    for k, v in headers.items():
        req.add_header(k, v)
    content = urlopen(req).read()
    image_name = re.search('<link id="bgLink".*?href="/th\?id=(.*?\.jpg).*?".*?>',
                           str(content),
                           re.S
                           ).groups()[0]
    image_path = os.path.join(os.path.split(os.path.realpath(__file__))[
                              0], 'fadetop_wallpaper.jpg')
    urlretrieve(url+'/th?id='+image_name, image_path)
    return image_path


def get_dynamic_bing_image():
    tmp_path = os.path.join(
        os.environ['USERPROFILE'], 'AppData\\Local\\Packages\\')
    dy_path = [i for i in os.listdir(tmp_path) if 'DynamicTheme' in i]
    if not dy_path:
        return
    dy_path = dy_path[0]
    dynamic_theme_path = os.path.join(
        tmp_path,
        dy_path,
        'LocalState\\Bing'
    )
    if not os.path.isdir(dynamic_theme_path):
        return None
    return os.path.join(
        dynamic_theme_path, os.listdir(dynamic_theme_path)[-1])


def run():
    if os.path.exists('f_id'):
        with open('f_pid', 'r') as f:
            pid = f.read()
            if pid:
                os.system("taskkill /pid {} /f".format(pid))

    with open('f_pid', 'w') as f:
        f.write(str(os.getpid()))
    exe_dir, motto = get_config()
    kill_FadeTop()
    change_wallpaper(motto, get_bing_image())
    if exe_dir:
        start_FadeTop(exe_dir)
    else:
        raise Exception('Place set FadeTop dir in config.txt on 1th line.')


def main():
    run()
    while True:
        if datetime.datetime.now().hour == 18:
            run()
        time.sleep(3600)


if __name__ == "__main__":
    Process(target=main).start()
    os.system("taskkill /pid {} /f".format(os.getpid()))
