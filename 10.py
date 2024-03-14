import os
import glob
import cv2 as cv2
import numpy as np
from lxml import etree

#色と色の二乗距離を計算する関数
def cLength(arr1,arr2):
    return (arr1[0]-arr2[0])**2 + (arr1[1]-arr2[1])**2 + (arr1[2]-arr2[2])**2

#色を与えるとパレットの中から一番近い色を返す関数
def cSelect(color,palettes):
    lengArr = []
    for palette in palettes:
        lengArr.append(cLength(palette,color))
    fillc = palettes[lengArr.index(min(lengArr))]
    return fillc

#階調化に必要な色のボロノイマップ対応辞書をつくる関数。軽量化のため色空間32立方をまとめて1つの写像。フルカラーで8*8*8個
def makeBoronoi(palettes):
    boronoiMap = [[[0 for _ in range(8)] for _ in range(8)] for _ in range(8)]
    for bi, bv in enumerate(boronoiMap):
        for gi, gv in enumerate(bv):
            for ri, rv in enumerate(gv):
                boronoiMap[bi][gi][ri] = cSelect([bi*32,gi*32,ri*32],palettes)
    return boronoiMap

#色を与えると色対応辞書から近い色を返す関数
def cSelect2(color,boronoiMap):
    x = color[0]//32
    y = color[1]//32
    z = color[2]//32
    return boronoiMap[x][y][z]

#階調化画像と色リストから黒シルエットsvgを色数ぶん保存する関数
def gradDevider(image,colorCodes,file):
    colorDicList = list(colorCodes.keys())
    colorCodeList = list(colorCodes.values())
    colorList = [code2bgr(code) for code in colorCodes.values()]

    svgbase = '''
    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 5120 5120">
    </svg>
    '''
    root = etree.fromstring(svgbase)
    if not os.path.exists("SVGs"):
        os.mkdir("SVGs")
    for index, palette in enumerate(colorList):
        if colorDicList[index] != "back":
        
            themec = np.array(colorList[index])  # 抽出する色(bgr)
            extract = cv2.inRange(image, themec, themec) #色の幅ゼロで色抽出
            extract = cv2.bitwise_not(extract) #白黒反転
            kernel = np.ones((5,5),np.uint8)
            extract = cv2.dilate(extract,kernel,iterations = 1)
            extract = cv2.erode(extract,kernel,iterations = 2)

                        
            # bmpを書いてsvgに変換
            name = os.path.splitext(file)[0]
            cv2.imwrite("tmp.bmp",extract)  # 画像の保存
            os.system("potrace -s --flat tmp.bmp") #bmp -> svg
            # os.system("potrace -s -u 0.1 tmp.bmp") #bmp -> svg
            os.system("del tmp.bmp")
            
            # 単色svgからpath要素を抜き出す
            b_tree = etree.parse("tmp.svg")
            paths = b_tree.xpath('//svg:path', namespaces={"svg": "http://www.w3.org/2000/svg"})
            # path要素にfill属性を追加して、g要素に加える
            for path in paths:
                path.set('fill', colorCodeList[index])
                #g.append(path)
                root.append(path)
            # a.svgに書き込む
            with open("./SVGs/"+name+".svg", "wb") as f:
                f.write(etree.tostring(root))
            os.system("del tmp.svg")

def compressColor(pngPath,boronoi):
    # 階調化
    img = cv2.imread(pngPath)
    img = cv2.flip(img, 0)
    h, w = img.shape[:2]
    for i in range(h):
        for j in range(w):
            b, g, r = img[i, j]
            img[i, j] = cSelect2([b,g,r],boronoi)
    return img

def code2bgr(code):
    #色辞書palettDicをbgr配列化
    return [int(code[5:7],16),int(code[3:5],16),int(code[1:3],16)]

#####################実行########################

def png2svg():
    colorCodes = {
        "main": "#000000",
        "c1":"#0E4037",
        "c2":"#26693D",
        "c3":"#678D76",
        "c4":"#C0DC9F",
        "c5":"#380D24",
        "c6":"#A99E34",
        "c7":"#C17265",
        "c8":"#8C2224",
        "back": "#FFFFFF"
    }
    BGRcodes = [code2bgr(code) for code in colorCodes.values()]
    boronoi = makeBoronoi(BGRcodes)

    pngs = glob.glob("*.png")
    for index, png in enumerate(pngs):
        compressedPng = compressColor(png,boronoi)
        # 色ごとに分離
        gradDevider(compressedPng,colorCodes,png)
        #進捗表示
        print(f"{png}をSVG化 {index+1}/{len(pngs)}")



############################COLR書き出し##################################
def split_list_into_chunks(lst, chunk_size):
    """リストを指定されたチャンクサイズごとに分割する関数"""
    return [lst[i:i + chunk_size] for i in range(0, len(lst), chunk_size)]

def svg2ttxs():
    svgs = glob.glob("./SVGs/*.svg")
    chunk_size = 50
    svgchunks = split_list_into_chunks(svgs,chunk_size)
    if not os.path.exists("ttfs"):
        os.mkdir("ttfs")
    for i, svgchunk in enumerate(svgchunks):
        command = f"nanoemoji --color_format glyf_colr_0 {' '.join(svgchunk)}"
        os.system(command)
        os.rename(f'./build/Font.ttf',f'./ttfs/{i*chunk_size+1}-{(i+1)*chunk_size}.ttf')
        os.system(f'ttx ./ttfs/{i*chunk_size+1}-{(i+1)*chunk_size}.ttf')

        print(f'building ttx by nanoemoji {i+1}/{len(svgchunks)}')



##########################################font合成###############################
def localize(fontpath,n):
    #ttx内のglyphnameやcolorの名前の値をすべてのファイルで異なるようにし、後のマージで衝突しないようにする
    with open(fontpath, "r") as file:
        content = file.read()
    root = etree.parse(fontpath).getroot()

    #glyphname
    for ColorGlyph in root.find('COLR').findall('ColorGlyph'):
        unicode = ColorGlyph.get('name')
        for layer in ColorGlyph.findall('layer'):
            glyphname = layer.get('name')
            content = content.replace(f'\"{glyphname}\"', f'\"{unicode}_{glyphname}\"')
    
    #glyphID
    #これは人間用でパース時には無視されるらしいのでローカライズ不要

    #colorID
    colors = root.find('CPAL').find('palette').findall('color')
    for color in colors:
        index = color.get('index') 
        content = content.replace(f'color index=\"{index}\"',f'color index=\"{n+int(index)}\"')
        content = content.replace(f'colorID=\"{index}\"',f'colorID=\"{n+int(index)}\"')

    with open(fontpath, "w") as file:
        file.write(content)
    #色数の合計を返す
    return len(root.find('CPAL').find('palette').findall('color'))

def mergettxs():
    ttxs = glob.glob('./ttfs/*.ttx')
    n = 0
    for i, ttx in enumerate(ttxs):
        n += localize(ttx,n)

    font1 = ttxs[0]
    tree1 = etree.parse(font1)
    root1 = tree1.getroot()

    for index, font2 in enumerate(ttxs[1:]):
        root2 = etree.parse(font2).getroot()

        for child in root2.find('GlyphOrder'):
            if not child.get('id') in ['0','1']:
                root1.find('GlyphOrder').append(child)

        for child in root2.find('hmtx'):
            if not child.get('name') == ".notdef":
                root1.find('hmtx').append(child)

        for child in root1.find('cmap').findall('cmap_format_4')[1:]:
            root1.find('cmap').remove(child)

        for child in root2.find('cmap').find('cmap_format_4').findall('map'):
            if len(child.get('code')) > 4:
                root1.find('cmap').find('cmap_format_4').append(child)

        for child in root2.find('glyf').findall('TTGlyph'):
            if child.get('name') != '.notdef':
                root1.find('glyf').append(child)

        for child in root2.find('COLR').findall('ColorGlyph'):
            root1.find('COLR').append(child)

        colorNums = 0
        colorNums += len(root1.find('CPAL').find('palette').findall('color'))
        colorNums += len(root2.find('CPAL').find('palette').findall('color'))
        root1.find('CPAL').find('numPaletteEntries').set('value',str(colorNums))

        for child in root2.find('CPAL').find('palette').findall('color'):
            root1.find('CPAL').find('palette').append(child)

        print(f'merging ttx {index}/{len(ttxs[1:])}')


    tree1.write(font1, encoding="utf-8", xml_declaration=True)
    os.rename(font1,f'./ttfs/font3.ttx')
    os.system(f'ttx ./ttfs/font3.ttx')
    os.rename(f'./ttfs/font3.ttf',f'./font3.ttx')

png2svg()
svg2ttxs()
mergettxs()
