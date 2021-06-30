from pathlib import Path
import cv2
import numpy as np
from datetime import datetime
from videotools import Video, YuvVideo
from watermarktools import WatermarkDecoder, WatermarkEncoder

# Input YUV420
yuvPath = Path('C:\\Users\\FOM\\Documents\\Development\\WatermarkingForense\\DataSet\\Video\\References_YUV420\\CrowdRun_25fps_1920x1080.yuv')
yuvReference = YuvVideo(yuvPath, 1920, 1080, 25)

# Encode Yuv Result
# 1 Initiate  the encoder and the password
print('############################################################################################################ \n')
print('Start Encoding Process \n')
encoder = WatermarkEncoder()
wm = 'popo'
print(f'Watermark key:{wm} \n')
encoder.set_watermark('bytes', wm.encode('utf-8'))
# 2 Encode File 
yuvEncoded = encoder.encode(yuvReference, 'dwtDct')
print(f'End Decoding Process \nYuv Watermarked in {yuvEncoded.name}\n')

# --------------------------------------------------------------------------------------------------
print('############################################################################################################ \n')
print('Start Decoding Process \n')


# Decode Yuv Result
resultTxt = open('C:\\Users\\FOM\\Documents\\Development\\WatermarkingForense\\DataSet\\TestOutput\\decodeResult.txt', 'at',  encoding='utf-8')
resultTxt.write('--------------------------------------(<~￣3￣)~--------------------------------------FOM------------------- \n')
resultTxt.write('############################################################################################################ \n')
resultTxt.write(f'Decoded Video: {yuvEncoded.name} \n')
resultTxt.write(f'Timestamp: {datetime.now()} ')
resultTxt.write('############################################################################################################ \n')
# 1 Initiate  the decoder
decoder = WatermarkDecoder('bytes', 32)
# 2 Open YUV420 file and read it frame by frame binary
newYuv = open(yuvEncoded.name, 'rb')
for i in range(yuvEncoded.nframes):
    yuvFrame = np.frombuffer(newYuv.read(yuvEncoded.width*yuvEncoded.heigth*3//2), dtype=np.uint8).reshape((yuvEncoded.heigth*3//2, yuvEncoded.width))
    bgrEnc = cv2.cvtColor(yuvFrame, cv2.COLOR_YUV2BGR_I420)
    watermark = decoder.decode(bgrEnc, 'dwtDct')
    readableWM = watermark.decode('utf-8')
    print(f'# Frame {i}: {readableWM}\n')
    resultTxt.write(f'# Frame {i}: {readableWM}\n')
resultTxt.write('############################################################################################################ \n')
resultTxt.write('--------------------------------------(<~￣3￣)~--------------------------------------FOM------------------- \n')
resultTxt.close()
newYuv.close()
print(f'End Decoding Process \nResult in {resultTxt.name}')
print('############################################################################################################ \n')
# --------------------------------------------------------------------------------------------------

# Encode lossless YUV420 to MPEG2 video H264
qp = [0, 10, 15]
for q in qp:
    print('############################################################################################################ \n')
    watermarkedTS = yuvEncoded.YUV2ts()
    print(f'Transcoded Watermarked YUV to h264 at:{watermarkedTS._name} \n')
    print('############################################################################################################ \n')
    # Get new YUV420 from ts
    print('############################################################################################################ \n')
    watermarkedTS2YUV = watermarkedTS.Video2YUV()
    print(f'YUV from Watermarked h264 at:{watermarkedTS2YUV.name} \n')
    print('############################################################################################################ \n')

    # 1 Initiate  the decoder
    decoder2 = WatermarkDecoder('bytes', 32)
    # 2 Open YUV420 file and read it frame by frame binary
    print('############################################################################################################ \n')
    print('Start Decoding Process \n')


    resultTxt = open('C:\\Users\\FOM\\Documents\\Development\\WatermarkingForense\\DataSet\\TestOutput\\decodeResult.txt', 'at',  encoding='utf-8')
    resultTxt.write('--------------------------------------(<~￣3￣)~--------------------------------------FOM------------------- \n')
    resultTxt.write('############################################################################################################ \n')
    resultTxt.write(f'Decoded Video: {watermarkedTS2YUV.name} \n')
    resultTxt.write(f'Timestamp: {datetime.now()} ')
    resultTxt.write('############################################################################################################ \n')
    newYuv = open(watermarkedTS2YUV.name, 'rb')
    for i in range(watermarkedTS2YUV.nframes):
        yuvFrame = np.frombuffer(newYuv.read(watermarkedTS2YUV.width*watermarkedTS2YUV.heigth*3//2), dtype=np.uint8).reshape((watermarkedTS2YUV.heigth*3//2, watermarkedTS2YUV.width))
        bgrEnc = cv2.cvtColor(yuvFrame, cv2.COLOR_YUV2BGR_I420)
        watermark = decoder2.decode(bgrEnc, 'dwtDct')
        readableWM = watermark.decode('utf-8')
        print(f'# Frame {i}: {readableWM}\n')
        resultTxt.write(f'# Frame {i}: {readableWM}\n')

    resultTxt.write('############################################################################################################ \n')
    resultTxt.write('--------------------------------------(<~￣3￣)~--------------------------------------FOM------------------- \n')
resultTxt.close()
newYuv.close()