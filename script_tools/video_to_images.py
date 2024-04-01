# coding=utf-8
import os
import sys

import cv2
import numpy as np
from pathlib import Path

def bgr_to_nv12(rgbData):
    yuvData = cv2.cvtColor(rgbData, cv2.COLOR_BGR2YUV_I420)
    height = rgbData.shape[0]
    width = rgbData.shape[1]
    uData = yuvData[height: height + height // 4, :]
    uData = uData.reshape((1, height // 4 * width))
    vData = yuvData[height + height // 4: height + height // 2, :]
    vData = vData.reshape((1, height // 4 * width))
    uvData = np.zeros((1, height // 4 * width * 2))
    uvData[:, 0::2] = uData
    uvData[:, 1::2] = vData
    uvData = uvData.reshape((height // 2, width))
    nv21Data = np.zeros((height + height // 2, width))
    nv21Data[0:height, :] = yuvData[0:height, :]
    nv21Data[height::, :] = uvData
    nv21Data = nv21Data.astype(dtype=np.uint8)
    return nv21Data


def resize_keep_ratio(img, input_size):
    dst_w = input_size[0]
    dst_h = input_size[1]

    src_w = img.shape[1]
    src_h = img.shape[0]

    if len(img.shape) == 3:
        padded_img = np.ones((dst_h, dst_w, 3), dtype=np.uint8) * 114
    else:
        padded_img = np.ones((dst_h, dst_w), dtype=np.uint8) * 114

    r = min(dst_h / src_h, dst_w / src_w)
    new_w = int(src_w * r)
    new_h = int(src_h * r)

    resized_img = cv2.resize(
        img,
        (new_w, new_h),
        interpolation=cv2.INTER_LINEAR,
    ).astype(np.uint8)

    start_x = int((dst_w - new_w) / 2)
    start_y = int((dst_h - new_h) / 2)

    padded_img[start_y:start_y + new_h, start_x:start_x + new_w] = resized_img

    padded_img = np.ascontiguousarray(padded_img, dtype=np.float32)
    return padded_img, r


if __name__ == '__main__':

    video_path = r"H:\精度统计工具测试视频\yuanqudaolu-baitian.mp4"# 5帧抽取1帧
    # video_path = r"H:\精度统计工具测试视频\xiangcunjiedao3-baitian.mp4"# 25帧抽取1帧
    input_video = cv2.VideoCapture(video_path)
    savd_img_dirpath = Path(video_path.split('\\')[-1]).stem
    if not os.path.exists(savd_img_dirpath):
        os.mkdir(savd_img_dirpath)

    frame_id = -1
    frame_rate = 5  # yuanqudaolu-baitian帧抽取1帧

    while True:
        frame_id += 1

        # Grab a single frame of recongnization
        ret, frame = input_video.read()

        # 3帧抽一帧
        if frame_id % frame_rate != 0:
            continue

        if frame is not None:
            print(f"frame id :{frame_id}")

            # save jpg
            savd_img_filename = savd_img_dirpath + "\{}.jpg".format(frame_id)
            cv2.imwrite(savd_img_filename, frame)

        else:
            break
