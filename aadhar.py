''' PREPROCESSING '''
#import cv2                                 # [Open-source] Image Processing s/w  
import numpy as np                         # Used for manipulating Images
from pdf2image import convert_from_path    # Convert the entire PDF to images                    
import re
import sys
from unidecode import unidecode
import pytesseract
from pytesseract import Output
import imghdr
from flask import Flask, request, jsonify, send_file
import os
import io
import cv2
#.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'  # Update this path
custom_oem_psm_config = r'-l eng+tam+hin+tel --oem 1 '

l=[]
def text_clean(text):
    #text = text.lower()
    text = text.replace(",","")
    return text


def find_keyword_higlight(TestFileName):
    print("hiii")
    if os.name == 'nt':  # For Windows
        pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
    else:  # For Linux-based environments
        pytesseract.pytesseract.tesseract_cmd = '/usr/bin/tesseract'    
    if imghdr.what(TestFileName) == None:
        images = convert_from_path(TestFileName, dpi=300)
        if images:
            # Show dimensions of the first page
            img= np.array(images[0])
            #Convert to BGR for OpenCV compatibility
           # img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
    else:
        img =  cv2.imread(TestFileName)
    #images = convert_from_path(TestFileName, dpi=00)
    #img = np.array(images[0])
    img_bytes=[]
    x1,y1,z=img.shape
    text=''
    d = pytesseract.image_to_data(img, output_type=Output.DICT, lang='eng')
 
    n_boxes = len(d['level'])
    if(n_boxes<250):
                
                img1= img
                text  = pytesseract.image_to_string(img1,config=custom_oem_psm_config)
                return text
    else:
        for i in range(n_boxes):
            if text_clean(d['text'][i])=='To' and text_clean(d['text'][i+1])!='establish' :
            
              (x, y, w, h) = (d['left'][i], d['top'][i], d['width'][i], d['height'][i])
              print(x,y,w,h)
              u=int((x1/3300)*600)
              l=int((y1/2550)*600)
              au=int((x1/3300)*10)
              al=int((y1/2550)*100)
           
              img1= img[y-au:x1,x-al:x+l]
              _, img_encoded = cv2.imencode('.png', img1)
              img_bytes.append(io.BytesIO(img_encoded.tobytes()))
              t = pytesseract.image_to_string(img1,config=custom_oem_psm_config)
              text=text+t
              print("1")
              #break
              
            elif  text_clean(d['text'][i])=='Enrollment' or text_clean(d['text'][i])== 'No' or text_clean(d['text'][i])=='Enrolment' :
              (x, y, w, h) = (d['left'][i], d['top'][i], d['width'][i], d['height'][i])
              print(x,y,w,h)
              u=int((x1/3300)*600)
              l=int((y1/2550)*600)
              au=int((x1/3300)*10)
              al=int((y1/2550)*300)
              if(x<al):
                  al=0
        
              
              img1= img[y-au:x1,x-al:x+l]
              _, img_encoded = cv2.imencode('.png', img1)
              img_bytes.append(io.BytesIO(img_encoded.tobytes()))
              t = pytesseract.image_to_string(img1,config=custom_oem_psm_config)
              text = text+t
              print("2")
              #break
            elif  text_clean(d['text'][i])=='Unique' :
              (x, y, w, h) = (d['left'][i], d['top'][i], d['width'][i], d['height'][i])
              print(x,y,w,h)
              u=int((x1/3300)*900)
              l=int((y1/2550)*800)
              au=int((x1/3300)*0)
              al=int((y1/2550)*0)
              print("3")
              img1= img[y-au:x1,x-al:x+l]
              _, img_encoded = cv2.imencode('.png', img1)
              img_bytes.append(io.BytesIO(img_encoded.tobytes()))
              t = pytesseract.image_to_string(img1,config=custom_oem_psm_config)
              text = text+t
              #break
    if text=='':
        text = ' '.join(d['text'])
    #print(text)
    #print("size 123 : ",end=" ")
    print(len(img_bytes))
    return text,img_bytes

def process_aadhar(pdf_path):
    print("hii")
    extracted_data,l = find_keyword_higlight(pdf_path)
    print(l)
    result_str = "Extracted Data:\n"
    
    name_pattern = r"[T][o][^\n]*[\n][\n][^\n]*[\n][\n][^\n]*[A-Za-z ]{3,50}[^\n]*|[T][o][^\n]*[\n][^\n]*[\n][^\n]*[A-Za-z ]{3,50}[^\n]*|[T][o].*[\n].*[\n].*[\n][A-Za-z ]{3,50}"
    date_pattern = r"DOB[^\n]*[0-9][0-9][/][0-9][0-9][/][0-9][0-9][0-9][0-9]|:.*[0-9][0-9][/][0-9][0-9][/][0-9][0-9][0-9][0-9]"
    fatherp = r"[CSWD]/O[:\- ]*[A-Za-z0-9 ]{3,50}[ ]*[\n,]"
    nor= r"[0-9]{4}[ ][0-9]{4}[ ][0-9]{4}"
    mobr=r"[0-9]{10}"
    genr=r"MALE|FEMALE"

    name_match = re.search(name_pattern, extracted_data , re.IGNORECASE)
    date_match = re.search(date_pattern, extracted_data , re.IGNORECASE)
    father = re.search(fatherp, extracted_data , re.IGNORECASE)
    no = re.search(nor, extracted_data , re.IGNORECASE)
    gen = re.search(genr, extracted_data , re.IGNORECASE)
    mob = re.search(mobr, extracted_data , re.IGNORECASE)
    user_details={}
    if name_match:
        user_details['Name'] = name_match.group(0).strip().split("\n")[len(name_match.group(0).strip().split("\n"))-1]
       # print("has")
    else: 
        user_details['Name']=''
    if date_match:
        user_details['Date'] = date_match.group(0).strip().split(" ")[len(date_match.group(0).strip().split(" "))-1]
    else:
        user_details['Date']=''
    if gen:
        user_details['gen'] = gen.group(0).strip()
       # print(user_details['gen'])
    else:
        user_details['gen']= ''
    
    if father:
        user_details['Father'] = ' '.join([f for f in father.group(0).split()[1:]])
        user_details['Father']=user_details['Father'].replace(",",'')
        
    else:
        user_details['Father']= ''
    if no:
        user_details['Number'] = no.group(0).strip()
    else:
        user_details['Number']=''
    if mob:
        user_details['Mobile'] = mob.group(0).strip()
    else:
        user_details['Mobile']=''
    for key,value in user_details.items():
        result_str += f"{key}: {value}\n"

    name,father,dob,aadhar,gen,mobile = text_clean(user_details['Name']),text_clean(user_details['Father']),text_clean(user_details['Date']),text_clean(user_details['Number']),text_clean(user_details['gen']),text_clean(user_details['Mobile'])
  
    return f"{name},{dob},{gen},{father},{mobile},{aadhar}",l

if __name__ == "__main__":

    file_path = sys.argv[1]
    #print(process_aadhar(file_path))
