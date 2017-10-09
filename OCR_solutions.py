
# coding: utf-8

# In[6]:


import pip


# In[8]:


pip.main(['install','imutils'])


# In[ ]:


from imutils.perspective import four_point_transform


# In[ ]:


from imutils import contours


# In[ ]:


import imutils


# In[ ]:


import cv2


# In[ ]:


# defining dictionary of digiits segments to identify error digits
# A "1" in the array means the given segment is on and "0" in the array means the given segments is off
DIGITS_LOOKUP = {
(1, 1, 1, 0, 1, 1, 1): 0,
(0, 0, 1, 0, 0, 1, 0): 1,
(1, 0, 1, 1, 1, 1, 0): 2,
(1, 0, 1, 1, 0, 1, 1): 3,
(0, 1, 1, 1, 0, 1, 0): 4,
(1, 1, 0, 1, 0, 1, 1): 5,
(1, 1, 0, 1, 1, 1, 1): 6,
(1, 0, 1, 0, 0, 1, 0): 7,
(1, 1, 1, 1, 1, 1, 1): 8,

}


# In[ ]:


# loading the example image
image = cv2.imread("example.jpg")


# In[ ]:


#preprocessing the image by resizing, converting into grayscale, blurring it and computing an edge map
image = imutils.resize(image, height=500)
gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
blurred = cv2.GaussianBlur(gray, (5, 5), 0)
edged = cv2.Canny(blurred, 50, 200, 255)


# In[ ]:


# Let's find contours in the edge map and sort them by size in descending order
cnts = cv2.findContours(edged.copy(), cv2.RETR_EXTERNAL,
cv2.CHAIN_APPROX_SIMPLE)


# In[ ]:


cnts = cnts[0] if imutils.is_cv2() else cnts[1]


# In[ ]:


cnts = sorted(cnts, key=cv2.contourArea, reverse=True)


# In[ ]:


displayCnt = None


# In[ ]:


# looping and approoximating over the contour
#check if the contour has four vertices to find the image display
for c in cnts:
    peri = cv2.arcLength(c, True)
    approx = cv2.approxPolyDP(c, 0.02 * peri, True)
    if len(approx) == 4:
        displayCnt = approx
break


# In[ ]:


# extracting the display by applying a perspective transform
warped = four_point_transform(gray, displayCnt.reshape(4, 2))
output = four_point_transform(image, displayCnt.reshape(4, 2))


# In[ ]:


# thresholding the warped image, cleaning up them using some morphological functions
thresh = cv2.threshold(warped, 0, 255,
cv2.THRESH_BINARY_INV | cv2.THRESH_OTSU)[1]
kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (1, 5))
thresh = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, kernel)


# In[ ]:


# finding contours in the threshold image then initialising the digit contour list
# looping over the digit area, computing the bounding box and identifying the error digit under certain given conditions
cnts = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL,
cv2.CHAIN_APPROX_SIMPLE)
cnts = cnts[0] if imutils.is_cv2() else cnts[1]
digitCnts = []
for c in cnts:
    (x, y, w, h) = cv2.boundingRect(c)
    if w >= 15 and (h >= 30 and h <= 40):   # if it is sufficiently large then it must be digit
digitCnts.append(c)


# In[ ]:


# sort the contours from left to right then initialise the actual digit
digitCnts = contours.sort_contours(digitCnts,
method="left-to-right")[0]
digits = []


# In[ ]:


# To loop each digit, extract their ROI, computing width & height, defining set of 7 segments for each error digit.
for c in digitCnts:
    (x, y, w, h) = cv2.boundingRect(c)
roi = thresh[y:y + h, x:x + w]
(roiH, roiW) = roi.shape
(dW, dH) = (int(roiW * 0.25), int(roiH * 0.15))
dHC = int(roiH * 0.05)
segments = [
((0, 0), (w, dH)), # top
((0, 0), (dW, h // 2)),# top-left
((w - dW, 0), (w, h // 2)), # top-right
((0, (h // 2) - dHC) , (w, (h // 2) + dHC)), # center
((0, h // 2), (dW, h)),	# bottom-left
((w - dW, h // 2), (w, h)), # bottom-right
((0, h - dH), (w, h)) # bottom
]
on = [0] * len(segments)


# In[ ]:


# looping over the segments, extract the segment ROI,counting the total number of threshold pixels in the segment and the area of segment

segROI = roi[yA:yB, xA:xB]
total = cv2.countNonZero(segROI)
area = (xB - xA) * (yB - yA)
if total / float(area) > 0.5: # applying conditions to mark the segment as "on"
     on[i]= 1
digit = DIGITS_LOOKUP[tuple(on)] # looking up the digits and drawing it on the image
digits.append(digit)
cv2.rectangle(output, (x, y), (x + w, y + h), (0, 255, 0), 1)
cv2.putText(output, str(digit), (x - 10, y - 10),
cv2.FONT_HERSHEY_SIMPLEX, 0.65, (0, 255, 0), 2)


# In[ ]:


# displaying the error digits
print(u"{}{}.{} \u00b0C".format(*digits))
cv2.imshow("Input", image)
cv2.imshow("Output", output)
cv2.waitKey(0)

