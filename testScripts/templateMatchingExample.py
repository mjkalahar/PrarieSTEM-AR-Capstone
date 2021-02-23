import cv2
import socket
import numpy as np
from matplotlib import pyplot as plt

DEBUG = True
path = r'mockFrame.png'
logoPath = r'template.png'
t = 100
w = 640.0
methods = ['cv2.TM_CCOEFF', 'cv2.TM_CCOEFF_NORMED', 'cv2.TM_CCORR',
            'cv2.TM_CCORR_NORMED', 'cv2.TM_SQDIFF', 'cv2.TM_SQDIFF_NORMED']

# methods = ['cv2.TM_CCORR']

try:
    template_rgb = cv2.imread(logoPath)
    search_rgb = cv2.imread(path)
    search_gray = cv2.cvtColor(search_rgb, cv2.COLOR_BGR2GRAY)
    template_gray = cv2.cvtColor(template_rgb, cv2.COLOR_BGR2GRAY)

    sift = cv2.SIFT()
    
    h, w = search_gray.shape[:2]
    th, tw = template_gray.shape[:2]
    while True:
        for meth in methods:
            method = eval(meth)
            found = None
            for scale in np.linspace(0.2, 1.0, 20)[::-1]:

                width = int(search_gray.shape[1] * scale)
                height = int(search_gray.shape[0] * scale)
                dim = (width, height)
                search_resized = cv2.resize(search_gray, dim)
                r = search_gray.shape[1] / float(search_resized.shape[1])
                search_edged = cv2.Canny(search_resized, 50, 200)
                template_edged = cv2.Canny(template_gray, 50, 200)
                result = cv2.matchTemplate(search_edged, template_edged, method)
                (_, maxVal, _, maxLoc) = cv2.minMaxLoc(result) 

                if search_resized.shape[0] < h or search_resized.shape[1] < w:
                    break
                found = (maxVal, maxLoc, r)
                    
            (_, maxLoc, r) = found
            (startX, startY) = (int(maxLoc[0] * r), int(maxLoc[1] * r))
            (endX, endY) = (int((maxLoc[0] + tw) * r), int((maxLoc[1] + th) * r))
                

            output = search_rgb.copy()


            cv2.rectangle(output, (startX, startY), (endX, endY), (0, 0, 255), 2)
            plt.subplot(121),plt.imshow(result)
            plt.title('Matching Result'), plt.xticks([]), plt.yticks([])
            plt.subplot(122),plt.imshow(output)
            plt.title('Detected Point'), plt.xticks([]), plt.yticks([])
            plt.suptitle(meth)
            plt.show()
finally:
    pass
