import numpy as np
import copy
import cv2
import pywt
import math
import pprint
from videotools import YuvVideo
from pathlib import Path
from logger import get_logger

log_level = 'DEBUG'
outputLog = ("C:\\Users\\FOM\\Documents\\Development\\WatermarkingForense\\video_invisible_watermark\\logs\\watermarking.log")
logger = get_logger(level=log_level, job_id=None, path=outputLog, name='Main')

pp = pprint.PrettyPrinter(indent=2)


class EmbedMaxDct(object):
    def __init__(self, watermarks=[], wmLen=8, scales=[0,36,36], block=4):
        self._watermarks = watermarks
        self._wmLen = wmLen
        self._scales = scales
        self._block = block

    # YUV decoding should be made in watermarktools this function should be kept as simple as possible
    def encode(self, yuvInput: YuvVideo):
        yuvFile = open(yuvInput.name, 'rb')
        YUVoutputPath = f"{yuvInput.name.parents[0]}/{yuvInput.name.stem}_encoded.yuv"
        yuvEncoded = YuvVideo(YUVoutputPath, yuvInput.width, yuvInput.heigth, yuvInput.framerate, yuvInput.nframes)
        newYuv = open(YUVoutputPath, 'ab')
        for i in range(yuvInput.nframes):
            # Read one frame
            yuvFrame = np.frombuffer(yuvFile.read(yuvInput.heigth*yuvInput.width*3//2), dtype=np.uint8).reshape((yuvInput.heigth*3//2, yuvInput.width))
            bgr = cv2.cvtColor(yuvFrame, cv2.COLOR_YUV2BGR_I420)
            yuv = cv2.cvtColor(bgr, cv2.COLOR_BGR2YUV)

            (row, col, channels) = bgr.shape
            
            for channel in range(2):
                if self._scales[channel] <= 0:
                    continue

                ca1,(h1,v1,d1) = pywt.dwt2(yuv[:row//4*4,:col//4*4,channel], 'haar')
                self.encode_frame(ca1, self._scales[channel])

                yuv[:row//4*4,:col//4*4,channel] = pywt.idwt2((ca1, (v1,h1,d1)), 'haar')
            
            bgr_encoded = cv2.cvtColor(yuv, cv2.COLOR_YUV2BGR)
            yuv_frame_encoded = cv2.cvtColor(bgr_encoded, cv2.COLOR_BGR2YUV)

            matYCbCr = []
            matYCbCr = cv2.split(yuv_frame_encoded)

            matCbHalf = cv2.resize(matYCbCr[1], (int(yuvInput.width/2) , int(yuvInput.heigth/2)), interpolation = cv2.INTER_CUBIC)
            matCrHalf = cv2.resize(matYCbCr[2], (int(yuvInput.width/2) , int(yuvInput.heigth/2)), interpolation = cv2.INTER_CUBIC)

            newYuv.write(matYCbCr[0])
            newYuv.write(matCbHalf)
            newYuv.write(matCrHalf)

            logger.info(f"Encoding....{int(i*100/yuvInput.nframes)}%")

        yuvFile.close()
        newYuv.close()
        return yuvEncoded

    def decode(self, bgr):
        (row, col, channels) = bgr.shape

        yuv = cv2.cvtColor(bgr, cv2.COLOR_BGR2YUV)

        scores = [[] for i in range(self._wmLen)]
        for channel in range(2):
            if self._scales[channel] <= 0:
                continue

            ca1,(h1,v1,d1) = pywt.dwt2(yuv[:row//4*4,:col//4*4,channel], 'haar')

            scores = self.decode_frame(ca1, self._scales[channel], scores)

        avgScores = list(map(lambda l: np.array(l).mean(), scores))

        bits = (np.array(avgScores) * 255 > 127)
        return bits

    # YUV decoding should be made in watermarktools this function should be kept as simple as possible
    # def decode(self, yuvInput:YuvVideo):
    #     yuvFile = open(yuvInput.name, 'rb')
    #     for i in range(yuvInput.nframes):
    #         yuvFrame = np.frombuffer(yuvFile.read(yuvInput.width*yuvInput.heigth*3//2), dtype=np.uint8).reshape((yuvInput.heigth*3//2, yuvInput.width))
    #         bgr = cv2.cvtColor(yuvFrame, cv2.COLOR_YUV2BGR_I420)
    #         (row, col, channels) = bgr.shape

    #         yuv = cv2.cvtColor(bgr, cv2.COLOR_BGR2YUV)

    #         scores = [[] for i in range(self._wmLen)]
    #         for channel in range(2):
    #             if self._scales[channel] <= 0:
    #                 continue

    #             ca1,(h1,v1,d1) = pywt.dwt2(yuv[:row//4*4,:col//4*4,channel], 'haar')

    #             scores = self.decode_frame(ca1, self._scales[channel], scores)

    #         avgScores = list(map(lambda l: np.array(l).mean(), scores))

    #         bits = (np.array(avgScores) * 255 > 127)
    #         result = tuple.append(bits)
    #     return result

    def decode_frame(self, frame, scale, scores):
        (row, col) = frame.shape
        num = 0

        for i in range(row//self._block):
            for j in range(col//self._block):
                block = frame[i*self._block : i*self._block + self._block,
                              j*self._block : j*self._block + self._block]

                score = self.infer_dct_matrix(block, scale)
                #score = self.infer_dct_svd(block, scale)
                wmBit = num % self._wmLen
                scores[wmBit].append(score)
                num = num + 1

        return scores

    def diffuse_dct_svd(self, block, wmBit, scale):
        u,s,v = np.linalg.svd(cv2.dct(block))

        s[0] = (s[0] // scale + 0.25 + 0.5 * wmBit) * scale
        return cv2.idct(np.dot(u, np.dot(np.diag(s), v)))

    def infer_dct_svd(self, block, scale):
        u,s,v = np.linalg.svd(cv2.dct(block))

        score = 0
        score = int ((s[0] % scale) > scale * 0.5)
        return score
        if score >= 0.5:
            return 1.0
        else:
            return 0.0

    def diffuse_dct_matrix(self, block, wmBit, scale):
        pos = np.argmax(abs(block.flatten()[1:])) + 1
        i, j = pos // self._block, pos % self._block
        val = block[i][j]
        if val >= 0.0:
            block[i][j] = (val//scale + 0.25 + 0.5 * wmBit) * scale
        else:
            val = abs(val)
            block[i][j] = -1.0 * (val//scale + 0.25 + 0.5 * wmBit) * scale
        return block

    def infer_dct_matrix(self, block, scale):
        pos = np.argmax(abs(block.flatten()[1:])) + 1
        i, j = pos // self._block, pos % self._block

        val = block[i][j]
        if val < 0:
            val = abs(val)

        if (val % scale) > 0.5 * scale:
            return 1
        else:
            return 0

    def encode_frame(self, frame, scale):
        '''
        frame is a matrix (M, N)

        we get K (watermark bits size) blocks (self._block x self._block)

        For i-th block, we encode watermark[i] bit into it
        '''
        (row, col) = frame.shape
        num = 0
        for i in range(row//self._block):
            for j in range(col//self._block):
                block = frame[i*self._block : i*self._block + self._block,
                              j*self._block : j*self._block + self._block]
                wmBit = self._watermarks[(num % self._wmLen)]


                diffusedBlock = self.diffuse_dct_matrix(block, wmBit, scale)
                #diffusedBlock = self.diffuse_dct_svd(block, wmBit, scale)
                frame[i*self._block : i*self._block + self._block,
                      j*self._block : j*self._block + self._block] = diffusedBlock

                num = num+1
