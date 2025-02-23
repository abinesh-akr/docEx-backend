''' PREPROCESSING '''
import cv2                                 # [Open-source] Image Processing s/w  
import numpy as np                         # Used for manipulating Images
from pdf2image import convert_from_path    # Convert the entire PDF to images                    
import re
import sys
from unidecode import unidecode
import pytesseract
from pytesseract import Output
import imghdr
import os
import io
#.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'  # Update this path
custom_oem_psm_config = r'-l eng+tam+hin+tel --oem 1 '

l=[]
def text_clean(text):
    #text = text.lower()
    text = text.replace(",","")
    return text


def find_keyword_higlight(TestFileName):
    img_bytes=[]
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
 
    x1,y1,z=img.shape

    d = pytesseract.image_to_data(img, output_type=Output.DICT, lang='eng')

    n_boxes = len(d['level'])
    text=''
    if(n_boxes<250):
                
                img1= img
                text  = pytesseract.image_to_string(img1,config=custom_oem_psm_config)
                _, img_encoded = cv2.imencode('.png', img1)
                img_bytes.append(io.BytesIO(img_encoded.tobytes()))
                return text,img_bytes
    else:
        for i in range(n_boxes-1):
            if ((text_clean(d['text'][i])=='income') or (text_clean(d['text'][i])=='income'))  and text_clean(d['text'][i+1])=='Certificate' :
            
              (x, y, w, h) = (d['left'][i], d['top'][i], d['width'][i], d['height'][i])
              print(x,y,w,h)
              u=int((x1/3300)*900)
              l=int((y1/2550)*600)
              au=int((x1/3300)*100)
              al=int((y1/2550)*200)
              
              img1= img[y-au:y+u,0:y1]
 
              t = pytesseract.image_to_string(img1,config=custom_oem_psm_config)
              text=text+t
              _, img_encoded = cv2.imencode('.png', img1)
              img_bytes.append(io.BytesIO(img_encoded.tobytes()))
              
            elif text_clean(d['text'][i+1])=='Certificate' :
            
              (x, y, w, h) = (d['left'][i], d['top'][i], d['width'][i], d['height'][i])
              print(x,y,w,h)
              u=int((x1/3300)*900)
              l=int((y1/2550)*600)
              au=int((x1/3300)*100)
              al=int((y1/2550)*200)
              
              img1= img[y-au:y+u,0:y1]
         
              t = pytesseract.image_to_string(img1,config=custom_oem_psm_config)
              text=text+t
              _, img_encoded = cv2.imencode('.png', img1)
              img_bytes.append(io.BytesIO(img_encoded.tobytes()))
            elif  text_clean(d['text'][i])=='Unique' :
              (x, y, w, h) = (d['left'][i], d['top'][i], d['width'][i], d['height'][i])
              print(x,y,w,h)
              u=int((x1/3300)*900)
              l=int((y1/2550)*800)
              au=int((x1/3300)*0)
              al=int((y1/2550)*0)
            
              img1= img[y-au:x1,x-al:x+l]
              
              t = pytesseract.image_to_string(img1,config=custom_oem_psm_config)
              text = text+t
              _, img_encoded = cv2.imencode('.png', img1)
              img_bytes.append(io.BytesIO(img_encoded.tobytes()))
    if text=='':
        text = ' '.join(d['text'])
    print(text)
    return text,img_bytes

def process_income(pdf_path):
    
    extracted_data,li = find_keyword_higlight(pdf_path)
    print(li)
    result_str = "Extracted Data:\n"
    
    name_pattern = r"(Selvan|Thiru)[A-Za-z0-9 ]{1,50} son|[A-Za-z]{1,50} [A-Za-z]{1,50} [A-Za-z]{1,50} son"
    date_pattern = r"Rs. [0-9]{1,10}"
    fatherp = r"Certificate No: [A-Z][A-Z][-][0-9]{12}" #Cert.no


    name_match = re.search(name_pattern, extracted_data , re.IGNORECASE)
    date_match = re.search(date_pattern, extracted_data , re.IGNORECASE)
    father = re.search(fatherp, extracted_data , re.IGNORECASE)

    user_details={}
    if name_match:
        user_details['Name'] = name_match.group(0).strip().split(' ')[1:len(name_match.group(0).strip().split(" "))-1]
        user_details['Name'] = ' '.join(user_details['Name'])
        print("has")
    else: 
        user_details['Name']=extracted_data
    if date_match:
        user_details['Date'] = date_match.group(0).strip().split(" ")[len(date_match.group(0).strip().split(" "))-1]
    else:
        user_details['Date']=' '
    
    if father:
        user_details['Father'] = ' '.join([f for f in father.group(0).split()[2:]])
        user_details['Father']=user_details['Father'].replace(",",'')
        
    else:
        user_details['Father']= ' '

    for key,value in user_details.items():
        result_str += f"{key}: {value}\n"

    name,father,dob  = text_clean(user_details['Name']),text_clean(user_details['Father']),text_clean(user_details['Date'])
    print(f"{name},{dob},{father}")
    print(li)
    return f"{name},{dob},{father}",li

if __name__ == "__main__":

    file_path = sys.argv[1]
    print(process_income(file_path))