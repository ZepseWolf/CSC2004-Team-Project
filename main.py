from tkinter import EXCEPTION
import eel
import base64
from docModule import docEncode, docDecode 

from png import main_png
from mp3 import main_audio
from Better_Video import videotest2

@eel.expose
def encodeFile(fileName , coverBase64 , payloadFileName , payloadBase64 , isTextBox , lsb):
    exit_flag = 0
    lsb = int(lsb)
    fileType = fileName.split(".")[1]
    data = str.encode(coverBase64.split(",")[1])
    leftover = coverBase64.split(",")[0]
    if len(leftover)>0:
        leftover+=","

    isBase64 = False
    if isTextBox: 
        # 'shunyao is stinky'
        payloadFileName = "text"
        payloadBase64 = "text,;meow;,"+payloadBase64
        # print(payloadBase64)

    elif ('.txt' in payloadFileName) and (fileType == "jpg" or fileType == "png"):
        payloadData = str.encode(payloadBase64.split(",")[1])
        with open("./source/"+payloadFileName, 'wb') as output_file:
            output_file.write(base64.decodebytes(payloadData))

         # 'krabby_patty.txt'
        payloadBase64 = payloadFileName
    else:
        payloadBase64 = payloadFileName+",;meow;,"+payloadBase64 
        isBase64 = True
    
    # Copy a empty coverBase file
    with open("./source/"+fileName, 'wb') as output_file:
        output_file.write(base64.decodebytes(data))
    
    
    if fileType== "docx" :
        # If cover is a docx file enter here
        docEncode(fileName.split(".")[0],payloadBase64)

    elif fileType == "jpg" or fileType == "png" :
        exit_flag = main_png.encodeMain(fileName, payloadBase64, isTextBox, isBase64, lsb)
        print("[*] Exit Flag: ", exit_flag)
        fileType = "png"

    elif fileType == "mp3" :
        exit_flag = main_audio.mainEncode(fileName, payloadBase64, lsb)
        fileType = "wav"
        print("[*] Exit Flag: ", exit_flag)

    elif fileType == "mp4" :
        exit_flag = videotest2.encodeVideo(fileName, payloadBase64, lsb)
        print("[*] Exit Flag: ", exit_flag)
    try:
        if exit_flag == -1:
            return {"success": False ,"message": "File is too big to be encoded"}
        else:
            # return {"success": False ,"message": "Some input error , please try again."}
            if not fileType == "mp4":
                with open("./output/"+fileName.split(".")[0]+"_encoded."+fileType, "rb") as file:
                    decodeBase64 = leftover+base64.b64encode(file.read()).decode('utf-8')
                    return {"success": True,"message": "File had successfully been encoded.","fileName": fileName.split(".")[0]+"_encoded."+fileType, "src": decodeBase64}
            else:
                return {"success": True,"message": "File had successfully been encoded.","fileName": fileName.split(".")[0]+"_encoded."+fileType, "src": "video"}
    except Exception as e :
        print("[*] Error raised: ", e )
        return {"success": False ,"message": "Some input error , please try again."}
    # except:
    #     print("Possible no file found.")

@eel.expose
def decodeFile(fileName, encodedBase64 ,lsb):
    fileType = fileName.split(".")[1]
    lsb = int(lsb)
   
    if not (fileType == "mp4" or fileType == "avi"):
        data = str.encode(encodedBase64.split(",")[1])
        with open("./source/"+fileName, 'wb') as output_file:
            output_file.write(base64.decodebytes(data))
    
    if fileType == "docx" :
        decodedString = docDecode(fileName.split(".")[0])
        itemtype = decodedString.split(",;meow;,")[0]
        decodeBase64 = decodedString.split(",;meow;,")[1]
        # print(decodeBase64)
        if itemtype =="text":
            return {"fileName": "text", "src": decodeBase64}
        else:
            x = decodeBase64
            try:
                x = decodeBase64.split(",")[1]
            except:
                pass
            data2 =str.encode(x)
            try:
                with open("./output/"+itemtype, "wb") as output_file:
                    output_file.write(base64.decodebytes(data2))
            except Exception as e :
                print("[*] Error raised: ", e )

            return {"fileName": itemtype, "src": decodeBase64}
        
    elif fileType == "jpg" or fileType == "png" :
        txtfilename, secret_type, secret_str = main_png.decodeMain(fileName)
        '''
        secret_type
        0: normal str
        1: base64 str
        2: txtfile str
        '''
        if secret_type == 0 :
            itemtype = secret_str.split(",;meow;,")[0]
            decodeBase64 = secret_str.split(",;meow;,")[1]
            return {"fileName": itemtype, "src": decodeBase64}

        elif secret_type == 1:
            itemtype = secret_str.split(",;meow;,")[0]
            decodeBase64 = secret_str.split(",;meow;,")[1]
            x = decodeBase64
            try:
                x = decodeBase64.split(",")[1]
            except:
                pass
            data2 =str.encode(x)
            try:
                with open("./output/"+itemtype, "wb") as output_file:
                    output_file.write(base64.decodebytes(data2))
            except Exception as e :
                print("[*] Error raised: ", e )
            return {"fileName": itemtype, "src": decodeBase64}

        elif secret_type == 2:
            
            return {"fileName": txtfilename, "src": secret_str}
        
    elif fileType == "mp3" or fileType == "wav" :
        # print()
        payload = main_audio.mainDecode(fileName, lsb)
        # print(payload)
        itemtype = payload.split(",;meow;,")[0]
        decodeBase64 = payload.split(",;meow;,")[1]
        if itemtype =="text":
            return {"fileName": "text", "src": decodeBase64}
        else:
            x = decodeBase64
            try:
                x = decodeBase64.split(",")[1]
            except:
                pass
            data2 =str.encode(x)
            try:
                with open("./output/"+itemtype, "wb") as output_file:
                    output_file.write(base64.decodebytes(data2))
            except Exception as e :
                print("[*] Error raised: ", e )

            return {"fileName": itemtype, "src": decodeBase64}
            

    elif fileType == "mp4" or fileType == "avi":
        payload = videotest2.decodeVideo(fileName.split(".")[0])
        print(payload)
        itemtype = payload.split(",;meow;,")[0]
        decodeBase64 = payload.split(",;meow;,")[1]
        if itemtype =="text":
            return {"fileName": "text", "src": decodeBase64}
        else:
            x = decodeBase64
            try:
                x = decodeBase64.split(",")[1]
            except:
                pass
            data2 =str.encode(x)
            try:
                with open("./output/"+itemtype, "wb") as output_file:
                    output_file.write(base64.decodebytes(data2))
            except Exception as e :
                print("[*] Error raised: ", e )
            return {"fileName": itemtype, "src": decodeBase64}
        
eel.init('www')
eel.start('index.html')