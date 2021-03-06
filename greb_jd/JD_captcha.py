# -*- coding: utf-8 -*-
# https://github.com/ohhal/EasyGrab

import base64
import os

import cv2
import numpy as np
from PIL import Image
from numpy import ndarray


def base2ndarray(img_base64: str) -> ndarray:
    return np.frombuffer(base64.b64decode(img_base64.split(',')[1]), np.uint8)


def cmp_hash(img_array: ndarray) -> str:
    '''
    :return: 原图标签（判断是那张验证码原图）
    '''

    def aHash(img):
        img = cv2.resize(img, (8, 8), interpolation=cv2.INTER_CUBIC)
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        s = 0
        hash_str = ''
        for i in range(8):
            for j in range(8):
                s = s + gray[i, j]
        avg = s / 64
        for i in range(8):
            for j in range(8):
                if gray[i, j] > avg:
                    hash_str = hash_str + '1'
                else:
                    hash_str = hash_str + '0'
        return hash_str

    def cmpHash(hash1, hash2):
        n = 0
        if len(hash1) != len(hash2):
            return -1
        for i in range(len(hash1)):
            if hash1[i] != hash2[i]:
                n = n + 1
        return n

    def getkey(x, dict_x):
        for (key_x, value_x) in dict_x.items():
            if x in value_x:
                return key_x

    dict = {'3.jpg': '1011111110111111101100100011001000110011001100100011001000110011',
            '4.jpg': '0000011000010010001000101111111111111110111111001111100011100000',
            '7.jpg': '0000000100000001000000010000000100001101000011110000111100011111',
            '0.jpg': '0000111000011011000111110001101100010101000110110001101100001000',
            '5.jpg': '1000110000010101011100011110001111011110010001001011101101011111',
            '6.jpg': '1111011111011110110111011111111111111111111111111111110111111101',
            '8.jpg': '1010010011110010101101111010111111011110011111100011100001111110',
            '9.jpg': '1111111111111111111111111111101111000011110000011100000111100011',
            '1.jpg': '0011110000111100001111000011110000011100000110000000000000001000',
            '2.jpg': '0000000000000000000011000001110000011100000001000000110000001000'}

    list_lable = list()
    img = cv2.imdecode(img_array, cv2.COLOR_RGB2BGR)
    hash_img = aHash(img)
    for x in dict.values():
        label = (cmpHash(hash_img, x), getkey(x, dict))
        list_lable.append(label)
    list_lable.sort()
    return list_lable[0][1]


def get_distance(img_array: ndarray, y_label: str) -> int:
    '''
    :param img_array: 缺失图片
    :param y_img: 原始图片label
    :return: 返回滑块滑到最左边的距离
    '''
    current_path = os.path.abspath(__file__)
    father_path = os.path.abspath(os.path.dirname(current_path) + os.path.sep + ".")
    path = os.path.join(father_path, 'img')
    y_name = path + '/' + y_label
    q_img = cv2.imdecode(img_array, cv2.COLOR_RGB2BGR)
    y_img = Image.open(y_name)
    y_img = np.asarray(y_img)
    if len(y_img.shape) > 2:
        y_img = cv2.cvtColor(y_img, cv2.COLOR_RGB2BGR)
    q_gray = cv2.cvtColor(q_img, cv2.COLOR_BGR2GRAY)
    y_gray = cv2.cvtColor(y_img, cv2.COLOR_BGR2GRAY)
    w = y_img.shape[0]
    h = y_img.shape[1]
    list_1 = []
    for y in range(h - 1):
        for x in range(w - 1):
            if abs(int(q_gray[x, y]) - int(y_gray[x, y])) > 25:  # 阀值
                p = (y, x)
                list_1.append(p)
    list_1.sort()
    distance = list_1[0][0]
    return distance


def jd_captcha(img_base64: str) -> float:
    img_array = base2ndarray(img_base64)
    y_label = cmp_hash(img_array)
    distance = get_distance(img_array, y_label)
    return distance * (278 / 360)


if __name__ == '__main__':
    img_base = '''
    data:image/png;base64,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
    '''
    print(jd_captcha(img_base))
