# -*- coding: utf-8 -*-
import torch
import torch.nn as nn
import torch.nn.functional as F


class DoubleConv(nn.Module):#pytorch中所有类都继承自module
    """(convolution => [GN] => ReLU) * 2，"""
#   #如何用pytorch构建神经网络框架https://blog.csdn.net/xu380393916/article/details/97280035
    def __init__(self, in_channels, out_channels):#在__init__中定义两次卷积
        super().__init__()#超类/父类初始化
        self.double_conv = nn.Sequential(#序贯模型，依次执行下列结构
            nn.Conv3d(in_channels, out_channels, kernel_size=3, padding=1),#进行3D卷积，卷积核大小为3*3,没有padding
            nn.BatchNorm3d(out_channels),#批标准化，处理后的数据服从N(0,1)的正态分布，可以加快学习率（为什么）
            nn.ReLU(inplace=True),#卷积后面加一个ReLU函数，留下相关特征，去掉不相关特征，卷积之后的正值越大，说明与卷积核相关性越强，负值越大，不相关性越大。
            nn.Conv3d(out_channels, out_channels, kernel_size=3, padding=1),#重复
            nn.BatchNorm3d(out_channels),
            nn.ReLU(inplace=True)
        )

    def forward(self, x):
        #p使用ytorch模型训练时，不需要显式使用forward，只要在实例化一个对象中传入对应的参数就可以自动调用 forward 函数
        #module(data) 等价于 module.forward(data)
        #https://blog.csdn.net/xu380393916/article/details/97280035
        return self.double_conv(x)

class Down(nn.Module):
    """Downscaling with maxpool then double conv"""
    def __init__(self, in_channels, out_channels):
        super().__init__()
        self.maxpool_conv = nn.Sequential(
            nn.MaxPool3d(2),#最大池化，下采样
            DoubleConv(in_channels, out_channels)#这里在池化后又进行了一次卷积，即把U-Net中卷积后下采样合成一步
        )
    def forward(self, x):
        return self.maxpool_conv(x)

class Up(nn.Module):
    """Upscaling then double conv"""
    def __init__(self, in_channels, out_channels, trilinear=True):
        super().__init__()

        # if bilinear, use the normal convolutions to reduce the number of channels
        #没查到normal convolution
        if trilinear:
            #上采样本质上是把低分辨率图像采样成更高分辨率，具体使用可参见https://www.cnblogs.com/wanghui-garcia/p/11399053.
            self.up = nn.Upsample(scale_factor=2, mode='trilinear', align_corners=True)
        else:
            #逆卷积，可以看作卷积的反向操作，与上采样不同
            self.up = nn.ConvTranspose3d(in_channels // 2, in_channels // 2, kernel_size=2, stride=2)
        self.conv = DoubleConv(in_channels, out_channels)
    def forward(self, x1, x2):
        x1 = self.up(x1)#x1经过一次上采样
        # input is CHW
        diffZ = x2.size()[2] - x1.size()[2]
        diffY = x2.size()[3] - x1.size()[3]
        diffX = x2.size()[4] - x1.size()[4]
        #F是torch.nn.functional,
        x1 = F.pad(x1, [diffX // 2, diffX - diffX // 2,
                        diffY // 2, diffY - diffY // 2,
                        diffZ // 2, diffZ - diffZ // 2])
        #将x1的维数填补（pad）成与x2相同
        x = torch.cat([x2, x1], dim=1)#将x1和x2拼接在一起
        return self.conv(x)

class OutConv(nn.Module):
    def __init__(self, in_channels, out_channels):
        super(OutConv, self).__init__()
        #再次卷积（1×1）后输出
        self.conv = nn.Conv3d(in_channels, out_channels, kernel_size=1)

    def forward(self, x):
        return self.conv(x)

class UNet_base(nn.Module):
    def __init__(self, n_channels, trilinear=True, chs=(16, 32, 64, 128, 256, 128, 64, 32, 16)):
        #n_channels是图像一开始的信道数，最后是在Demo_unet_4c中被赋值
        super(UNet_base, self).__init__()
        self.n_channels = n_channels
        self.trilinear = trilinear

        self.inc = DoubleConv(n_channels, chs[0])
        self.down1 = Down(chs[0], chs[1])
        self.down2 = Down(chs[1], chs[2])
        self.down3 = Down(chs[2], chs[3])
        self.down4 = Down(chs[3], chs[4])
        self.up1 = Up(chs[4] + chs[3], chs[5], trilinear)
        self.up2 = Up(chs[5] + chs[2], chs[6], trilinear)
        self.up3 = Up(chs[6] + chs[1], chs[7], trilinear)
        self.up4 = Up(chs[7] + chs[0], chs[8], trilinear)

    def forward(self, x):
        x1 = self.inc(x)
        x2 = self.down1(x1)
        x3 = self.down2(x2)
        x4 = self.down3(x3)
        x5 = self.down4(x4)
        x = self.up1(x5, x4)
        x = self.up2(x, x3)
        x = self.up3(x, x2)
        x = self.up4(x, x1)
        return x

class UNet(nn.Module):
    def __init__(self, n_channels, n_classes, depth=(16, 32, 64, 128, 256, 128, 64, 32, 16)):
        super(UNet, self).__init__()
        self.unet = UNet_base(n_channels=n_channels, chs=depth)#n_channels是图像一开始的信道数，最后是在Demo_unet_4c中被赋值
        self.out_conv = nn.Conv3d(depth[-1], n_classes, 1)#将输出单独作一个类,但好像没有用到前面定义的OutConv
        #n——classes
        self.softmax = nn.Softmax(dim=1)#把一些输入映射为0-1之间的实数，并且归一化保证和为1
    def forward(self, x):
        Z = x.size()[2]#x是五维量
        Y = x.size()[3]
        X = x.size()[4]
        diffZ = (32 - x.size()[2] % 32) % 32
        diffY = (32 - x.size()[3] % 32) % 32
        diffX = (32 - x.size()[4] % 32) % 32
        #计算距率32的整数倍还差多少

        x = F.pad(x, [diffX // 2, diffX - diffX // 2,
                      diffY // 2, diffY - diffY // 2,
                      diffZ // 2, diffZ - diffZ // 2])
        #把x填充到32的倍数
        x = self.unet(x)
        x = self.out_conv(x)
        x = self.softmax(x)
        return x[:, :, diffZ//2: Z+diffZ//2, diffY//2: Y+diffY//2, diffX // 2:X + diffX // 2]
        #按填充后的维度进行输出