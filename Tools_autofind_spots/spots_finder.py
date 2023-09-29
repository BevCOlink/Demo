#!/usr/bin/env python3
# -*- coding: utf-8 -*-
'''
@author: zhou jiyang
@contact: zjy777@mail.ustc.edu.cn
@file: spots_finder.py
@time: 2022/4/19/0019 17:28:19
@desc:
'''
import pandas as pd
import numpy as np
import os
import matplotlib.pyplot as plt
from skimage import measure
import cv2

class Spots_Finder():
    def __init__(self):
        # 找点相关参数
        self.x_tick_0 = 0  # scan image's ticks
        self.y_tick_0 = 0
        self.x_tick = 0
        self.y_tick = 0
        self.scan_data = 0
        self.scan_inf = 0
        self.real_position_xy = 0  # real position of the zero point
        self.real_position_z = 0
        self.vmax = 3  # max colorbar value is vmax_rate * the median of the image
        self.thresh_rate = 4
        # # 数据读取和保存
        # self.data_path = ''
        # self.data_name = ''  # save name of final labeled figure

    def _BubbleSort(self, arr1, arr2, reverse=False):
        arr2 = np.array(arr2)
        for i in np.arange(0, np.size(arr1), 1):
            for j in np.arange(0, np.size(arr1) - i - 1, 1):
                if reverse:  # 从大到小排序
                    if arr1[j] < arr1[j + 1]:
                        temp = arr1[j]
                        arr1[j] = arr1[j + 1]
                        arr1[j + 1] = temp

                        temp = arr2[j]
                        arr2[j] = arr2[j + 1]
                        arr2[j + 1] = temp
                else:  # 从小到大排序
                    if arr1[j] > arr1[j + 1]:
                        temp = arr1[j]
                        arr1[j] = arr1[j + 1]
                        arr1[j + 1] = temp

                        temp = arr2[j]
                        arr2[j] = arr2[j + 1]
                        arr2[j + 1] = temp

        return arr2

    def _sort_contours(self, cnts, bubble = False, method="left-to-right"):
        reverse = False
        i = 0
        if method == "right-to-left" or method == "bottom-to-top":
            reverse = True
        if method == "top-to-bottom" or method == "bottom-to-top":
            i = 1
        boundingBoxes = [cv2.boundingRect(c) for c in cnts]
        (cnts, boundingBoxes) = zip(*sorted(zip(cnts, boundingBoxes), key=lambda b: b[1][i], reverse=reverse))
        if bubble:
            position_means = []
            for c in cnts:
                position_means.append(c.mean(axis=0)[0])
            position_means = np.array(position_means)
            cnts = self._BubbleSort(position_means[0:int((np.shape(position_means)[0]) / 2), 1], cnts, reverse=True)
            cnts = self._BubbleSort(position_means[int((np.shape(position_means)[0]) / 2):, 0], cnts)
        return cnts, boundingBoxes

    def _band_pass_filter(self,low_band,high_band):
        '''
        low_band & high_band: binary image data (n * m matrix)
        doing '^' bool operation for every corresponding elements in data
        '''
        filted_data = np.zeros(np.shape(low_band))
        for i, l in enumerate(low_band):
            for j,e in enumerate(l):
                filted_data[i,j] = low_band[i,j] ^ high_band[i,j]

        return filted_data


    def Median_2D(self,matrix):
        matrix = [j for i in matrix for j in i]
        matrix = np.sort(matrix)
        matrix = matrix[int(len(matrix)/2)]
        return matrix

    def SaveScan(self, data,position, range, step,scan_axis,int_time, path, name):

        header1 = 'XYZ Center: %.4f %.4f %.4f\n' % (
            position[0], position[1], position[2])
        header2 = 'XYZ Step: %.2f %.2f %.2f\n' % (
            step[0], step[1], step[2])
        header3 = 'XYZ Range: %.2f %.2f %.2f\n' % (
            range[0], range[1], range[2])
        header4 = 'Count Time: %d ms\n' % int_time
        header5 = 'scan axis: %d\n' % scan_axis
        header_all = header1 + header2 + header3 + header4 + header5
        header_all = header_all.encode('utf-8').decode(
            'latin1')  # 将编码方式改写，否则报错（https://blog.csdn.net/u014744494/article/details/41986647）
        np.savetxt(path + name, data, fmt='%.2f', newline='\n', header=header_all)
        print('scan saved')


    def LoadScan(self,data_path):

        f = open(data_path, 'r', encoding='UTF-8')

        with f:
            # 接受读取的内容，并显示到多行文本框中
            data = f.readlines()
            lists_inf = []
            list_scan = []
            for string in data[:3]:
                string = string.strip()  # 去除换行等符号
                string = string.split(' ')  # 以空格作为分隔符
                string = string[3:]
                string = list(map(float, string))  # 将字符串转换为浮点数，注意需要使用list转换掉map格式
                lists_inf.append(string)
            self.scan_inf = np.array(lists_inf)

            for string in data[4:5]:
                string = string.strip()  # 去除换行等符号
                string = string.split(' ')  # 以空格作为分隔符
                string = int(string[3])  # 第三个信息是扫描轴的信息
            self.scan_axis_sign = string

            for string in data[6:]:  # 第6行开始为数据
                string = string.strip()  # 去除换行等符号
                string = string.split(' ')  # 以空格作为分隔符
                string = list(map(float, string))  # 将字符串转换为浮点数，注意需要使用list转换掉map格式
                list_scan.append(string)
            # self.scan_data = np.delete(self.scan_data, [-3,-2,-1], axis=1)
            self.scan_data = np.transpose(np.array(list_scan))
            self.scan_data = np.delete(self.scan_data,[0,1,2],axis=0)



            if self.scan_axis_sign == 1:
                self.x_tick_0 = np.linspace(0, np.shape(self.scan_data)[1], 5)
                self.y_tick_0 = np.linspace(0, np.shape(self.scan_data)[0], 5)
                self.x_tick = np.round(np.linspace(self.scan_inf[0, 0] - self.scan_inf[2, 0],
                                                   self.scan_inf[0, 0] + self.scan_inf[2, 0], 5), 4)
                self.y_tick = np.round(np.linspace(self.scan_inf[0, 1] - self.scan_inf[2, 1],
                                                   self.scan_inf[0, 1] + self.scan_inf[2, 1], 5), 4)
                # self.x_tick = self.x_tick.astype(int)
                # self.y_tick = self.y_tick.astype(int)
                self.real_position_xy = np.array([self.scan_inf[0,0] - self.scan_inf[2,0], self.scan_inf[0,1] - self.scan_inf[2,1]])


            elif self.scan_axis_sign == 2 or self.scan_axis_sign == 3:
                self.x_tick_0 = np.linspace(0, np.shape(self.scan_data)[1], 5)
                self.y_tick_0 = np.linspace(0, np.shape(self.scan_data)[0], 5)
                self.x_tick = np.linspace(self.scan_inf[0, 0] - self.scan_inf[2, 0],
                                          self.scan_inf[0, 0] + self.scan_inf[2, 0], 5)
                self.y_tick = np.linspace(self.scan_inf[0, 2] - self.scan_inf[2, 2],
                                          self.scan_inf[0, 2] + self.scan_inf[2, 2], 5)
                # self.x_tick = self.x_tick.astype(int)
                # self.y_tick = self.y_tick.astype(int)
                self.real_position_z = np.array([self.scan_inf[0,2] - self.scan_inf[2,2]])


    def label_bright_spots(self,data_path,data_name,vmax=18,gray_thresh=115, numP_min=100, numP_max=600, plot =False):
        """
        thresh_rate: param used to binary image, the thresh is thresh_rate * average of the image
        numP_min & numP_max: used to restrict the pixel numbers when analyse connected component
        plot: whether to plot the image when processing
        retrun: cnts & positions: the contours and pixel positions([x,y]) of every labeled spots
        """

        fig, ax = plt.subplots()

        ax.imshow(self.scan_data, cmap='gray', vmin=np.min(self.scan_data[np.nonzero(np.array(self.scan_data))]), vmax=vmax, origin='lower')
        # print(self.scan_data)
        print('v_min:',np.min(self.scan_data[np.nonzero(np.array(self.scan_data))]))
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)

        self.x_tick_0 = self.x_tick_0[:4]
        self.x_tick = self.x_tick[:4]
        self.y_tick_0 = self.y_tick_0[:4]
        self.y_tick = self.y_tick[:4]

        plt.xticks(self.x_tick_0, self.x_tick)
        plt.yticks(self.y_tick_0, self.y_tick)
        plt.savefig(data_path+data_name+'-xy.jpg', dpi=150)

        self.x_tick_0 = self.x_tick_0[:2]
        self.x_tick = self.x_tick[:2]
        self.y_tick_0 = self.y_tick_0[:2]
        self.y_tick = self.y_tick[:2]
        plt.xticks(self.x_tick_0, self.x_tick)
        plt.yticks(self.y_tick_0, self.y_tick)
        plt.savefig(data_path + data_name + '-xy_black.jpg', facecolor='k', dpi=150)
        if plot:
            fig.show()
        else:
            plt.close()

        image_black = cv2.imread(data_path+data_name+'-xy_black.jpg', cv2.IMREAD_UNCHANGED)
        image_white = cv2.imread(data_path+data_name+'-xy.jpg', cv2.IMREAD_UNCHANGED)
        gray = cv2.cvtColor(image_black, cv2.COLOR_BGR2GRAY)
        blurred = cv2.GaussianBlur(gray, (11, 11), 0)
        if plot:
            cv2.imshow('Gray Image', blurred)
            cv2.waitKey(0)


        # threshold the image to reveal light regions in the blurred image
        thresh = cv2.threshold(blurred, gray_thresh, 255, cv2.THRESH_BINARY)[1]
        if plot:
            cv2.imshow('thresh', thresh)
            cv2.waitKey(0)
        # perform a series of erosions and dilations to remove any small blobs of noise from the thresholded image
        thresh = cv2.erode(thresh, None, iterations=2)
        thresh = cv2.dilate(thresh, None, iterations=3)
        if plot:
            cv2.imshow('Er and Di Image', thresh)
            cv2.waitKey(0)

        # perform a connected component analysis on the thresholded
        # image, then initialize a mask to store only the "large" components
        labels = measure.label(thresh, neighbors=8, background=0)

        mask = np.zeros(thresh.shape, dtype="uint8")
        # loop over the unique components
        for label in np.unique(labels):
            # if this is the background label, ignore it
            if label == 0:
                continue
            # otherwise, construct the label mask and count the number of pixels
            labelMask = np.zeros(thresh.shape, dtype="uint8")
            labelMask[labels == label] = 255
            numPixels = cv2.countNonZero(labelMask)
            print('轮廓大小:', numPixels)
            # if the number of pixels in the component is sufficiently
            # large, then add it to our mask of "large blobs"
            if numPixels > numP_min and numPixels < numP_max:
                mask = cv2.add(mask, labelMask)

        if plot:
            cv2.imshow('Masked Image', mask)
            cv2.waitKey(0)

        #find contours of bright spots
        contour, hierarchy = cv2.findContours(mask.copy(), cv2.RETR_EXTERNAL,
                                              cv2.CHAIN_APPROX_SIMPLE)
        positions = []
        if len(contour) == 0:
            print('no points found or passed thresh')
            return [],[]
        else:
            cnts = self._sort_contours(contour, method='top-to-bottom')[0]

            for (i, c) in enumerate(cnts):  # index,counts
                # draw the bright spot on the image
                (x, y, w, h) = cv2.boundingRect(c)
                ((cX, cY), radius) = cv2.minEnclosingCircle(c)
                cv2.circle(image_white, (int(cX), int(cY)), int(radius),
                           (0, 0, 255), 1)
                cv2.putText(image_white, "#{}".format(i + 1), (x, y - 15),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 1)

                positions.append(c.mean(axis=0)[0])

            positions = np.array(positions)

            if plot:
                cv2.imshow('Labeled Image', image_white)
                cv2.waitKey(0)

            cv2.imwrite(data_path+data_name+'-xy_labeled.jpg', image_white)
            os.remove(data_path+data_name+'-xy_black.jpg')
            # os.remove(data_path + data_name + '-xy.jpg')

            return cnts, positions

    def label_focused_position(self,data_path,data_name,vmax=14,gray_thresh=175, numP=5000, plot =False):
        """
        thresh_rate: param used to binary image, the thresh is thresh_rate * average of the image
        numP: used to restrict the pixel numbers when analyse connected component
        plot: whether to plot the image when processing
        retrun: cnts & positions: the contours and z pixel min&max positions([z_min,z_max]) of every labeled spots
        """

        fig, ax = plt.subplots()

        ax.imshow(self.scan_data, cmap='gray', vmin=0, vmax=vmax, origin='lower')
        # print(np.max(self.scan_data))
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)

        self.x_tick_0 = self.x_tick_0[:4]
        self.x_tick = self.x_tick[:4]
        self.y_tick_0 = self.y_tick_0[:4]
        self.y_tick = self.y_tick[:4]
        plt.xticks(self.x_tick_0, self.x_tick)
        plt.yticks(self.y_tick_0, self.y_tick)
        plt.savefig(data_path + data_name + '-z.jpg', dpi=150)
        self.x_tick_0 = [self.x_tick_0[0], self.x_tick_0[2]]
        self.x_tick = [self.x_tick[0], self.x_tick[2]]
        self.y_tick_0 = self.y_tick_0[:2]
        self.y_tick = self.y_tick[:2]
        plt.xticks(self.x_tick_0, self.x_tick)
        plt.yticks(self.y_tick_0, self.y_tick)
        plt.savefig(data_path+data_name+'-z_black.jpg', facecolor='k', dpi=150)

        if plot:
            fig.show()
        else:
            plt.close()

        image_black = cv2.imread(data_path+data_name+'-z_black.jpg', cv2.IMREAD_UNCHANGED)
        image_white = cv2.imread(data_path+data_name+'-z.jpg', cv2.IMREAD_UNCHANGED)
        gray = cv2.cvtColor(image_black, cv2.COLOR_BGR2GRAY)
        blurred = cv2.GaussianBlur(gray, (11, 11), 0)
        if plot:
            cv2.imshow('Gray Image', blurred)
            cv2.waitKey(0)

        # threshold the image to reveal light regions in the blurred image
        # thresh_high = cv2.threshold(blurred, thresh_rate_high * np.average(blurred), 255, cv2.THRESH_BINARY)[1]
        # thresh_low = cv2.threshold(blurred, thresh_rate_low * np.average(blurred), 255, cv2.THRESH_BINARY)[1]
        # thresh = self._band_pass_filter(low_band=thresh_low,high_band=thresh_high)
        thresh = cv2.threshold(blurred, gray_thresh, 255, cv2.THRESH_BINARY)[1]

        # perform a series of erosions and dilations to remove any small blobs of noise from the thresholded image
        thresh = cv2.erode(thresh, None, iterations=3)
        thresh = cv2.dilate(thresh, None, iterations=3)
        if plot:
            cv2.imshow('Er and Di Image', thresh)
            cv2.waitKey(0)

        # perform a connected component analysis on the thresholded
        # image, then initialize a mask to store only the "large" components
        labels = measure.label(thresh, neighbors=8, background=0)

        mask = np.zeros(thresh.shape, dtype="uint8")
        # loop over the unique components
        for label in np.unique(labels):
            # if this is the background label, ignore it
            if label == 0:
                continue
            # otherwise, construct the label mask and count the number of pixels
            labelMask = np.zeros(thresh.shape, dtype="uint8")
            labelMask[labels == label] = 255
            numPixels = cv2.countNonZero(labelMask)
            # if the number of pixels in the component is sufficiently
            # large, then add it to our mask of "large blobs"
            if numPixels > numP:
                mask = cv2.add(mask, labelMask)

        if plot:
            cv2.imshow('Masked Image', mask)
            cv2.waitKey(0)

        #find contours of bright spots
        contour, hierarchy = cv2.findContours(mask.copy(), cv2.RETR_EXTERNAL,
                                              cv2.CHAIN_APPROX_SIMPLE)
        if len(contour) == 0:
            return [],[]
        else:
            cnts = self._sort_contours(contour, method='top-to-bottom')[0]
            if len(cnts) != 1:
                print('Warning: contour is not equal 1')
            for (i, c) in enumerate(cnts):  # index,counts
                # draw the bright spot on the image
                (x, y, w, h) = cv2.boundingRect(c)
                positions=[x,y,w,h]
                # ((cX, cY), radius) = cv2.minEnclosingCircle(c)
                cv2.rectangle(image_white, (int(x), int(y)), (int(x + w), int(y + h)), (0, 255, 0), 1)
                cv2.putText(image_white, "#{}".format(i + 1), (x, y - 15),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 1)


            pixel_min_z = positions[1]
            pixel_max_z = positions[1]+positions[3]
            positions = np.array([pixel_min_z,pixel_max_z])

            if plot:
                cv2.imshow('Labeled Image', image_white)
                cv2.waitKey(0)

            cv2.imwrite(data_path+data_name+'-z_labeled.jpg', image_white)
            os.remove(data_path + data_name + '-z_black.jpg')
            # os.remove(data_path + data_name + '-z.jpg')
            return cnts, positions

    def pixel_to_real_position_xy(self,data_path,data_name,plot = False):
        """
        :return: [a,b]: a is the x zero point's pixel position, b is the y zero point's pixel position
                 [c,d]: c is the x axis's pixel to position rate, d is the y axis's rate
        """
        #set axis
        data_0 = np.zeros(np.shape(self.scan_data)) + 1
        #only plot axis
        fig, ax = plt.subplots()
        ax.imshow(data_0, cmap='gray', vmin=0, vmax=1,origin='lower')
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.spines['bottom'].set_visible(False)
        ax.spines['left'].set_visible(False)

        # print(self.scan_axis_sign)
        plt.xticks(self.x_tick_0, self.x_tick)
        plt.yticks(self.y_tick_0, self.y_tick)
        # plt.tick_params(labelsize=15)

        #save figure and re-read figure
        plt.savefig(data_path+data_name+'-xy_axis.jpg', dpi=150)
        if plot:
            fig.show()
        else:
            plt.close()

        image_zero = cv2.imread(data_path+data_name+'-xy_axis.jpg', cv2.IMREAD_UNCHANGED)
        gray = 255 - cv2.cvtColor(image_zero, cv2.COLOR_BGR2GRAY)
        thresh = cv2.threshold(gray, 20, 255, cv2.THRESH_BINARY)[1]
        # thresh = cv2.erode(thresh, None, iterations=1)
        # thresh = cv2.dilate(thresh, None, iterations=3)
        if plot:
            cv2.imshow('Er and Di Image', thresh)
            cv2.waitKey(0)

        # perform a connected component analysis on the thresholded
        # image, then initialize a mask to store only the "large" components
        labels = measure.label(thresh, neighbors=8, background=0)

        #
        mask = np.zeros(thresh.shape, dtype="uint8")
        # loop over the unique components
        for label in np.unique(labels):
            # if this is the background label, ignore it
            if label == 0:
                continue
            # otherwise, construct the label mask and count the number of pixels
            labelMask = np.zeros(thresh.shape, dtype="uint8")
            labelMask[labels == label] = 255
            numPixels = cv2.countNonZero(labelMask)
            # if the number of pixels in the component is sufficiently
            # large, then add it to our mask of "large blobs"
            if numPixels>10 and numPixels < 20:
                mask = cv2.add(mask, labelMask)

        if plot:
            cv2.imshow('Masked Image', mask)
            cv2.waitKey(0)
        contour, hierarchy = cv2.findContours(mask.copy(), cv2.RETR_EXTERNAL,
                                              cv2.CHAIN_APPROX_SIMPLE)

        cnts = self._sort_contours(contour, bubble=True, method='left-to-right')[0]
        print('xy axis contours:',len(cnts))
        pixel = []
        for (i, c) in enumerate(cnts):
            (x, y, w, h) = cv2.boundingRect(c)
            pixel.append([x, y, w, h])
            cv2.rectangle(image_zero, (int(x), int(y)), (int(x + w), int(y + h)), (0, 255, 0), 1)
            cv2.putText(image_zero, "#{}".format(i + 1), (x, y - 15), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 1)

        if plot:
            cv2.imshow('Labeled Image', image_zero)
            cv2.waitKey(0)

        pixel_0_x = round(pixel[len(self.x_tick)][0] + pixel[len(self.x_tick)][2] / 2)
        pixel_0_y = round(pixel[0][1] + pixel[0][3] / 2)
        pixel_to_position_x = (self.x_tick[1] - self.x_tick[0]) / (
                round(pixel[len(self.x_tick) + 1][0] + pixel[len(self.x_tick) + 1][2] / 2) - round(
            pixel[len(self.x_tick)][0] + pixel[len(self.x_tick)][2] / 2))
        pixel_to_position_y = (self.y_tick[1] - self.y_tick[0]) / (
                round(pixel[0][1] + pixel[0][3] / 2) - round(pixel[1][1] + pixel[1][3] / 2))

        pixel=np.array([pixel_0_x, pixel_0_y])
        pixel_to_position = np.array([pixel_to_position_x, -pixel_to_position_y])

        os.remove(data_path + data_name + '-xy_axis.jpg')
        cv2.imwrite(data_path + data_name + '-xy_axis.jpg', image_zero)

        return pixel, pixel_to_position

    def pixel_to_real_position_z(self,data_path,data_name,plot = False):
        """
        :return: pixel_z_min & pixel_to_position_z:
        """
        #set axis
        data_0 = np.zeros(np.shape(self.scan_data)) + 1
        #only plot axis
        fig, ax = plt.subplots()
        ax.imshow(data_0, cmap='gray', vmin=0, vmax=1,origin='lower')
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.spines['bottom'].set_visible(False)
        ax.spines['left'].set_visible(False)

        # print(self.scan_axis_sign)
        plt.xticks(self.x_tick_0, self.x_tick)
        plt.yticks(self.y_tick_0, self.y_tick)
        # plt.tick_params(labelsize=15)
        #save figure and re-read figure
        plt.savefig(data_path+data_name+'-z_axis.jpg', dpi=150)
        if plot:
            fig.show()
        else:
            plt.close()

        image_zero = cv2.imread(data_path+data_name+'-z_axis.jpg', cv2.IMREAD_UNCHANGED)
        gray = 255 - cv2.cvtColor(image_zero, cv2.COLOR_BGR2GRAY)
        thresh = cv2.threshold(gray, 1 * np.average(gray), 255, cv2.THRESH_BINARY)[1]
        thresh = cv2.erode(thresh, None, iterations=1)
        thresh = cv2.dilate(thresh, None, iterations=3)
        if plot:
            cv2.imshow('Er and Di Image', thresh)
            cv2.waitKey(0)

        # perform a connected component analysis on the thresholded
        # image, then initialize a mask to store only the "large" components
        labels = measure.label(thresh, neighbors=8, background=0)

        #
        mask = np.zeros(thresh.shape, dtype="uint8")
        # loop over the unique components
        for label in np.unique(labels):
            # if this is the background label, ignore it
            if label == 0:
                continue
            # otherwise, construct the label mask and count the number of pixels
            labelMask = np.zeros(thresh.shape, dtype="uint8")
            labelMask[labels == label] = 255
            numPixels = cv2.countNonZero(labelMask)
            # if the number of pixels in the component is sufficiently
            # large, then add it to our mask of "large blobs"
            if numPixels > 200:
                mask = cv2.add(mask, labelMask)

        if plot:
            cv2.imshow('Masked Image', mask)
            cv2.waitKey(0)
        contour, hierarchy = cv2.findContours(mask.copy(), cv2.RETR_EXTERNAL,
                                              cv2.CHAIN_APPROX_SIMPLE)

        cnts = self._sort_contours(contour, bubble=True, method='left-to-right')[0]
        if len(cnts) != 4:
            print('contour error! len(cnts) != 4')
        pixel = []
        for (i, c) in enumerate(cnts):
            (x, y, w, h) = cv2.boundingRect(c)
            pixel.append([x, y, w, h])
            cv2.rectangle(image_zero, (int(x), int(y)), (int(x + w), int(y + h)), (0, 255, 0), 1)
            cv2.putText(image_zero, "#{}".format(i + 1), (x, y - 15), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 1)

        if plot:
            cv2.imshow('Labeled Image', image_zero)
            cv2.waitKey(0)

        pixel_z_min = round(pixel[0][1] + pixel[0][3] / 2)
        pixel_z_max = round(pixel[1][1] + pixel[1][3] / 2)
        pixel_to_position_z = -(self.y_tick[1] - self.y_tick[0]) / (pixel_z_max - pixel_z_min)  #pixel方向与position方向相反

        os.remove(data_path + data_name + '-z_axis.jpg')
        cv2.imwrite(data_path + data_name + '-z_axis.jpg', image_zero)

        return pixel_z_min, pixel_to_position_z

    def label_real_position_xy(self,data_path,data_name,vmax=18,gray_thresh=115, numP_min=100, numP_max=500):
        """
        :return: real position of points
        """
        cnts, pixel_position= self.label_bright_spots(data_path=data_path,data_name=data_name,vmax=vmax,gray_thresh=gray_thresh, numP_min=numP_min, numP_max=numP_max)
        if cnts == []:
            return []
        else:
            pixel_0, pixel_to_position = self.pixel_to_real_position_xy(data_path=data_path,data_name=data_name)
            real_position = (pixel_position - pixel_0) * pixel_to_position + self.real_position_xy
            real_position = np.round(real_position,4)
            image = cv2.imread(data_path+data_name + '-xy.jpg', cv2.IMREAD_UNCHANGED)
            for (i, c) in enumerate(cnts):  # index,counts
                # draw the bright spot on the image
                (x, y, w, h) = cv2.boundingRect(c)
                ((cX, cY), radius) = cv2.minEnclosingCircle(c)
                cv2.circle(image, (int(cX), int(cY)), int(radius),
                           (0, 0, 255), 1)
                cv2.putText(image, "#{}".format(i + 1)+str(np.round(real_position[i],2)), (x-15, y - 15),
                            cv2.FONT_HERSHEY_TRIPLEX, 0.5, (0, 0, 255), 1)

            cv2.imwrite(data_path+data_name+'-xy-real_position.jpg', image)

            return real_position

    def label_real_position_z(self,data_path,data_name,vmax=14,gray_thresh=175, numP=5000):
        """
        :return: real position of focus point ([z_max,z_min])
        """
        cnts, pixel_position= self.label_focused_position(data_path=data_path,data_name=data_name,vmax=vmax,gray_thresh=gray_thresh, numP=numP)
        if cnts == []:
            print('z focus not found')
            return []
        else:
            pixel_0, pixel_to_position = self.pixel_to_real_position_z(data_path=data_path,data_name=data_name)
            real_position = (pixel_0 - pixel_position) * pixel_to_position + self.real_position_z
            real_position = np.round(real_position,4)
            image = cv2.imread(data_path+data_name + '-z.jpg', cv2.IMREAD_UNCHANGED)
            for (i, c) in enumerate(cnts):  # index,counts
                # draw the bright spot on the image
                (x, y, w, h) = cv2.boundingRect(c)
                ((cX, cY), radius) = cv2.minEnclosingCircle(c)
                cv2.rectangle(image, (int(x), int(y)), (int(x + w), int(y + h)),
                           (0, 0, 255), 1)
                cv2.putText(image, str(real_position[0]), (x-15, y - 15),
                            cv2.FONT_HERSHEY_TRIPLEX, 0.5, (0, 0, 255), 1)
                cv2.putText(image, str(real_position[1]), (x - 15, y - 15 + h),
                            cv2.FONT_HERSHEY_TRIPLEX, 0.5, (0, 0, 255), 1)

            cv2.imwrite(data_path+data_name+'-z-real_position.jpg', image)

            return real_position





if __name__ == '__main__':

    data_path = 'F:/xy.txt'
    save_path = 'F:/'
    save_name = 'point_array'

    finder = Spots_Finder()

    finder.data_path = data_path
    finder.data_name = save_name
    finder.LoadScan(data_path)
    # print(finder.scan_inf)
    # print(np.sort(finder.scan_data))
    # finder.vmax_rate = 10
    # finder.label_bright_spots(save_path,save_name,gray_thresh=170,vmax=800,plot=True)
    finder.pixel_to_real_position_xy(save_path,save_name,plot=True)
    # finder.label_real_position_xy(save_path,save_name,gray_thresh=170,vmax=1000)

    # finder.label_focused_position(save_path, save_name,plot=True)
    # finder.label_real_position_z(save_path,save_name,vmax=10)
