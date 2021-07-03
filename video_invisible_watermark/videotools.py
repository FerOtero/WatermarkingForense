import cv2
import sys
import os
import subprocess as sp
from pathlib import Path
from logger import get_logger

log_level = 'DEBUG'
outputLog = ("C:\\Users\\FOM\\Documents\\Development\\WatermarkingForense\\video_invisible_watermark\\logs\\watermarking.log")
logger = get_logger(level=log_level, job_id=None, path=outputLog, name='VideoTools')

class YuvVideo:
    def __init__(self, name: Path, width: int, heigth:int, framerate: float, nframes = 0):
        self._name = Path(name)
        self._width = width
        self._heigth = heigth
        if os.path.exists(name):
            self._size = os.path.getsize(name)
            self._nframes = self._size // (self._width*self._heigth*3 // 2)
        if nframes != 0:
            self._nframes = nframes            
        self._framerate = framerate
 
    @property
    def name(self):
        return Path(self._name)

    @property
    def nframes(self):
        return int(self._nframes)
    
    @property
    def heigth(self):
        return int(self._heigth)
    
    @property
    def width(self):
        return int(self._width)

    @property
    def framerate(self):
        return self._framerate
    
    @property
    def size(self):
        if self._size == 0 and os.path.exists(self._name):
            self._size = os.path.getsize(self._name)
            return self._size
        return self._size

    def YUV2ts (self, heigth = 0 , width = 0, qp = 0 ):
        outputPath = f"{self._name.parents[0]}/{self._name.stem}_qp_{qp}.ts"
        if (heigth == 0 and width == 0):
            sp.run(f'ffmpeg -s {int(self._width)}x{int(self._heigth)} -r {self._framerate} -i {self._name} -c:v libx264 -preset ultrafast -r {self._framerate} -qp {qp} {outputPath}')
        else:
            sp.run(f'ffmpeg -s {int(width)}x{int(heigth)} -r {self._framerate} -i {self._name} -c:v libx264 -preset ultrafast -r {self._framerate} -qp {qp} {outputPath}')
    
        outputVideo = Video(outputPath)
        return outputVideo


    
class Video:
    def __init__(self, name: Path):
        self._name = Path(name)
        self.__video = cv2.VideoCapture(str(self._name))
        if self.__video.isOpened():
            self._width = self.__video.get(cv2.CAP_PROP_FRAME_WIDTH)
            self._heigth = self.__video.get(cv2.CAP_PROP_FRAME_HEIGHT)
            self._framerate = self.__video.get(cv2.CAP_PROP_FPS)
        else:
            logger.info("Video not found at this address:", sys.exc_info()[0])
            raise 
    
    def Video2YUV(self, start=0, duration=0):
        # sp.run('ffmpeg -y -f lavfi -i testsrc=size={}x{}:rate=1 -pix_fmt yuv420p -t 10 {}'.format(width, height, yuv_filename))
        if start!=0 or duration!=0:
            outputPath = f"{self._name.parents[0]}/{self._name.stem}_start_{int(start)}s_end_{int(duration)}_{int(self._width)}x{int(self._heigth)}.yuv"
            sp.run(f'ffmpeg -ss {int(start)} -i {self._name} -t {int(duration)} -vcodec rawvideo -pix_fmt yuv420p -filter:v yadif -y {outputPath}')
        else:
            outputPath = f"{self._name.parents[0]}/{self._name.stem}_{int(self._width)}x{int(self._heigth)}.yuv"
            sp.run(f'ffmpeg -i {self._name} -vcodec rawvideo -pix_fmt yuv420p -filter:v yadif -y {outputPath}')
        return YuvVideo(outputPath, self._width, self._heigth, self._framerate)
        



