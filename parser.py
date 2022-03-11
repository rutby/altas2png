
# -*- coding: utf-8 -*-
 
import os
import sys
import os.path
import shutil
from PIL import Image
import json
from optparse import OptionParser
import re

def _parse(filePath, fileName):
    root = os.path.dirname(filePath)
    dstPath = os.path.join(root, fileName)
    atlasFile = filePath
    
    if os.path.exists(dstPath):
        shutil.rmtree(dstPath)
    os.mkdir(dstPath)
    
    sourceImage = None
    sourceAtlas = open(atlasFile, 'r')
    
    sourceAtlas.seek(0, 2)
    total = sourceAtlas.tell()
    sourceAtlas.seek(0, 0)
    
    while(True):
        line = sourceAtlas.readline().strip('\n')
        if sourceAtlas.tell() == total:
            break
        
        match1 = re.match(r'.*\.png', line)
        if match1:
            pngFile = os.path.join(root, line)
            sourceImage = Image.open(pngFile)
            for x in xrange(4):
                sourceAtlas.readline()
        
        match2 = re.match(r'^[^\s]+', line)
        if not match1 and match2:
            name = line.strip('\n')
            rotate = sourceAtlas.readline().split(':')[1].strip('\n').strip(' ') == 'true'
            xy = sourceAtlas.readline().split(':')[1].strip('\n').strip(' ')
            size = sourceAtlas.readline().split(':')[1].strip('\n').strip(' ')
            orig = sourceAtlas.readline().split(':')[1].strip('\n').strip(' ')
            offset = sourceAtlas.readline().split(':')[1].strip('\n').strip(' ')
            sourceAtlas.readline()
        
            width = int(size.split(',')[0])
            height = int(size.split(',')[1])
            if rotate:
                width, height = height, width
                
            ltx = int(xy.split(',')[0])
            lty = int(xy.split(',')[1])
            rbx = ltx + width
            rby = lty + height
            
            splitImage = Image.new("RGBA", (width, height), (0, 0, 0, 0))
            frame = sourceImage.crop((ltx, lty, rbx, rby))
            splitImage.paste(frame, (0, 0, width, height))
            
            levels = name.split('/')
            fixedPath = dstPath
            for i in range(len(levels) -1):
                fullPath = os.path.join(fixedPath, levels[i])
                if not os.path.exists(fullPath):
                    os.mkdir(fullPath)
                fixedPath = fullPath
            splitImage.save(os.path.join(root, fileName, name + '.png'))
    sourceAtlas.close()

def parse(src):
    if os.path.isdir(src):
        for root, dirs, files in os.walk(src):
            for name in files:
                fileName = os.path.splitext(name)[0]
                ext = os.path.splitext(name)[1]
                if ext == '.atlas':
                    _parse(os.path.join(root, name), fileName)
                    
    if os.path.isfile(src):
        fileName = os.path.splitext(src)[0]
        ext = os.path.splitext(src)[1]
        if ext == '.atlas':
            _parse(src, fileName)
    
if __name__ == '__main__':
    optParser = OptionParser()
    optParser.add_option('-i', '--input', action='store', type="string" ,dest='src', default=os.getcwd(), help='input file')
    option, args = optParser.parse_args()
    parse(option.src)
    
 