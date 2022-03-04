#!/usr/bin/env -S python3 -B
#
# javadoc-cleanup: Github action for tidying up javadocs
# 
# Copyright (c) 2020-2022 Vincent A Cicirello
# https://www.cicirello.org/
#
# MIT License
# 
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
# 
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
# 
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
# 

import sys
import os
import os.path

def tidy(filename, baseUrl=None, extraBlock=None) :
    """The tidy function does the following:
    1) Removes any javadoc timestamps that were inserted by javadoc despite using the
    notimestamp option.
    2) Adds the meta viewport tag to improve browsing javadocs on mobile browsers.
    3) Adds the canonical link (if that option was chosen).

    Keyword arguments:
    filename - The name of the file, including path.
    baseUrl - The url of the documentation site
    extraBlock - A string containing an additional block to insert into the head of
        each page (e.g., can be used for links to favicons, etc).
    """
    modified = False
    generatedByJavadoc = False
    if baseUrl != None :
        canonical = '<link rel="canonical" href="{0}">\n'.format(urlstring(filename, baseUrl))
    with open(filename, 'r+') as f :
        contents = f.readlines()
        for i, line in enumerate(contents) :
            if line.strip() == "<head>" :
                headIndex = i
            elif line.strip().startswith("<!-- Generated by javadoc") :
                generatedByJavadoc = True
                if line.strip() != "<!-- Generated by javadoc -->" :
                    contents[i] = "<!-- Generated by javadoc -->\n"
                    modified = True
                    break
        if generatedByJavadoc and contents[headIndex+1].strip() != "<!-- GitHub action javadoc-cleanup -->" :
            j = 1
            contents.insert(headIndex+j, "<!-- GitHub action javadoc-cleanup -->\n")
            j += 1
            if baseUrl != None :
                contents.insert(headIndex+j, canonical)
                j += 1
            contents.insert(headIndex+j, '<meta name="viewport" content="width=device-width, initial-scale=1">\n')
            j += 1
            if extraBlock != None :
                if extraBlock=="" or extraBlock[-1] != "\n" :
                    extraBlock = extraBlock + "\n"
                contents.insert(headIndex+j, extraBlock)
                j += 1
            contents.insert(headIndex+j, "<!-- End javadoc-cleanup block -->\n")
            modified = True
        if modified :
            f.seek(0)
            f.truncate()
            f.writelines(contents)
    return modified

def urlstring(f, baseUrl) :
    """Forms a string with the full url from a filename and base url.
    
    Keyword arguments:
    f - filename
    baseUrl - address of the root of the website
    """
    if f[0]=="." :
        u = f[1:]
    else :
        u = f
    if len(u) >= 11 and u[-11:] == "/index.html" :
        u = u[:-10]
    elif u == "index.html" :
        u = ""
    if len(u) >= 1 and u[0]=="/" and len(baseUrl) >= 1 and baseUrl[-1]=="/" :
        u = u[1:]
    elif (len(u)==0 or u[0]!="/") and (len(baseUrl)==0 or baseUrl[-1]!="/") :
        u = "/" + u
    return baseUrl + u

if __name__ == "__main__" :
    websiteRoot = sys.argv[1]
    baseUrl = sys.argv[2].strip()
    extraBlock = sys.argv[3] if len(sys.argv[3]) > 0 else None
    
    if not baseUrl.startswith("http") :
        baseUrl = None

    os.chdir(websiteRoot)

    allFiles = []
    for root, dirs, files in os.walk(".") :
        for f in files :
            if len(f) >= 5 and ".html" == f[-5:] :
                allFiles.append(os.path.join(root, f))

    count = 0
    for f in allFiles :
        if tidy(f, baseUrl, extraBlock) :
            count += 1
    
    print("::set-output name=modified-count::" + str(count))
    
    
