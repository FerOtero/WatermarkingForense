from logging import error, log
from pathlib import Path
import cv2
import numpy as np
from datetime import datetime
from videotools import Video, YuvVideo
from watermarktools import WatermarkDecoder, WatermarkEncoder
from logger import get_logger

log_level = 'DEBUG'
outputLog = ("C:\\Users\\FOM\\Documents\\Development\\WatermarkingForense\\video_invisible_watermark\\logs\\watermarking.log")
logger = get_logger(level=log_level, job_id=None, path=outputLog, name='Main')


# Input YUV420
# yuvPath = Path('DataSet\\Video\\References_YUV420\\BigBuckBunny_25fps_1920x1080\\BigBuckBunny_25fps_1920x1080.yuv')
# yuvPath = Path('DataSet\\Video\\References_YUV420\\BirdsInCage_30fps_1920x1080\\BirdsInCage_30fps_1920x1080.yuv')
# yuvPath = Path('DataSet\\Video\\References_YUV420\\CrowdRun_25fps_1920x1080\\CrowdRun_25fps_1920x1080.yuv')
# yuvPath = Path('DataSet\\Video\\References_YUV420\\ElFuente1_30fps_1920x1080\\ElFuente1_30fps_1920x1080.yuv')
# yuvPath = Path('DataSet\\Video\\References_YUV420\\FoxBird_25fps_1920x1080\\FoxBird_25fps_1920x1080.yuv')
# yuvPath = Path('DataSet\\Video\\References_YUV420\\Tennis_24fps_1920x1080\\Tennis_24fps_1920x1080.yuv')
yuvs = [Path('DataSet\\Video\\References_YUV420\\BigBuckBunny_25fps_1920x1080\\BigBuckBunny_25fps_1920x1080.yuv'),
Path('DataSet\\Video\\References_YUV420\\BirdsInCage_30fps_1920x1080\\BirdsInCage_30fps_1920x1080.yuv'),
Path('DataSet\\Video\\References_YUV420\\CrowdRun_25fps_1920x1080\\CrowdRun_25fps_1920x1080.yuv'),
Path('DataSet\\Video\\References_YUV420\\ElFuente1_30fps_1920x1080\\ElFuente1_30fps_1920x1080.yuv'),
Path('DataSet\\Video\\References_YUV420\\FoxBird_25fps_1920x1080\\FoxBird_25fps_1920x1080.yuv'),
Path('DataSet\\Video\\References_YUV420\\Tennis_24fps_1920x1080\\Tennis_24fps_1920x1080.yuv')]
for yuvPath in yuvs:
    yuvReference = YuvVideo(yuvPath, 1920, 1080, 25)

    # Encode Yuv Result
    # 1 Initiate  the encoder and the password
    logger.info('############################################################################################################')
    logger.info('--------------------------------------(<~*3*)~--------------------------------------FOM---------------------')
    logger.info('Start Watermark Insertion Process in: ')
    logger.info(f'{yuvReference.name}')
    encoder = WatermarkEncoder()
    wm = 'popo'
    logger.info(f'Watermark key:{wm} ')
    encoder.set_watermark('bytes', wm.encode('utf-8'))
    # 2 Encode File 
    yuvEncoded = encoder.encode(yuvReference, 'dwtDct')
    logger.info('End of insertion Process. Yuv Watermarked in:')
    logger.info(f'{yuvEncoded.name}')
    logger.info('############################################################################################################')

    # --------------------------------------------------------------------------------------------------
    logger.info('############################################################################################################')
    logger.info('--------------------------------------(<~*3*)~--------------------------------------FOM---------------------')
    logger.info('Extracting Watermark from:')
    logger.info(f'Watermarked Video: {yuvEncoded.name}')
    logger.info('############################################################################################################')
    # 1 Initiate  the decoder
    decoder = WatermarkDecoder('bytes', 32)
    # 2 Open YUV420 file and read it frame by frame binary
    newYuv = open(yuvEncoded.name, 'rb')
    unreadable=0
    readable=0
    missed=0
    for i in range(yuvEncoded.nframes):
        yuvFrame = np.frombuffer(newYuv.read(yuvEncoded.width*yuvEncoded.heigth*3//2), dtype=np.uint8).reshape((yuvEncoded.heigth*3//2, yuvEncoded.width))
        bgrEnc = cv2.cvtColor(yuvFrame, cv2.COLOR_YUV2BGR_I420)
        watermark = decoder.decode(bgrEnc, 'dwtDct')
        try:
            readableWM = watermark.decode('utf-8')
            logger.info(f'# Frame {i}: {readableWM}')
            if readableWM == wm:
                readable+=1
            else:
                missed+=1
        except UnicodeDecodeError:
            unreadable+=1
            logger.info(f'# Frame {i}: {watermark} Error unreadable WM')
            
    newYuv.close()
    logger.warning(f'{unreadable}/{yuvEncoded.nframes} Frames had an unreadable Watermark')
    logger.info(f'The Watermark was retreived from {readable}/{yuvEncoded.nframes} Frames')
    logger.info(f'The Watermark was lost in {missed+unreadable}/{yuvEncoded.nframes} Frames')
    logger.info('############################################################################################################')
    logger.info('--------------------------------------(<~*3*)~--------------------------------------FOM-------------------')
    logger.info('############################################################################################################')
    logger.info('#                                                                                                          #')
    logger.info('#                             END OF THE EXTRACTION FROM ORIGINAL YUV                                      #')
    logger.info('#                                                                                                          #')
    # --------------------------------------------------------------------------------------------------
    logger.info('############################################################################################################')
    logger.info('--------------------------------------(<~*3*)~--------------------------------------FOM-------------------')
    logger.info('Start Threshold Testing Process ')

    qp = [0, 10, 20, 21, 22, 23, 24, 25, 26, 27, 28, 30, 40, 50]
    for q in qp:
        watermarkedTS = yuvEncoded.YUV2ts(qp=q)
        logger.info(f'Transcoding Watermarked YUV to h264 at:{watermarkedTS._name} with qp {q}')
        # Get new YUV420 from ts
        watermarkedTS2YUV = watermarkedTS.Video2YUV()
        logger.info(f'Converted new h264 to YUV at:{watermarkedTS._name}')
        # 1 Initiate  the decoder
        decoder2 = WatermarkDecoder('bytes', 32)
        # 2 Open YUV420 file and read it frame by frame binary
        logger.info('Extracting Watermark')
        logger.info(f'Watermarked Video: {watermarkedTS2YUV.name}')
        newYuv = open(watermarkedTS2YUV.name, 'rb')
        unreadable=0
        readable=0
        missed=0
        for i in range(watermarkedTS2YUV.nframes):
            yuvFrame = np.frombuffer(newYuv.read(watermarkedTS2YUV.width*watermarkedTS2YUV.heigth*3//2), dtype=np.uint8).reshape((watermarkedTS2YUV.heigth*3//2, watermarkedTS2YUV.width))
            bgrEnc = cv2.cvtColor(yuvFrame, cv2.COLOR_YUV2BGR_I420)
            watermark = decoder2.decode(bgrEnc, 'dwtDct')
            try:
                readableWM = watermark.decode('utf-8')
                logger.info(f'# Frame {i}: {readableWM}')
                if readableWM == wm:
                    readable+=1
                else:
                    missed+=1
            except UnicodeDecodeError:
                unreadable+=1
                logger.info(f'# Frame {i}: {watermark} Error unreadable WM')

        logger.info('Extracted Watermark from Video {watermarkedTS._name} ')
        logger.warning(f'{unreadable}/{watermarkedTS2YUV.nframes} Frames had an unreadable Watermark')
        logger.info(f'The Watermark was retreived from {readable}/{watermarkedTS2YUV.nframes} Frames')
        logger.info(f'The Watermark was lost in {missed+unreadable}/{watermarkedTS2YUV.nframes} Frames')
        logger.info('############################################################################################################')
        logger.info('--------------------------------------(<~*3*)~--------------------------------------FOM---------------------')
    logger.info('############################################################################################################')
    logger.info('#                                                                                                          #')
    logger.info('#                                 END OF THE EXTRACTION FOR THRESHOLD                                      #')
    logger.info('#                                                                                                          #')
    logger.info('############################################################################################################')
    # resultTxt.close()
    newYuv.close()