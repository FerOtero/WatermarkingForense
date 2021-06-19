import cv2
from imwatermark import WatermarkEncoder
wmImPath= "C:\\Users\\FOM\\Documents\\Development\\WatermarkingForense\\VideoWMarker\\Python\\toyStory.png"
bgr = cv2.imread(wmImPath)
wm = 'popo'

encoder = WatermarkEncoder()
encoder.set_watermark('bytes', wm.encode('utf-8'))
bgr_encoded = encoder.encode(bgr, 'dwtDct')

cv2.imwrite('test_wm_4.png', bgr_encoded)
