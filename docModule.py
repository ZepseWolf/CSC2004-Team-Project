
import sys
from zipfile import ZipFile
import os
import shutil

#astring = payload in base64
def docEncode(filename, aString):
	infilename = os.path.join("./source",filename+".docx")
	newname = infilename.replace('.docx', '.zip')
	os.rename(infilename, newname)
	shutil.unpack_archive("./source/"+filename+".zip", "./source/doctemp")
	
	infilename2 = os.path.join("./source",filename+".zip")
	newname2 = infilename2.replace('.zip', '.docx')
	os.rename(infilename2, newname2)

	toWriteString = ""
	with ZipFile("./source/"+filename+".docx", 'r') as zipObject:
		try:
			with zipObject.open('word/styles.xml',"r") as f:
				xmlText = f.read().decode('UTF-8') 
				frontIndex = xmlText.rfind("w:styleId=\"")  # 11 is the num of char in this string
				if frontIndex < 0:
					print("Possible no w:styleId in word/styles.xml." )
					return -1
				else:
					sliceFront = slice(frontIndex+11)
					sliceBack = slice(frontIndex+11,len(xmlText))

					frontString = xmlText[sliceFront]
					backString = xmlText[sliceBack]
					endindex = backString.find("\"")

					sliceContent = slice(endindex,len(xmlText))
					backString = backString[sliceContent]
					toWriteString = frontString+aString+backString

					f.close()
		except:
			print("Possible corrupted docx given." )
			return -1
		
	with open("./source/doctemp/word/styles.xml", "w") as f:
		f.write(toWriteString)
		f.close()
	try:
		os.remove("./output/"+filename+"_encoded"+".docx")
	except:
		print("File not exist before.")
	
	shutil.make_archive("./output/"+filename+"_encoded", 'zip', "./source/doctemp")	
	infilename3 = os.path.join("./output",filename+"_encoded"+".zip")
	newname3 = infilename3.replace('.zip', '.docx')
	os.rename(infilename3, newname3)
	return 0

def docDecode(filename):
	decodedString = ""
	with ZipFile("./source/"+filename+".docx", 'r') as zipObject:
		try:
			with zipObject.open('word/styles.xml',"r") as f:
				xmlText = f.read().decode('UTF-8') 
				frontIndex = xmlText.rfind("w:styleId=\"")  # 11 is the num of char in this string
				if frontIndex < 0:
					print("Possible no w:styleId in word/styles.xml." )
					return -1
				else:
					sliceFront = slice(frontIndex+11)
					sliceBack = slice(frontIndex+11,len(xmlText))
					
					backString = xmlText[sliceBack]
					endindex = backString.find("\"")

					sliceContent = slice(endindex)
					backString = backString[sliceContent]
					decodedString = backString

					f.close()
		except:
			print("Possible corrupted docx given." )
			return -1
		
	return decodedString

# sys.modules[__name__] = encode ,decode 