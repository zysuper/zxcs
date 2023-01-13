import requests
import time
import os
from bs4 import BeautifulSoup
from os import rename
import filetype
import patoolib
import re
import fileinput
import sys
import argparse

download_url = "http://www.zxcs.me/download.php?id="
book_url = "http://www.zxcs.me/post/"

title_string = ""
author_string = ""

no_cover = False

def downloader(url, path):
    start = time.time()
    size = 0
    response = requests.get(url, stream=True)
    chunk_size = 1024
    content_size = int(response.headers['content-length'])
    if response.status_code == 200:
        print('[文件名称]:%s' % path)
        print('[文件大小]:%0.2f MB' % (content_size / chunk_size / 1024))
        with open(path, 'wb') as file:
            for data in response.iter_content(chunk_size=chunk_size):
                file.write(data)
                size += len(data)
                print('\r'+'[下载进度]:%s%.2f%%' % ('>'*int(size*50 /
                                                        content_size), float(size / content_size * 100)), end='')
    end = time.time()
    print('\n' + "[下载状态]:%s下载完成！用时%.2f秒" % (path, (end-start)))
    print('------------------------------')


def rename_file(path):
    file_type = filetype.guess(path)
    rename(path, path + '.' + file_type.extension)


def get_one_page(url):
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.162 Safari/537.36'
        }
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            return response.text
        return None
    except RequestException:
        return None


result = input("请输入书籍编号: ")

pic_url = (book_url+result)
dl_url = (download_url+result)



def get_file_name(dl_url):
    global title_string
    global author_string
    html = get_one_page(dl_url)
    soup = BeautifulSoup(html, 'lxml')
    path = soup.h2.string
    title_string = re.search(r'(?<=《)[^》]+',path)[0]
    author_string = re.search(r'(?<=作者：).*',path)[0]
    return path

filename = (get_file_name(dl_url))

def download_book(dl_url):
    global filename
    html = get_one_page(dl_url)
    soup = BeautifulSoup(html, 'lxml')
    path = filename + '.rar'
    url = soup.find("a", string="线路一").get("href")
    downloader(url=url, path=path)


def download_pic(pic_url):
    global filename
    html = get_one_page(pic_url)
    soup = BeautifulSoup(html, 'lxml')
    path = filename + '.jpg'
    title = soup.find('title').string.split(" - ")[0]
    print(title)
    try:
        url = soup.find("img", title="点击查看原图").get("src")
    except:
        url = soup.find("img", alt=title).get("src")
    downloader(url=url, path=path)

def createConvert(title):
    title_with_sp = " ".join(list(title)) 
    font_width = len(title_with_sp) * 63
    x = 280 - (font_width / 2)
    y = 348 
    cmd = """convert -font "霞鶩文楷等寬-TC-Light" -pointsize 70 -draw "text %d,%d '%s'" cover.jpg output.jpg""" % (x, y, title_with_sp)
    print(">> %s\n" % cmd)
    os.system(cmd)


print("开始下载封面图片.....")
try:
    download_pic(pic_url)
except:
    print("!! 下载封面失败...")
    no_cover = True
    print("自己合成封面...")
    createConvert(title_string)

print("开始下载书籍压缩文件.....")
download_book(dl_url)

rarname = filename + ".rar"
jpgname = "output.jpg" if no_cover else filename + ".jpg"
txtname = filename + ".txt"
epubname = title_string + "-" + author_string + ".epub"
print("正在解压缩文件到当前目录......")
patoolib.extract_archive(rarname, outdir="./")

print("开始文件转码.......")
f = open(txtname, 'r', encoding="gb18030")
content = f.read()
f.close()
f = open(txtname, 'w', encoding="utf-8")
f.write(content)
f.close()


f = open(txtname,'r', encoding="utf-8")
content = f.read()
f.close()


lines = content.split("\n") 
new_content = []
new_content.append("% "+ title_string)
new_content.append("% "+ author_string)
for line in lines:
    if line == "更多精校小说尽在知轩藏书下载：http://www.zxcs.me/" or line == "==========================================================" or line == title_string or line == title_string + " 作者：" + author_string or line == "作者：" + author_string:
        continue
    
    if line == "内容简介：":
        new_content.append("# " + line + "\n")
        continue
    if re.match(r'^\s*([第序][0123456789一二三四五六七八九十零〇百千两]*[章回部节集卷]|卷[0123456789一二三四五六七八九十零〇百千两]*).*',line):
        new_content.append("# " + line + "\n")
        continue
    line = line.replace("　　","")
    new_content.append(line + "\n")
new_content = "\n".join(new_content)

f = open(txtname,'w',encoding="utf=8")
f.write(new_content)
f.close
    

print("开始转换EPUB文件........")
os.system('pandoc "%s" -o "%s" -t epub3 --css=epub.css --epub-cover-image="%s"' % (txtname, epubname, jpgname))

print("开始转换KEPUB文件.........")
os.system('kepubify -i "%s"' % (epubname))

print("删除残留文件......")
os.system("rm '%s'" % (txtname))
os.system("rm '%s'" % (jpgname))
os.system("rm '%s'" % (rarname))
os.system("mv *.kepub.epub ./kepub/")
os.system("mv *.epub ./epub/")
print("完成，收工，撒花！！🎉🎉")
