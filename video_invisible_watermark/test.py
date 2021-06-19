from pathlib import Path
import cv2
import numpy as np
from videotools import Video, YuvVideo
from watermarktools import WatermarkDecoder, WatermarkEncoder

# wmImPath= Path("C:\\Users\\FOM\\Documents\\Development\\WatermarkingForense\\Tests\\mp4Tests\\AsianFusion_VMAFViterbiQualityBasedAdaptor_Trace_0.mp4")
yuvPath = Path('C:\\Users\\FOM\\Documents\\Development\\WatermarkingForense\\Tests\\ref\\BigBuckBunny_25fps_1920x1080_trimm.yuv')
# reference = Video(wmImPath)
yuvVideo = YuvVideo(yuvPath, 1920, 1080, 25)

# Encode Yuv Result
encoder = WatermarkEncoder()
wm = 'popo'

encoder.set_watermark('bytes', wm.encode('utf-8'))

yuvEncoded = encoder.encode(yuvVideo, 'dwtDct')

# Decode Yuv Result
decoder = WatermarkDecoder('bytes', 32)
newYuv = open(yuvEncoded.name, 'rb')
for i in range(yuvEncoded.nframes):

    yuvFrame = np.frombuffer(newYuv.read(yuvEncoded.width*yuvEncoded.heigth*3//2), dtype=np.uint8).reshape((yuvEncoded.heigth*3//2, yuvEncoded.width))
    bgrEnc = cv2.cvtColor(yuvFrame, cv2.COLOR_YUV2BGR_I420)
    watermark = decoder.decode(bgrEnc, 'dwtDct')
    print(watermark.decode('utf-8'))
