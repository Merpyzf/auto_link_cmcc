"""
@version: 1.0.0
@author: wangke
@time: 2019/2/24 3:24 PM
@contact: merpyzf@qq.com
@software: PyCharm
"""
import re
import socket
import time
from urllib.parse import unquote

import requests

user_agent = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.14; rv:65.0) Gecko/20100101 Firefox/65.0'
host = 'wlan.jsyd139.com'
# 手机号码
username = '输入你的手机号码'
# 静态密码
pwd = '输入你的静态密码'
is_login = False


def get_local_address():
    hostname = socket.getfqdn(socket.gethostname())
    ip_address = socket.gethostbyname(hostname)
    if ip_address == '127.0.0.1':
        raise AttributeError('程序结束！使用此脚本前请先连接到CMCC-EDU热点')
    return ip_address


def get_base_params():
    """
    获取sto_id和param_str
    :return:
    """
    payload = {
        'wlanacname': '0024.0025.250.00',
        'wlanuserip': get_local_address(),
        'vlan': '3887',
        'NASID': '0785002525000460',
        'ssid': 'CMCC-EDU'
    }
    # wlan.jsyd139.com/?wlanacname=0024.0025.250.00&wlanuserip=172.17.35.101&vlan=3887&NASID=0785002525000460&ssid=CMCC-EDU
    headers = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Encoding': 'gzip, deflate',
        'Accept-Language': 'zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2',
        'Cache-Control': 'max-age=0',
        'Connection': 'keep-alive',
        'Host': host,
        'Upgrade-Insecure-Requests': '1',
        'User-Agent': user_agent
    }
    home_url = 'http://wlan.jsyd139.com'
    r = requests.get(home_url, params=payload, headers=headers)
    # 获取html
    html_text = r.text
    search_obj = re.search('\?paramStr=(.*)" ', html_text, flags=0)
    sto_id = r.cookies.get('sto-id-20480')
    if search_obj and sto_id:
        # 获取参数字符串
        params_str = search_obj.group(1)
        return (params_str, sto_id, r.url)
    else:
        return None


def get_jsessionid(params):
    url = 'http://wlan.jsyd139.com/style/university/index.jsp'
    # 对url传递的参数进行解码
    param_encode = unquote(params[0], 'utf-8')
    payload = {'paramStr': param_encode}
    cookies = {'sto-id-20480': params[1]}
    headers = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Encoding': 'gzip, deflate',
        'Accept-Language': 'zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2',
        'Cache-Control': 'max-age=0',
        'Connection': 'keep-alive',
        'Host': 'wlan.jsyd139.com',
        'Referer': params[2],
        'Upgrade-Insecure-Requests': '1',
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.14; rv:65.0) Gecko/20100101 Firefox/65.0'
    }
    r = requests.get(url, params=payload, cookies=cookies, headers=headers)
    jsessionid = r.cookies.get_dict().get('JSESSIONID')
    if jsessionid:
        return (jsessionid, url + '?paramStr=' + params[0])
    else:
        return None


def auth(params, jsessionid):
    global is_login
    auth_url = 'http://wlan.jsyd139.com/authServlet'
    # 表示当前连接的来源
    referer = jsessionid[1]
    cookies = {
        'sto-id-20480': params[1],
        'JSESSIONID': jsessionid[0]
    }
    headers = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
        'Accept-Encoding': 'gzip, deflate',
        'Accept-Language': 'zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2',
        'Cache-Control': 'max-age=0',
        'Connection': 'keep-alive',
        'Content-Type': 'application/x-www-form-urlencoded',
        'Host': host,
        'Referer': referer,
        'Upgrade-Insecure-Requests': '1',
        'User-Agent': user_agent
    }
    data = {
        'paramStr': unquote(params[0], 'utf-8'),
        'UserType': '1',
        'province': '',
        'pwdType': '1',
        'UserName': username,
        'PassWord': pwd
    }
    r = requests.post(auth_url, data=data, cookies=cookies, headers=headers, allow_redirects=False)
    redirect_location = r.headers['Location']
    if redirect_location.find('fail') != -1:
        is_login = False
        print('认证失败！请按照正常步骤使用此脚本，或关闭wifi后再次使用本脚本登录！')
    else:
        is_login = True
        print('认证成功！')


def logout(params, jsessionid):
    logout_url = 'http://wlan.jsyd139.com/logoutServlet'
    referer = 'http://wlan.jsyd139.com/style/university/logon.jsp' + '?paramStr=' + params[0]
    cookies = {
        'sto-id-20480': params[1],
        'JSESSIONID': jsessionid[0]
    }
    headers = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
        'Accept-Encoding': 'gzip, deflate',
        'Accept-Language': 'zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2',
        'Cache-Control': 'max-age=0',
        'Connection': 'keep-alive',
        'Content-Type': 'application/x-www-form-urlencoded',
        'Host': host,
        'Referer': referer,
        'Upgrade-Insecure-Requests': '1',
        'User-Agent': user_agent
    }
    param_encode = unquote(params[0], 'utf-8')
    print('离线:')
    data = {
        'bOffline': 'true',
        'paramStr': param_encode,
        'userName': username
    }

    r = requests.post(logout_url, data=data, cookies=cookies, headers=headers)
    logout_html = r.text
    success = logout_html.find('下线成功')
    if success != -1:
        print('下线成功！')
        exit(0)
        is_login = False
    else:
        print('下线失败！')
        is_login = True


def main():
    global is_login
    MAX_TRY_COUNT = 5
    params = get_base_params()
    if params is None:
        raise AttributeError('基础参数获取失败,程序结束!')
    jsessionid = get_jsessionid(params)
    if jsessionid is None:
        raise AttributeError('jsessionid获取失败，程序结束！')
    try_num = 0
    auth(params, jsessionid)
    while try_num < MAX_TRY_COUNT:
        if is_login:
            break
        time.sleep(2)
        auth(params, jsessionid)
        try_num += 1
    print('从键盘上键入数字2以注销本账号登录: ')
    while True:
        num = input()
        logout(params, jsessionid)
        if num == 1:
            # 注销登录
            logout(params, jsessionid)
            # 注销失败后进行多次注销尝试
            if is_login == True:
                try_num = 0
                while try_num < MAX_TRY_COUNT:
                    if is_login == False:
                        break
                    time.sleep(2)
                    logout(params, jsessionid)
                    try_num += 1


if __name__ == '__main__':
    try:
        main()
    except AttributeError as error:
        print(error)
        exit(0)
