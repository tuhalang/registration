import numpy as np
import cv2

def find_location(img):
    #img = cv2.imread(url, 0)
    #img = cv2.cvtColor(img)
    blur = cv2.GaussianBlur(img,(5,5),0)
    thresh = cv2.adaptiveThreshold(blur,255,cv2.ADAPTIVE_THRESH_GAUSSIAN_C,cv2.THRESH_BINARY_INV,11,2)

    horizal = thresh
    vertical = thresh

    scale_height = 20
    scale_long = 15

    long = int(img.shape[1]/scale_long)
    height = int(img.shape[0]/scale_height)

    horizalStructure = cv2.getStructuringElement(cv2.MORPH_RECT, (long, 1))
    horizal = cv2.erode(horizal, horizalStructure, (-1, -1))
    horizal = cv2.dilate(horizal, horizalStructure, (-1, -1))

    verticalStructure = cv2.getStructuringElement(cv2.MORPH_RECT, (1, height))
    vertical = cv2.erode(vertical, verticalStructure, (-1, -1))
    vertical = cv2.dilate(vertical, verticalStructure, (-1, -1))

    mask = vertical + horizal

    contours, hierarchy = cv2.findContours(mask,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)

    table = []

    for cnt in contours:
        x, y, w, h = cv2.boundingRect(cnt)
        #print((x,y,w,h))
        if h > 1 and w > 1:
            square = cv2.contourArea(cnt)
            table.append((square,x,y,w,h))

    table.sort(reverse=True)
    #print(table[0])
    return table[0]

def add_matrix(image, mark):
    (a,b) = mark.shape
    (x,y) = image.shape
    delta_y = int((b-y)/2)
    delta_x = int((a-x)/2)
    for i in range(a):
        for j in range(b):
            if(j>delta_y and j<y+delta_y and i>delta_x and i<x+delta_x):
                if 0 != image[i-delta_x][j-delta_y]:
                    mark[i][j]=255
                else:
                    mark[i][j]=0
    return mark

def decode(img, model):
    delta=3
    location = find_location(img)
    start = location[1]+delta
    diff = int((location[3] - 2*delta)/5)
    rs = ""
    for i in range(5):
        sub = img[location[2]:location[2]+location[4],start:start+diff]
        mark = np.zeros((75,75))
        start = start+diff
        sub_img = add_matrix(sub,mark)
        sub_img = sub_img.reshape(-1,75,75,1)
        result = model.predict(sub_img)
        result = np.argmax(result, axis=-1)
        rs = rs + str(result[0])
    return rs