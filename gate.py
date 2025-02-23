
from pickle import TRUE
import cv2                                 # [Open-source] Image Processing s/w  
import numpy as np                         # Used for manipulating Images
from pdf2image import convert_from_path    # Convert the entire PDF to images                    
import re
import sys
from unidecode import unidecode
import pytesseract
from pytesseract import Output
import imghdr
import io
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'  # Update this path
custom_oem_psm_config = r'-l eng+tam+hin+tel --oem 1 '

l=[]
def text_clean(text):
    #text = text.lower()
    text = text.replace(",","")
    text = text.replace("|","")
    return text


def find_keyword_higlight(TestFileName):
    print(imghdr.what(TestFileName))
    if imghdr.what(TestFileName) == None:
        images = convert_from_path(TestFileName, dpi=500)
        if images:
            # Show dimensions of the first page
            img= np.array(images[0])
            #Convert to BGR for OpenCV compatibility
            img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
 #   else:
  #      img =  cv2.imread(TestFileName)
     
    #images = convert_from_path(TestFileName, dpi=400)
    #img = np.array(images[0])
    img_bytes=[]
    print(img.shape)
    x1,y1,z=img.shape
    text=''
    d = pytesseract.image_to_data(img, output_type=Output.DICT, lang='eng')
    print(d['text'])
    name=False
    mark=False
    year=False
    
    n_boxes = len(d['level'])
    if(n_boxes<250):
                
                img1= img
                text  = pytesseract.image_to_string(img1,config=custom_oem_psm_config)
                _, img_encoded = cv2.imencode('.png', img1)
                img_bytes.append(io.BytesIO(img_encoded.tobytes()))
                return text,img_bytes
    else:
        for i in range(n_boxes):
            if text_clean(d['text'][i])=='GATE' and ( text_clean(d['text'][i+2])=='Scorecard' or text_clean(d['text'][i+2])=='scorecard' ) :
            
              (x, y, w, h) = (d['left'][i], d['top'][i], d['width'][i], d['height'][i])
              (xx,yy,ww)=(d['left'][i+2], d['top'][i+2],d['width'][i+2])
              print(x,y,w,h)
              u=int((x1/3300)*900)
              l=int((y1/2550)*10)
              au=int((x1/3300)*10)
              al=int((y1/2550)*100)
              print(u,l,au,al)
              
              img1= img[y-au:y+h+u,x-al:xx+ww+l]

              t = pytesseract.image_to_string(img1,config=custom_oem_psm_config)
              text=text+text_clean(t)
              print(text)
              year=True
              _, img_encoded = cv2.imencode('.png', img1)
              img_bytes.append(io.BytesIO(img_encoded.tobytes()))

    if text=='':
        text = ' '.join(d['text'])
    return text,img_bytes

def process_gate(pdf_path):
    
    extracted_data,l = find_keyword_higlight(pdf_path)
    print(extracted_data)
    print(unidecode(extracted_data))
    result_str = "Extracted Data:\n"
    
    name_pattern = r"[T][o][^\n]*[\n][\n][^\n]*[\n][\n][^\n]*[A-Za-z ]{3,50}[^\n]*|[T][o][^\n]*[\n][^\n]*[\n][^\n]*[A-Za-z ]{3,50}[^\n]*"
    date_pattern = r"[0-9][0-9][0-9][0-9]"
    mobr=r"[0-9]{2}[.][0-9]{1,4}| [0-9]{2,3} "

    name_match = re.search(name_pattern, extracted_data , re.IGNORECASE)
    date_match = re.search(date_pattern, extracted_data , re.IGNORECASE)
    mob = re.search(mobr, extracted_data , re.IGNORECASE)
    user_details={}
    if name_match:
        user_details['Name'] = name_match.group(0).strip().split("\n")[len(name_match.group(0).strip().split("\n"))-1]
        print("has")
    else: 
        user_details['Name']=extracted_data
    if date_match:
        user_details['Date'] = date_match.group(0).strip().split(" ")[len(date_match.group(0).strip().split(" "))-1]
    else:
        user_details['Date']=' '
   
    if mob:
        user_details['Mobile'] = mob.group(0).strip()
    else:
        user_details['Mobile']=' '
    for key,value in user_details.items():
        result_str += f"{key}: {value}\n"

    name,dob,mobile = text_clean(user_details['Name']),text_clean(user_details['Date']),text_clean(user_details['Mobile'])
    print(f"{name},{dob},{mobile}")
    return f"{name},{dob},{mobile}",l

if __name__ == "__main__":
    print('maincalled')
    file_path = sys.argv[1]
    print(process_gate(file_path))