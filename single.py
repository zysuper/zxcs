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

title_string = ""
author_string = ""

no_cover = False

def createConvert(title):
    title_with_sp = " ".join(list(title)) 
    font_width = len(title_with_sp) * 63
    x = 280 - (font_width / 2)
    y = 348 
    cmd = """convert -font "霞鹜文楷等宽-TC-Light" -pointsize 70 -draw "text %d,%d '%s'" cover.jpg output.jpg""" % (x, y, title_with_sp)
    print(">> %s\n" % cmd)
    os.system(cmd)

def main(filename, titlename):
    rarname = filename + ".rar"
    jpgname = "output.jpg" if no_cover else filename + ".jpg"
    txtname = filename + ".txt"
    epubname = filename + ".epub"
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
        if re.match(r'^\s*([第序][0123456789一二三四五六七八九十零〇百千两]*[章回部节集卷]|卷[0123456789一二三四五六七八九十零〇百千两]).*',line):
            new_content.append("# " + line + "\n")
            continue
        line = line.replace("　　","")
        new_content.append(line + "\n")
    new_content = "\n".join(new_content)

    f = open(txtname,'w',encoding="utf=8")
    f.write(new_content)
    f.close
        
    createConvert(titlename)
    print("开始转换EPUB文件........")
    os.system('pandoc "%s" -o "%s" -t epub3 --css=epub.css --metadata title="%s" --epub-cover-image=output.jpg' % (txtname, epubname, titlename))

    print("开始转换KEPUB文件.........")
    os.system('kepubify -i "%s"' % (epubname))

    print("完成，收工，撒花！！🎉🎉")

if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2])

