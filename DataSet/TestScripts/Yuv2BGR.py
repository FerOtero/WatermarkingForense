from typing import List
import cv2
import numpy as np
import os
import subprocess as sp
from imwatermark import WatermarkEncoder, WatermarkDecoder

# Build synthetic video and read binary data into memory (for testing):
#########################################################################
# mp4_filename = 'input.mp4'  # the mp4 is used just as reference
yuv_filename = 'C:\\Users\\FOM\\Documents\\Development\\WatermarkingForense\\Tests\\ref\\BigBuckBunny_25fps_1920x1080_trimm.yuv'
YUVoutputPath = (f"C:\\Users\\FOM\\Documents\\Development\\WatermarkingForense\\Tests\\mierdasvarias\\output_wmarked.yuv")
width, height = 1920, 1080
# fps = 1 # 1Hz (just for testing)

# Build synthetic video, for testing (the mp4 is used just as reference):
# sp.run('ffmpeg -y -f lavfi -i testsrc=size={}x{}:rate=1 -vcodec libx264 -crf 18 -t 10 {}'.format(width, height, mp4_filename))
# sp.run('ffmpeg -y -f lavfi -i testsrc=size={}x{}:rate=1 -pix_fmt yuv420p -t 10 {}'.format(width, height, yuv_filename))
#########################################################################

encoder = WatermarkEncoder()
decoder = WatermarkDecoder('bytes', 32)
wm = 'popo'
encoder.set_watermark('bytes', wm.encode('utf-8'))
file_size = os.path.getsize(yuv_filename)

# Number of frames: in YUV420 frame size in bytes is width*height*1.5
n_frames = file_size // (width*height*3 // 2)

# Open 'input.yuv' a binary file.
f = open(yuv_filename, 'rb')
newYuv = open(YUVoutputPath, 'ab')

for i in range(n_frames):
    # Read Y, U and V color channels and reshape to height*1.5 x width numpy array
    yuv = np.frombuffer(f.read(width*height*3//2), dtype=np.uint8).reshape((height*3//2, width))

    # Convert YUV420 to BGR (for testing), applies BT.601 "Limited Range" conversion.
    bgr = cv2.cvtColor(yuv, cv2.COLOR_YUV2BGR_I420)

    # yuv2 = cv2.cvtColor(bgr, cv2.COLOR_BGR2YUV)
    (row, col, channels) = bgr.shape
    bgr_encoded = encoder.encode(bgr, "dwtDct")
    yuv_encoded = cv2.cvtColor(bgr_encoded, cv2.COLOR_BGR2YUV)

    matYCbCr = []
    matYCbCr = cv2.split(yuv_encoded)

    matCbHalf = cv2.resize(matYCbCr[1], (int(width/2) , int(height/2)), interpolation = cv2.INTER_CUBIC)
    matCrHalf = cv2.resize(matYCbCr[2], (int(width/2) , int(height/2)), interpolation = cv2.INTER_CUBIC)

    newYuv.write(matYCbCr[0])
    newYuv.write(matCbHalf)
    newYuv.write(matCrHalf)

    outputPath = (f"C:\\Users\\FOM\\Documents\\Development\\WatermarkingForense\\Tests\\outputTests\\output_wmarked_{i}.png")
    cv2.imwrite(outputPath, bgr_encoded)

newYuv.close()
newYuv = open(YUVoutputPath, 'rb')
for i in range(n_frames):

    yuvFrame = np.frombuffer(newYuv.read(width*height*3//2), dtype=np.uint8).reshape((height*3//2, width))
    bgrEnc = cv2.cvtColor(yuvFrame, cv2.COLOR_YUV2BGR_I420)
    watermark = decoder.decode(bgrEnc, 'dwtDct')
    print(watermark.decode('utf-8'))

    # Convert YUV420 to Grayscale
    # gray = cv2.cvtColor(yuv, cv2.COLOR_YUV2GRAY_I420)

    #Show RGB image and Grayscale image for testing
    # cv2.imshow('rgb', bgr)
    # cv2.waitKey(500)  # Wait a 0.5 second (for testing)
    # cv2.imshow('gray', gray)
    # cv2.waitKey(500)  # Wait a 0.5 second (for testing)

f.close()
newYuv.close()
cv2.destroyAllWindows()