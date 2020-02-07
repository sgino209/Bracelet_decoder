import sys
import cv2
import numpy as np
import imutils
from matplotlib import pyplot as plt

debug = False

img_rgb = cv2.imread('/Users/shahargino/Downloads/frame_gray_'+sys.argv[1]+'.jpg')
img_gray = cv2.cvtColor(img_rgb, cv2.COLOR_BGR2GRAY)
template = cv2.imread('/Users/shahargino/Downloads/template.png',0)
w, h = img_gray.shape[::-1]
tw, th = template.shape[:2]
cv2.imshow("Template", template)

for scale in np.linspace(0.4, 1.2, 20)[::-1]:

    resized = imutils.resize(template, width=int(tw*scale))
    r = template.shape[1] / float(resized.shape[1])

    res = cv2.matchTemplate(img_gray,resized,cv2.TM_CCOEFF_NORMED)

    threshold = 0.7
    loc = np.where( res >= threshold)
    for pt in zip(*loc[::-1]):
        cv2.rectangle(img_rgb, pt, (pt[0] + int(tw*scale), pt[1] + int(th*scale)), (0,0,255), 2)
    
    if debug:
        cv2.imshow("Visualize", img_rgb)
        cv2.waitKey(0)

cv2.imwrite('/Users/shahargino/Downloads/res_'+sys.argv[1]+'.png',img_rgb)
