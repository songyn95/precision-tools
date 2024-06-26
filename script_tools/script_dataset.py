# coding=utf-8
"""
@project:   blueberry
@File:  script_dataset.py
@IDE:   
@author:    song yanan 
@Date:  2024/3/13 12:54

"""
from pathlib import Path
import pandas as pd
from matplotlib import pyplot as plt
import matplotlib
from xml.etree import ElementTree as ET
import glob
import os

FILE = Path(__file__).resolve()
ROOT = FILE.parents[0]  # root directory


def plot_evolve(evolve_csv=ROOT / "result.csv"):
    evolve_csv = Path(evolve_csv)
    data = pd.read_csv(evolve_csv)
    keys = [x.strip() for x in data.columns]
    x = data.values[:, ]
    plt.figure(figsize=(10, 12), tight_layout=True)
    matplotlib.rc("font", **{"size": 8})

    plt.plot(x[:, -2], x[:, -1])
    plt.title(f"iou:(0-1) PR curves")
    f = evolve_csv.with_suffix(".png")  # filename
    plt.savefig(f, dpi=200)
    plt.close()
    print(f"Saved {f}")


def plot(evolve_csv="result.csv"):
    evolve_csv = Path(evolve_csv)
    df_data = pd.read_csv(evolve_csv, header=None)
    data = df_data.sort_values(by=1)
    x = data.values[:, ]
    fig = plt.figure(figsize=(10, 12), tight_layout=True)
    matplotlib.rc("font", **{"size": 8})

    ax1 = fig.add_subplot(2, 1, 1)
    ax1.plot(x[:, -2], x[:, -1])
    ax1.set_xlabel('precision')
    ax1.set_ylabel('recall')
    ax1.set_title('PR curve')
    ax1.set_xlim(0.0, 1.0)
    ax1.set_ylim(0.0, 1.0)

    ax1 = fig.add_subplot(2, 1, 2)
    ax1.plot(x[:, -3][::-1], x[:, -1][::-1])
    ax1.set_xlabel('FPR')
    ax1.set_ylabel('TPR')
    ax1.set_title('ROC curve')
    ax1.set_xlim(0.0, 1.0)
    ax1.set_ylim(0.0, 1.0)
    # plt.plot(x[:, -2], x[:, -1])
    # plt.title(f"iou:(0-1) PR curves")
    f = evolve_csv.with_suffix(".png")  # filename
    fig.savefig(f, dpi=600)
    print(f"Saved {f}")


class Dataset:
    def __init__(self, path, batch_size=1):
        self.path = path

        ## xml文件
        try:
            f = []  # xml files
            for p in path if isinstance(path, list) else [path]:
                p = Path(p)  # os-agnostic
                if p.is_dir():  # dir
                    f += glob.glob(str(p / "**" / "*.xml"), recursive=True)
                elif p.is_file() and p.name.endswith('.xml'):  # file
                    f += p  #
                else:
                    raise FileNotFoundError(f"{p} does not exist")

            self.im_files = sorted(f)
            assert self.im_files, f"No xml file found"

        except Exception as e:
            raise Exception(f"Error loading data from {path}:") from e

    def convert_image_xml_txt(self):
        # 逐个获取xml文件
        for eachfile in self.im_files:
            anno = ET.parse(eachfile)
            filename = anno.find('path').text.strip().split(os.sep)[-1]  ## filename 000001.jpg
            # 获取图像标签大小
            img_sz = [0, 0]  # width height
            for img_info in anno.findall('size'):
                img_sz[0] = int(img_info.find('width').text)
                img_sz[1] = int(img_info.find('height').text)
            print(filename)
            filename += ' '
            for obj in anno.findall('object'):
                if int(obj.find('difficult').text) == 1:  # 0表示易识别，1表示难识别
                    continue

                difficult = int(obj.find('difficult').text)
                bndbox_anno = obj.find('bndbox')
                bbox = ' '.join([bndbox_anno.find(tag).text for tag in ('xmin', 'ymin', 'xmax', 'ymax')])
                conf = round(float(bbox.split()[-1]) / img_sz[1], 2)
                labelname = obj.find('name').text.strip()
                filename += ' '.join([labelname, bbox, str(conf)])
                filename += ' '
            # print(str_line)
            f.write(filename + '\n')

    def convert_video_xml_txt(self):
        # 逐个获取xml文件
        for eachfile in self.im_files:
            eachfile = open(eachfile, encoding='GB2312')
            anno = ET.parse(eachfile).getroot()
            filename = anno.find('path').text.strip().split(os.sep)[-1]  ## filename 000001.jpg
            # 获取图像标签大小
            img_sz = [0, 0]  # width height
            for img_info in anno.findall('size'):
                img_sz[0] = int(img_info.find('width').text)
                img_sz[1] = int(img_info.find('height').text)
            frameid = anno.find('framenumber').text
            filename = ' '.join([filename, frameid])
            filename += ' '
            for obj in anno.findall('object'):
                obj_id = [obj.find('id').text]
                bndbox_anno = obj.find('bndbox')
                bbox = [int(bndbox_anno.find(tag).text) for tag in ('xmin', 'ymin', 'width', 'height')]

                bbox[-2] += bbox[0]
                bbox[-1] += bbox[1]
                bbox = [str(i) for i in bbox]
                obj_box = ' '.join(obj_id + bbox)
                conf = round(float(bbox[-1]) / img_sz[1], 2)
                labelname = obj.find('name').text.strip()
                filename += ' '.join([labelname, obj_box, str(conf)])
                filename += ' '
            # print(str_line)
            f.write(filename.strip() + '\n')

    def __len__(self):
        return len(self.im_files)


if __name__ == '__main__':
    plot('../result/result.csv')
    # dataset = Dataset(ROOT / "test_data" / 'detect' / "video" / "gt")
    # with open(ROOT / "test_data" / 'detect' / "video" / 'pred.txt', 'w', encoding='utf-8') as f:
    #     dataset.convert_image_xml_txt()
    # dataset.convert_video_xml_txt()
