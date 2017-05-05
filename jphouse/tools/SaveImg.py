# -*- coding: UTF-8 -*-
import os, urllib, uuid


# 生成一个文件名字符串
def generateFileName():
    return str(uuid.uuid1())


# 根据文件名创建文件
def createFileWithFileName(localPath, fileName):
    if not os.path.exists(localPath):
        os.makedirs(localPath)
    totalPath = localPath + '\\' + fileName
    if not os.path.exists(totalPath):
        file = open(totalPath, 'a+')
        file.close()
        return totalPath


# 根据图片的地址，下载图片并保存在本地
def getAndSaveImg(imgUrl, localPath):
    if (len(imgUrl) != 0):
        fileName = generateFileName() + '.jpeg'
        urllib.request.urlretrieve(imgUrl, createFileWithFileName(localPath, fileName))
