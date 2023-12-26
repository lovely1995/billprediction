
#共用FUC
import os
from flask import request,jsonify
import json
import fitz  # PyMuPDF
#from PIL import Image, ImageDraw,ImageFont

def convertPdfToPng(pdf_path,tpe):
    # 打开PDF文件
    pdf_document = fitz.open(pdf_path)
    # 设置更高的分辨率（DPI）
    dpi = 300  # 可以根据需要调整
    for page_number in range(pdf_document.page_count):
        # 获取PDF页面
        page = pdf_document[page_number]

        # 获取页面尺寸（以点为单位）
        rect = page.rect

        # 将页面转换为图像
        #image = page.get_pixmap()
        # 将页面转换为图像，设置更高的分辨率
        image = page.get_pixmap(matrix=fitz.Matrix(dpi/72, dpi/72))
        # 将图像保存为PNG文件
        image.save(f"D:/G0G00/CarbonWeb/static/bill/paddleCase/pic/{tpe}_page_{page_number + 1}.png", "PNG")

    # 关闭PDF文件
    pdf_document.close()
from paddleocr import PaddleOCR
def OCR (path):
    #models
    cls_model_dir="D:/.paddleocr/whl/cls/ch_ppocr_mobile_v2.0_cls_infer"
    det_model_dir="D:/.paddleocr/whl/det/ch/ch_PP-OCRv4_det_infer"
    rec_model_dir="D:/.paddleocr/whl/rec/ch/ch_PP-OCRv4_rec_infer"
    
    ocr = PaddleOCR(use_angle_cls=True, lang="ch",det_model_dir=det_model_dir,cls_model_dir=cls_model_dir,rec_model_dir=rec_model_dir)
    #ocr = PaddleOCR(use_angle_cls=True, lang="ch")
    img_path = path
    result = ocr.ocr(img_path, cls=True)
    return result
import cv2


def drawYoloBoxes(image_path,output_path, coordinates,label):
    # 讀取圖片
    image = cv2.imread(image_path)

    # 將座標轉換為整數
    coordinates = [(int(x), int(y)) for x, y in coordinates]

    # 繪製邊框
    color = (0, 255, 0)  # BGR格式，這裡使用綠色
    thickness = 2
    for i in range(len(coordinates) - 1):
        cv2.line(image, coordinates[i], coordinates[i + 1], color, thickness)
        cv2.line(image, coordinates[-1], coordinates[0], color, thickness)

    # 在圖片上寫上文字
    font = cv2.FONT_HERSHEY_SIMPLEX
    font_scale = 0.5
    font_thickness = 1

    # 計算文字區域大小
    text_size = cv2.getTextSize(label, font, font_scale, font_thickness)[0]
    text_width, text_height = text_size[0], text_size[1]

    # 設定文字底色區域
    # 設定文字底色區域，增加空間
    background_padding = 5  # 設定額外的空間
    rect_background = (
        (coordinates[0][0], coordinates[0][1] - text_height - background_padding),
        (coordinates[0][0] + text_width + background_padding, coordinates[0][1] + background_padding)
    )

    # 填充底色
    cv2.rectangle(image, rect_background[0], rect_background[1], color, thickness=cv2.FILLED)

    # 寫上文字
    text_position = (coordinates[0][0], coordinates[0][1] - 5)
    cv2.putText(image, label, text_position, font, font_scale, (0, 0, 0), font_thickness)  # 文字使用黑色


    # 保存結果
    cv2.imwrite(output_path, image)

    



def labelTarget(pureStr,content,res,out):
    # 将每个子列表的两个元素组成元组，并创建新的列表
    xy = [(point[0], point[1]) for point in content[0]]
    number = content[1][1]*100
    acc = "{:.5f}".format(number)
    label = f"{content[1][0]} {acc}%"  if pureStr==""  else f"{pureStr} {acc}%"
    
    drawYoloBoxes(res,out, xy, label)

def findFile(path):
    if os.path.exists(path):
        return True
    else:
        return False



#電費單
def ele(data):
    try:
        # 获取JSON数据
        # data = json.loads(request.data.decode('utf-8'))
        # 在这里可以处理接收到的JSON数据
        # 例如，访问特定字段
        path = data['PATH']

        #pdf轉png
        #convertPdfToPng("ori/1.pdf","ELE")
        convertPdfToPng("D:/G0G00/CarbonWeb/static/bill/paddleCase/ori/"+path,"ELE")
        #電費
        elePage1=OCR('D:/G0G00/CarbonWeb/static/bill/paddleCase/pic/ELE_page_1.png')
        elePage2=OCR('D:/G0G00/CarbonWeb/static/bill/paddleCase/pic/ELE_page_2.png')
        #1
        picPath1="D:/G0G00/CarbonWeb/static/bill/paddleCase/pic/ELE_page_1.png"
        existPath1="D:/G0G00/CarbonWeb/static/bill/target/ELE_show1.png"
        usePath1 =""
        try:
            os.remove(existPath1)
        except:
            _=""
        #2
        picPath2="D:/G0G00/CarbonWeb/static/bill/paddleCase/pic/ELE_page_2.png"
        existPath2="D:/G0G00/CarbonWeb/static/bill/target/ELE_show2.png"
        usePath2 =""
        try:
            os.remove(existPath2)
        except:
            _=""
        #電度數
        co2Value=0
        eleValue=0
        date=""
        
        #第一張
        for line in elePage1:
            for word_info in line:
                
                if(findFile(existPath1)): 
                    usePath1=existPath1
                else:
                    usePath1=picPath1
                    
                # 提取文字和坐标
                worContent = word_info[1]
                xy = word_info[0]
                
                if '公斤' in worContent[0]:
                    pureStr=worContent[0].replace(" ", "").replace("公斤", "")
                    labelTarget(pureStr,word_info,usePath1,existPath1)
                    co2Value=pureStr
                    print(f"碳排 {pureStr}")
                if ('年' in worContent[0]) and ('月' in worContent[0]) and ('力' in worContent[0]):
                    pureStr=worContent[0].replace(" ", "").split('年')[1].split('月')[0]
                    labelTarget(pureStr,word_info,usePath1,existPath1)
                    date=pureStr
                    print(f"月份 {pureStr}")
        #第二張
        for line in elePage2:
            i =0
            for word_info in line:
                if(findFile(existPath2)): 
                    usePath2=existPath2
                else:
                    usePath2=picPath2
                    
                # 提取文字和坐标
                worContent = word_info[1]

                #找出本期
                if '本期' in worContent[0] and len(worContent[0])==2:
                    #本期的下兩個為數值
                    word_info_target=line[i+2]
                    labelTarget("",word_info_target,usePath2,existPath2)
                    eleValue=word_info_target[1][0]
                    print(f"度數 {eleValue}")
                
                i=i+1
                
        # 電度數,月份
        return jsonify(
                {
                    'STATUS': 'success', 
                    'VALUE':eleValue,#電度數
                    'CO2VALUE':co2Value,
                    'DATE':date,#日期
                    'PICPATH':picPath1,#原始照片
                    'TARGETPATH':existPath1,#標記目標的照片
                    'PICPATH2':picPath2,#原始照片
                    'TARGETPATH2':existPath2#標記目標的照片
                }
            )

    except Exception as e:
        return jsonify({'status': 'error', 'error_message': str(e)})
    # try:
    #     print(request)
    #     json_data =json.loads(request.data.decode('utf-8'))
    #     print(json.loads(request.data.decode('utf-8')))
    #     if 'PATH' not in json_data:
    #         return jsonify({'status': 'error', 'error_message': 'PATH not in json'})
    # except Exception as e:
    #     print(e)
    
    # print(request)




#水費單
def water(data):
    try:
        # 获取JSON数据
        #data = json.loads(request.data.decode('utf-8'))
        # 在这里可以处理接收到的JSON数据
        # 例如，访问特定字段
        path = data['PATH']
        
        #pdf轉png
        #convertPdfToPng("ori/1.pdf","ELE")
        convertPdfToPng("D:/G0G00/CarbonWeb/static/bill/paddleCase/ori/"+path,"WATER")

        
        #pdf轉png
        #convertPdfToPng("ori/2023-9月自來水費0927.pdf","WATER")
        #convertPdfToPng(path,"WATER")
        #水費
        waterPage1=OCR('D:/G0G00/CarbonWeb/static/bill/paddleCase/pic/WATER_page_1.png')
        
        picPath="D:/G0G00/CarbonWeb/static/bill/paddleCase/pic/WATER_page_1.png"
        existPath="D:/G0G00/CarbonWeb/static/bill/target/WATER_show1.png"
        usePath =""

        #水度數
        waterValue=0
        waterValueBckup=0
        date=""
        
        try:
            os.remove(existPath)
        except:
            _=""
            
        #第一張
        for line in waterPage1: 
            i =0       
            for word_info in line:
                #
                if(findFile(existPath)): 
                    usePath=existPath
                else:
                    usePath=picPath

                # 提取文字和坐标
                worContent = word_info[1]
        
                #找出本期日期
                if '列印日期' in worContent[0] :
                    labelTarget(worContent[0],word_info,usePath,existPath)
                    eleValue=worContent[0].replace("列印日期","")
                    month=eleValue.split('.')[1]
                    date=month
                    print(f"月份 {month}")


                if '本期實用' in worContent[0]:
                #本期的下兩個為數值
                    word_info_target=line[i+1]
                    #labelTarget("",word_info,usePath,existPath)
                    labelTarget("",word_info_target,usePath,existPath)
                    eleValue=word_info_target[1][0]
                    waterValue=eleValue
                    print(f"度數 {eleValue}")
                    
                if '本期' in worContent[0] and len( worContent[0])==2:
                #本期的下兩個為數值
                    word_info_target=line[i+1]
                    #labelTarget("",word_info,usePath,existPath)
                    labelTarget("",word_info_target,usePath,existPath)
                    eleValue=word_info_target[1][0]
                    waterValueBckup=eleValue
                    print(f"備用度數 {eleValue}")

                i=i+1
    
        # 水度數,備用水度數,月份
        return jsonify(
                {
                    'STATUS': 'success', 
                    'VALUE':waterValue,#水度數
                    'VALUE2':waterValueBckup,#水度數 次選擇
                    'DATE':date,#日期
                    'PICPATH':picPath,#原始照片
                    'TARGETPATH':existPath#標記目標的照片
                }
            )
    except Exception as e:
        # 如果发生异常，返回错误响应
        return jsonify({'status': 'error', 'error_message': str(e)})