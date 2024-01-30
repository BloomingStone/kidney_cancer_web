# -*- coding: utf-8 -*-
import os
from os.path import join
from time import time
import numpy as np
import torch
from _3DUNetKidney.models.UNet import UNet


def predict(img_path, save_path, model_name="UNet_4c", num_classes=5):
    """

    @param img_path: 输入图片的相对路径(包括文件名)
    @param save_path: 分割结果的相对路径(包括文件名)
    @param model_name: 所用模型的名称
    @param num_classes: 通道数
    @return:
    """

    k = '200_'  # 选择权重后缀
    checkpoint_dir = '_3DUNetKidney/weights'    # 存放权重的目录

    net_S = UNet(n_channels=1, n_classes=5)  # 实例化网络

    net_S.load_state_dict(torch.load('{0}/{1}_epoch_{2}.pth'.format(checkpoint_dir, model_name, k), map_location=torch.device('cpu')))   # 加载参数

    print("Predict test_once data")
    net_S.eval()    # 验证集和测试集都在eval下运行
    image = np.fromfile(img_path, dtype=np.uint16)
    n_pieces = int(image.shape[0] / (150 * 150))
    image = image.reshape(1, 1, n_pieces, 150, 150)

    # 注释后匹配的是没有预处理的参数
    image = np.where(image < 0., 0., image)
    image = np.where(image > 2048., 2048., image)
    image = image.astype(np.float32)
    image = image / 2048.

    image = torch.from_numpy(image)
    predict_result = np.zeros((1, num_classes, n_pieces, 150, 150), dtype=np.float32)

    with torch.no_grad():
        a = time()
    predict_result += net_S(image).data.numpy()
    b = time()
    print(b - a)

    predict_result = np.argmax(predict_result[0], axis=0)
    predict_result = predict_result.astype(np.uint16)
    predict_result.tofile(save_path)


def is_image3d_file(filename):
    return any(filename.endswith(extension) for extension in [".raw"])
