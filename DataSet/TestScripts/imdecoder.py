import cv2
from imwatermark import WatermarkDecoder

wmImPath= "C:\\Users\\FOM\\Documents\\Development\\WatermarkingForense\\VideoWMarker\\Python\\output_png\\output_wmarked_0.png"
bgr = cv2.imread(wmImPath)
decoder = WatermarkDecoder('bytes', 32)
watermark = decoder.decode(bgr, 'dwtDct')
print(watermark.decode('utf-8'))