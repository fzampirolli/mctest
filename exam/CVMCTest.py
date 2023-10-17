'''
=====================================================================
Copyright (C) 2018-2023 Francisco de Assis Zampirolli
from Federal University of ABC and individual contributors.
All rights reserved.

This file is part of MCTest 5.2.

Languages: Python 3.8.5, Django 2.2.4 and many libraries described at
github.com/fzampirolli/mctest

You should cite some references included in vision.ufabc.edu.br
in any publication about it.

MCTest is free software: you can redistribute it and/or modify
it under the terms of the GNU Affero General Public License
(gnu.org/licenses/agpl-3.0.txt) as published by the Free Software
Foundation, either version 3 of the License, or (at your option) 
any later version.

MCTest is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
GNU General Public License for more details.

=====================================================================
'''
# coding=UTF-8
# -*- coding: UTF-8 -*-

import binascii
import csv
import itertools as it
import math
import os
import smtplib
import subprocess
import zlib
from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart  # sudo pip install email
from email.mime.text import MIMEText

import PyPDF2  # pip install PyPDF2
import bcrypt
import cv2  # pip install opencv-python
import numpy as np
from django.http import HttpResponse, Http404
from django.utils.translation import gettext_lazy as _
from pyzbar.pyzbar import decode
from skimage.measure import label
from skimage.measure import regionprops  # pip install scikit-image

from exam.UtilsLatex import Utils
from exam.models import Exam, StudentExam, StudentExamQuestion
from mctest.settings import BASE_DIR
from mctest.settings import webMCTest_FROM
from mctest.settings import webMCTest_PASS
from mctest.settings import webMCTest_SERVER
from student.models import Student
from topic.models import Question

circle_min = 650
circle_max = 940  # 895


class cvMCTest(object):
    try:
        CV_CUR_LOAD_IM_GRAY = cv2.CV_LOAD_IMAGE_GRAYSCALE
    except AttributeError:
        CV_CUR_LOAD_IM_GRAY = cv2.IMREAD_GRAYSCALE

    imgAnswers = None
    imgAnswersSegment = None
    centroidsMarked = []

    ################ para manipular PDF #################
    @staticmethod
    def getQRCode(img, countPage):
        DEBUG = False

        myFlagArea = True
        qr = []
        try:  # try find Answer Area
            cvMCTest.imgAnswers = img = cvMCTest.getAnswerArea(img, countPage)
            if DEBUG: cv2.imwrite("_getQRCode" + "_p" + str(countPage + 1).zfill(3) + "_01answerArea.png", img)
        except:
            myFlagArea = False
            pass

        try:
            imgQR = cvMCTest.segmentQRcode(img, countPage)
            if DEBUG: cv2.imwrite("_getQRCode" + "_p" + str(countPage + 1).zfill(3) + "_02qrcode.png", imgQR)
            qr = cvMCTest.decodeQRcode(imgQR)

        except:
            pass
        return myFlagArea, qr

    ################ para manipular PDF #################
    @staticmethod
    def tiff_header_for_ccitt(width, height, img_size, ccitt_group=4):
        tiff_header_struct = '<' + '2s' + 'h' + 'l' + 'h' + 'hhll' * 8 + 'h'
        return struct.pack(tiff_header_struct,
                           b'II',  # Byte order indication: Little indian
                           42,  # Version number (always 42)
                           8,  # Offset to first IFD
                           8,  # Number of tags in IFD
                           256, 4, 1, width,  # ImageWidth, LONG, 1, width
                           257, 4, 1, height,  # ImageLength, LONG, 1, lenght
                           258, 3, 1, 1,  # BitsPerSample, SHORT, 1, 1
                           259, 3, 1, ccitt_group,  # Compression, SHORT, 1, 4 = CCITT Group 4 fax encoding
                           262, 3, 1, 0,  # Threshholding, SHORT, 1, 0 = WhiteIsZero
                           273, 4, 1, struct.calcsize(tiff_header_struct),  # StripOffsets, LONG, 1, len of header
                           278, 4, 1, height,  # RowsPerStrip, LONG, 1, lenght
                           279, 4, 1, img_size,  # StripByteCounts, LONG, 1, size of image
                           0  # last IFD
                           )

    @staticmethod
    def handle_ccitt_fax_decode_img(obj):
        if obj['/DecodeParms']['/K'] == -1:
            ccitt_group = 4
        else:
            ccitt_group = 3
        width = obj['/Width']
        height = obj['/Height']
        data = obj._data  # sorry, getData() does not work for CCITTFaxDecode
        img_size = len(data)
        tiff_header = cvMCTest.tiff_header_for_ccitt(width, height, img_size, ccitt_group)
        data = tiff_header + data
        return cv2.imdecode(np.frombuffer(data, np.uint8), cvMCTest.CV_CUR_LOAD_IM_GRAY)

    @staticmethod
    def handle_other_img(obj):
        data = obj._data
        return 255 - cv2.imdecode(np.frombuffer(data, np.uint8), cvMCTest.CV_CUR_LOAD_IM_GRAY)

    @staticmethod
    def get_img_from_page(pdf_obj, page):
        page_obj = pdf_obj.getPage(page)
        x_obj = page_obj['/Resources']['/XObject'].getObject()
        for obj in x_obj:
            if x_obj[obj]['/Subtype'] == '/Image':
                if x_obj[obj]['/Filter'] == '/CCITTFaxDecode':
                    return cvMCTest.handle_ccitt_fax_decode_img(x_obj[obj])
                else:
                    return cvMCTest.handle_other_img(x_obj[obj])

    @staticmethod
    def get_images_from_pdf(file_path):
        pdf_obj = PyPDF2.PdfFileReader(open(file_path, "rb"))
        n_pages = pdf_obj.getNumPages()
        images = [cvMCTest.get_img_from_page(pdf_obj, page) for page in range(n_pages)]
        return images

    ################ para segmentar imagens #################
    @staticmethod
    def decodeQRcode(img):
        DEBUG = False
        if DEBUG: cv2.imwrite("_test_decodeQRcode_01all.png", img)

        qr = dict()
        if True:
            dec0 = decode(img)
            if not dec0:
                return []

            dec0 = dec0[0][0]
            safterScan = binascii.unhexlify(dec0)

            if len(safterScan) < 51:  ##### este caso é para questões dissertativas com uma questão por folha
                dec = zlib.decompress(safterScan)
                dec = dec.decode('utf-8')
                ss = str(dec).split(';')
                qr['date'] = ss[0]  # [2:]
                qr['idClassroom'] = ss[1]
                qr['idExam'] = ss[2]
                qr['idStudent'] = ss[3]
                qr['term'] = ss[4]
                qr['text'] = ss[5]
                qr['question'] = ss[6]
            else:
                un_hashed = safterScan[:53].decode('utf-8')
                safterScan = safterScan[53:]
                dec = zlib.decompress(safterScan)
                dec = dec.decode('utf-8')
                ss = str(dec).split(';')
                pre = '$2b$06$' + un_hashed

                qr['date'] = ss[0]  # [2:]
                qr['idClassroom'] = ss[1]
                qr['idExam'] = ss[2]
                qr['idStudent'] = ss[3]

                if len(ss[3]) >= 8:
                    stu = ss[3][:8].encode('utf-8')
                else:
                    stu = ss[3].zfill(8).encode('utf-8')

                if pre.encode('utf-8') != bcrypt.hashpw(stu, pre.encode('utf-8')):
                    return HttpResponse("error18 = ERROR")

                qr['term'] = ss[4]
                qr['stylesheet'] = ss[5]  # 0=vert ; 1=horiz
                qr['var1'] = ss[6]
                qr['var2'] = ss[7]
                qr['var3'] = ss[8]
                qr['var4'] = ss[9]
                qr['var5'] = ss[10]
                qr['text'] = ss[11]
                numMCQ = int(ss[6]) + int(ss[7]) + int(ss[8]) + int(ss[9]) + int(ss[10])
                numQT = int(qr['text'])
                qr['answer'] = ss[12]
                qr['numquest'] = numMCQ
                qr['correct'] = ''  ### Quando o gabarito esta na primeira pagina do pdf

                # ler gabarito do servidor
                # fi = ';'.join([i for i in dec.split(';')[:-1]])
                fileGAB = 'tmpGAB/' + dec + '.txt'
                if os.path.exists(fileGAB):
                    with open(fileGAB, 'r') as myfile:
                        mysbeforeQR = myfile.read()
                        myfile.close()
                else:
                    qr['correct'] = ''
                    qr['dbtext'] = ''
                    return qr

                safterScanmy = binascii.unhexlify(mysbeforeQR)
                un_hashed = safterScanmy[:53]
                safterScan = safterScanmy[53:]
                decompressed = zlib.decompress(safterScan)
                decompressed = decompressed.decode('utf-8')
                ss0 = str(decompressed).split(';')
                print(ss, '!=', ss0)
                if ss[0:12] != ss0[0:12]:
                    raise Http404("ERRO:", ss, '!=', ss0)

                if len(ss0) > 12:  ### Quando as respostas corretas estao no QRcode
                    qr['correct'] = ss0[len(ss0) - numMCQ - numQT - 1:-1 - numQT]
                    qr['dbtext'] = ss0[len(ss0) - numQT - 1: -1]

        return qr

    @staticmethod
    def isBigRectangle(p1, p2, p3, p4):
        x1, y1 = p1
        x2, y2 = p2
        x3, y3 = p3
        x4, y4 = p4
        cx = (x1 + x2 + x3 + x4) / 4  # centro de massa
        cy = (y1 + y2 + y3 + y4) / 4

        # distancia do centro de massa aos extremos do rectangulo
        dd1 = math.sqrt((cx - x1) ** 2) + math.sqrt((cy - y1) ** 2)
        dd2 = math.sqrt((cx - x2) ** 2) + math.sqrt((cy - y2) ** 2)
        dd3 = math.sqrt((cx - x3) ** 2) + math.sqrt((cy - y3) ** 2)
        dd4 = math.sqrt((cx - x4) ** 2) + math.sqrt((cy - y4) ** 2)
        ddmin = np.mean([dd1, dd2, dd3, dd4])

        erro = max(abs(dd1 - dd2), abs(dd1 - dd3), abs(dd1 - dd4), abs(dd2 - dd3), abs(dd2 - dd4), abs(dd3 - dd4))

        return erro < 50 and ddmin > 500  # > w/2=1350/2

    @staticmethod
    def four_point_transform(image, pts):
        # adaptado de: http://www.pyimagesearch.com/2014/08/25/4-point-opencv-getperspective-transform-example/
        rect = pts  # Utils.order_points(pts)
        (tl, tr, br, bl) = rect
        widthA = np.sqrt(((br[0] - bl[0]) ** 2) + ((br[1] - bl[1]) ** 2))
        widthB = np.sqrt(((tr[0] - tl[0]) ** 2) + ((tr[1] - tl[1]) ** 2))
        maxWidth = max(int(widthA), int(widthB))
        heightA = np.sqrt(((tr[0] - br[0]) ** 2) + ((tr[1] - br[1]) ** 2))
        heightB = np.sqrt(((tl[0] - bl[0]) ** 2) + ((tl[1] - bl[1]) ** 2))
        maxHeight = max(int(heightA), int(heightB))
        dst = np.array([[0, 0], [maxWidth - 1, 0], [maxWidth - 1, maxHeight - 1], [0, maxHeight - 1]], dtype="float32")
        BORDER = -15
        M = cv2.getPerspectiveTransform(dst, rect)
        M[0, 2] = -pts[0][1] - BORDER
        M[1, 2] = -pts[0][0] - BORDER
        warped = cv2.warpPerspective(image, M, (maxHeight - 2 * BORDER, maxWidth - 2 * BORDER))
        return warped

    @staticmethod
    def order_points(pts):
        # fonte: http://www.pyimagesearch.com/2014/08/25/4-point-opencv-getperspective-transform-example/
        rect = np.zeros((4, 2), dtype="int64")
        s = np.sum(pts, axis=1)
        rect[0] = pts[np.argmin(s)]
        rect[2] = pts[np.argmax(s)]
        diff = np.diff(pts, axis=1)
        rect[1] = pts[np.argmin(diff)]
        rect[3] = pts[np.argmax(diff)]
        return rect

    @staticmethod
    def get_circles(img, countPage):
        DEBUG = False
        if DEBUG: cv2.imwrite("_testget_circles00" + "_p" + str(countPage + 1).zfill(3) + "_01.png", img)

        img = cv2.medianBlur(img, 3)
        if DEBUG: cv2.imwrite("_testget_circles00" + "_p" + str(countPage + 1).zfill(3) + "_02.png", img)

        b = 1;
        img[:, -b:] = img[:, :b] = img[:b, :] = img[-b:, :] = 255
        ret, img = cv2.threshold(img, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
        if DEBUG: cv2.imwrite("_testget_circles00" + "_p" + str(countPage + 1).zfill(3) + "_03.png", img)

        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))
        img = cv2.morphologyEx(img, cv2.MORPH_CLOSE, kernel)
        if DEBUG: cv2.imwrite("_testget_circles00" + "_p" + str(countPage + 1).zfill(3) + "_04.png", img)

        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (19, 19))
        img = cv2.morphologyEx(img, cv2.MORPH_OPEN, kernel)
        if DEBUG: cv2.imwrite("_testget_circles00" + "_p" + str(countPage + 1).zfill(3) + "_05.png", img)

        img = cv2.distanceTransform(img, cv2.DIST_L2, 3)
        if DEBUG: cv2.imwrite("_testget_circles00" + "_p" + str(countPage + 1).zfill(3) + "_06.png", img)

        # label
        labels = label(cvMCTest.imfillhole(img))
        if DEBUG: cv2.imwrite("_testget_circles00" + "_p" + str(countPage + 1).zfill(3) + "_07.png", img)

        # encontra circulos
        # print ("in "+str(circle_min)+" until "+str(circle_max)+" ? ")
        p = []
        areaMax = 0
        for region in regionprops(labels):
            if areaMax < region.area:
                areaMax = region.area
            h, w = region.centroid
            if circle_min < region.area < circle_max:
                # print("####region.area####===", region.area, int(h), int(w))
                p.append([int(h), int(w)])

        findRec = []  # se tiver mais que 4 pontos, escolho os que formam um retangulo
        for i in np.array(list(it.combinations(range(len(p)), 4))):
            # print(i)
            if len(i) == 4 and cvMCTest.isBigRectangle(p[i[0]], p[i[1]], p[i[2]], p[i[3]]):
                findRec = [p[i[0]], p[i[1]], p[i[2]], p[i[3]]]

        if not findRec:
            print("ERRO in get_circles: to not find circles")
            print("AREA MAXIMA DO CIRCULO = ", areaMax)
            print("INTERVALO CONSIDERADO  = ", circle_min, circle_max)
            return -1
        else:
            return cvMCTest.order_points(findRec)

    @staticmethod
    def getAnswerArea(img, countPage):
        DEBUG = False

        if DEBUG: cv2.imwrite("_getAnswerArea.png", img)
        H, W = img.shape
        if (H < W):
            img = np.rot90(img)
        if DEBUG: cv2.imwrite("_getAnswerArea" + "_p" + str(countPage + 1).zfill(3) + "_01.png", img)
        # padroniza dimensoes da imagem   
        H = 1754;
        W = 1350;
        img = cv2.resize(img, (W, H), interpolation=cv2.INTER_CUBIC)
        if DEBUG: cv2.imwrite("_getAnswerArea" + "_p" + str(countPage + 1).zfill(3) + "_02.png", img)

        pts = cvMCTest.get_circles(img, countPage)
        pts = np.array(pts, np.float32)
        img = cvMCTest.four_point_transform(img, pts)
        if DEBUG: cv2.imwrite("_getAnswerArea" + "_p" + str(countPage + 1).zfill(3) + "_03.png", img)
        return img

    @staticmethod
    def segmentQRcode(img, countPage):
        DEBUG = False

        img0 = img.copy()
        if DEBUG: cv2.imwrite("_testQRcode" + "_p" + str(countPage + 1).zfill(3) + "_01.png", img)

        img = cv2.GaussianBlur(img, (11, 11), 0)
        if DEBUG: cv2.imwrite("_testQRcode" + "_p" + str(countPage + 1).zfill(3) + "_02.png", img)

        ret, img = cv2.threshold(img, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
        if DEBUG: cv2.imwrite("_testQRcode" + "_p" + str(countPage + 1).zfill(3) + "_03.png", img)

        se = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
        img = cv2.morphologyEx(img, cv2.MORPH_ERODE, se)
        if DEBUG: cv2.imwrite("_testQRcode" + "_p" + str(countPage + 1).zfill(3) + "_04ero3x3.png", img)

        se = cv2.getStructuringElement(cv2.MORPH_RECT, (7, 7))
        img = cv2.morphologyEx(img, cv2.MORPH_CLOSE, se)
        if DEBUG: cv2.imwrite("_testQRcode" + "_p" + str(countPage + 1).zfill(3) + "_05clo7x7.png", img)

        img = cvMCTest.imfillhole(img)
        if DEBUG: cv2.imwrite("_testQRcode" + "_p" + str(countPage + 1).zfill(3) + "_06fill.png", img)

        se = cv2.getStructuringElement(cv2.MORPH_RECT, (1, 35))
        img = cv2.morphologyEx(img, cv2.MORPH_OPEN, se)
        if DEBUG: cv2.imwrite("_testQRcode" + "_p" + str(countPage + 1).zfill(3) + "_07open1x35.png", img)

        se = cv2.getStructuringElement(cv2.MORPH_RECT, (35, 1))
        img = cv2.morphologyEx(img, cv2.MORPH_OPEN, se)
        if DEBUG: cv2.imwrite("_testQRcode" + "_p" + str(countPage + 1).zfill(3) + "_08open35x1.png", img)

        # find the contours in the thresholded image
        (_, cnts, _) = cv2.findContours(img.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        # if no contours were found, return None
        if len(cnts) == 0:
            return None

        # c = sorted(cnts, key = cv2.contourArea, reverse = True)[0]

        for c in cnts:
            x, y, w, h = cv2.boundingRect(c)
            if abs(w - h) < 30 and x + w > 800 and y < 200:  # quadrado e no topo direito

                if 10000 < cv2.contourArea(c):
                    # raise Http404(cv2.contourArea(c),str(x+w),str(y))
                    rect = cv2.minAreaRect(c)
                    box = np.int0(cv2.boxPoints(rect))

        square = box  # self.SortPointsExtreme(box)
        y1, x1 = square[1]
        y2, x2 = square[3]
        [p1, p2] = [[min(x1, x2), min(y1, y2)], [max(x1, x2), max(y1, y2)]]

        # H, W = img.shape

        bord = 7
        img = img0[p1[0] - bord:p2[0] + bord, p1[1] - bord:p2[1] + bord]
        if DEBUG: cv2.imwrite("_testQRcode" + "_p" + str(countPage + 1).zfill(3) + "_09_qrcode.png", img)
        return img

    @staticmethod
    def imfillhole(img):
        # label
        labels = label(img == 0)
        labelCount = np.bincount(labels.ravel())
        background = np.argmax(labelCount)
        img[labels != background] = 255
        # labels = label(img)
        return img

    @staticmethod
    def imclearborder(imgBW, radius):
        # fonte: https://www.codementor.io/tips/8240393197/segmenting-license-plate-characters

        # Given a black and white image, first find all of its contours
        imgBWcopy = imgBW.copy()
        (_, contours, _) = cv2.findContours(imgBWcopy.copy(), cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)

        # Get dimensions of image
        imgRows = imgBW.shape[0]
        imgCols = imgBW.shape[1]

        contourList = []  # ID list of contours that touch the border

        # For each contour...
        for idx in np.arange(len(contours)):
            # Get the i'th contour
            cnt = contours[idx]

            # Look at each point in the contour
            for pt in cnt:
                rowCnt = pt[0][1]
                colCnt = pt[0][0]

                # If this is within the radius of the border
                # this contour goes bye bye!
                check1 = (rowCnt >= 0 and rowCnt < radius) or (rowCnt >= imgRows - 1 - radius and rowCnt < imgRows)
                check2 = (colCnt >= 0 and colCnt < radius) or (colCnt >= imgCols - 1 - radius and colCnt < imgCols)

                if check1 or check2:
                    contourList.append(idx)
                    break

        for idx in contourList:
            cv2.drawContours(imgBWcopy, contours, idx, (0, 0, 0), -1)

        return imgBWcopy

    @staticmethod
    def SortPointsExtreme(big_rectangle):  # ordena extremos do quadro
        points2 = np.float32(big_rectangle)

        Haux = (points2[:, :, 1].min() + points2[:, :, 1].max()) / 2
        Waux = (points2[:, :, 0].min() + points2[:, :, 0].max()) / 2
        p0 = p1 = p2 = p3 = []
        for i in range(4):
            if points2[i, 0, 0] < Waux and points2[i, 0, 1] < Haux:
                p0 = points2[i, 0]
            if points2[i, 0, 0] < Waux and points2[i, 0, 1] > Haux:
                p1 = points2[i, 0]
            if points2[i, 0, 0] > Waux and points2[i, 0, 1] > Haux:
                p2 = points2[i, 0]
            if points2[i, 0, 0] > Waux and points2[i, 0, 1] < Haux:
                p3 = points2[i, 0]
        return np.float32([p0, p1, p2, p3])

    @staticmethod
    def findSquaresHor(qr, img, countPage):
        DEBUG = False
        # img0 = img

        if DEBUG: cv2.imwrite("_testfindSquares" + "_p" + str(countPage + 1).zfill(3) + "_00.png", img)

        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (25, 25))
        img = cv2.morphologyEx(img, cv2.MORPH_DILATE, kernel)
        if DEBUG: cv2.imwrite("_testfindSquares" + "_p" + str(countPage + 1).zfill(3) + "_01.png", img)
        b = 5;
        img[:, -b:] = img[:, :b] = img[:b, :] = img[-b:, :] = 0

        imgSquares = img

        (_, contours, _) = cv2.findContours(img.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        contours = sorted(contours, key=cv2.contourArea, reverse=True)[:len(contours)]

        # size_rectangle_max = 0
        squares = []
        for cnt in contours:  # loop over the contours
            if int(qr['numquest']) <= 200:
                approximation = cv2.approxPolyDP(cnt, 0.04 * cv2.arcLength(cnt, True), True)
            else:
                approximation = cv2.approxPolyDP(cnt, 0.004 * cv2.arcLength(cnt, True), True)
                ############################# ATENCAO ^^^^^ TRATAMENTO DIFERENCIADO PARA >= 200 QUESTOES
            # has the polygon 4 sides?
            if (not (len(approximation) == 4)):
                continue;

            if (not cv2.isContourConvex(approximation)):
                continue;

            # descarta qrcode
            x, y, w, h = cv2.boundingRect(cnt)
            if abs(
                    w - h) < 30 and x + w > 800 and y < 200:  # quadrado e no topo direito
                if cv2.contourArea(cnt) > 25000:
                    continue;

            size_rectangle = cv2.contourArea(approximation)

            if size_rectangle > 2000:
                cv2.drawContours(imgSquares, [approximation], 0, (255, 0, 255), 10)
                squares.append(cvMCTest.SortPointsExtreme(approximation))

        pt = []
        ptSort = []
        H, W = imgSquares.shape
        for i in range(len(squares)):
            squa = squares[i]
            aux = np.array(squa, np.int64)
            y1, x1 = aux[1]
            y2, x2 = aux[3]
            [p1, p2] = [[min(x1, x2), min(y1, y2)], [max(x1, x2), max(y1, y2)]]
            ptSort.append([p1, p2])
            pc = int(p1[1] / 30) + W * int(p1[0] / 30)  # raster order
            pt.append(pc)

        pto = np.argsort(pt)
        rectSquares = []
        for i in range(len(ptSort)):
            rectSquares.append(ptSort[pto[i]])

        return rectSquares

    @staticmethod
    def findSquares(qr, img, countPage):

        DEBUG = False

        # img0 = img

        img = cvMCTest.findCirclesAnwsers(img, countPage, -1)

        # encontra quadros
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (15, 15))
        img = cv2.morphologyEx(img, cv2.MORPH_OPEN, kernel)

        if DEBUG: cv2.imwrite("_testfindSquares" + "_p" + str(countPage + 1).zfill(3) + "_01.png", img)

        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (30, 30))  # ajustar
        img = cv2.morphologyEx(img, cv2.MORPH_DILATE, kernel)

        if DEBUG: cv2.imwrite("_testfindSquares" + "_p" + str(countPage + 1).zfill(3) + "_02.png", img)

        b = 1;
        img[:, -b:] = img[:, :b] = img[:b, :] = img[-b:, :] = 0
        img = cv2.morphologyEx(img, cv2.MORPH_ERODE, kernel)

        if DEBUG: cv2.imwrite("_testfindSquares" + "_p" + str(countPage + 1).zfill(3) + "_03.png", img)

        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (1, 70))  # mudei 3/5/17, antes 120
        img = cv2.morphologyEx(img, cv2.MORPH_OPEN, kernel)

        if DEBUG: cv2.imwrite("_testfindSquares" + "_p" + str(countPage + 1).zfill(3) + "_04.png", img)

        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (50, 1))
        img = cv2.morphologyEx(img, cv2.MORPH_OPEN, kernel)

        if DEBUG: cv2.imwrite("_testfindSquares" + "_p" + str(countPage + 1).zfill(3) + "_05.png", img)

        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (25, 25))
        img = cv2.morphologyEx(img, cv2.MORPH_DILATE, kernel)

        if DEBUG: cv2.imwrite("_testfindSquares" + "_p" + str(countPage + 1).zfill(3) + "_06.png", img)
        b = 5;
        img[:, -b:] = img[:, :b] = img[:b, :] = img[-b:, :] = 0

        imgSquares = img

        (_, contours, _) = cv2.findContours(img.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        contours = sorted(contours, key=cv2.contourArea, reverse=True)[:len(contours)]

        # size_rectangle_max = 0
        squares = []
        for cnt in contours:  # loop over the contours

            if int(qr['numquest']) <= 200:
                approximation = cv2.approxPolyDP(cnt, 0.04 * cv2.arcLength(cnt, True), True)
            else:
                approximation = cv2.approxPolyDP(cnt, 0.004 * cv2.arcLength(cnt, True), True)
                ############################# ATENCAO ^^^^^ TRATAMENTO DIFERENCIADO PARA >= 200 QUESTOES

            # has the polygon 4 sides?
            if (not (len(approximation) == 4)):
                continue;
            # is the polygon convex ?
            if (not cv2.isContourConvex(approximation)):
                continue;
                # area of the polygon
            size_rectangle = cv2.contourArea(approximation)

            if size_rectangle > 800:
                cv2.drawContours(imgSquares, [approximation], 0, (255, 0, 255), 10)
                squares.append(cvMCTest.SortPointsExtreme(approximation))

        pt = []
        ptSort = []
        H, W = imgSquares.shape
        for i in range(len(squares)):
            squa = squares[i]

            aux = np.array(squa, np.int64)
            y1, x1 = aux[1]
            y2, x2 = aux[3]
            [p1, p2] = [[min(x1, x2), min(y1, y2)], [max(x1, x2), max(y1, y2)]]

            ptSort.append([p1, p2])

            # pc =int(p1[0]/30)+H*np.int(p1[1]/30)
            pc = int((p2[0] + p1[0]) / 30) + W * np.int((p2[1] + p1[1]) / 30)  # raster order
            pt.append(pc)

        pto = np.argsort(pt)

        rectSquares = []
        for i in range(len(ptSort)):
            rectSquares.append(ptSort[pto[i]])

        return rectSquares

    @staticmethod
    def findBoxesAnwsersHor(img, countPage, countSquare):
        DEBUG = False

        if DEBUG: cv2.imwrite(
            "_findBoxesAnwsersHor" + "_p" + str(countPage + 1).zfill(3) + "_" + str(countSquare + 1).zfill(
                3) + "_00.png", img)

        img = cv2.GaussianBlur(img, (7, 7), 0)
        if DEBUG: cv2.imwrite(
            "_findBoxesAnwsersHor" + "_p" + str(countPage + 1).zfill(3) + "_" + str(countSquare + 1).zfill(
                3) + "_01.png", img)

        se = cv2.getStructuringElement(cv2.MORPH_CROSS, (2, 1))
        img = cv2.morphologyEx(img, cv2.MORPH_OPEN, se)
        if DEBUG: cv2.imwrite(
            "_findBoxesAnwsersHor" + "_p" + str(countPage + 1).zfill(3) + "_" + str(countSquare + 1).zfill(
                3) + "_01OPEN1.png", img)

        se = cv2.getStructuringElement(cv2.MORPH_CROSS, (1, 2))
        img = cv2.morphologyEx(img, cv2.MORPH_OPEN, se)
        if DEBUG: cv2.imwrite(
            "_findBoxesAnwsersHor" + "_p" + str(countPage + 1).zfill(3) + "_" + str(countSquare + 1).zfill(
                3) + "_01OPEN2.png", img)

        # se = cv2.getStructuringElement(cv2.MORPH_CROSS,(3,1))
        # img=cv2.morphologyEx(img, cv2.MORPH_CLOSE, se)
        # if DEBUG: cv2.imwrite("_findBoxesAnwsersHor"+"_p"+str(countPage+1).zfill(3)+"_"+str(countSquare+1).zfill(3)+"_01op3.png", img)

        b = 20;
        img[:, -b:] = img[:, :b] = img[:b, :] = img[-b:, :] = 255
        ret, img = cv2.threshold(img, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
        # img0 = img
        if DEBUG: cv2.imwrite(
            "_findBoxesAnwsersHor" + "_p" + str(countPage + 1).zfill(3) + "_" + str(countSquare + 1).zfill(
                3) + "_02.png", img)

        img = cvMCTest.imfillhole(img)
        if DEBUG: cv2.imwrite(
            "_findBoxesAnwsersHor" + "_p" + str(countPage + 1).zfill(3) + "_" + str(countSquare + 1).zfill(
                3) + "_02fill.png", img)

        se = cv2.getStructuringElement(cv2.MORPH_RECT, (9, 1))  # vertical
        img = cv2.morphologyEx(img, cv2.MORPH_ERODE, se)
        if DEBUG: cv2.imwrite(
            "_findBoxesAnwsersHor" + "_p" + str(countPage + 1).zfill(3) + "_" + str(countSquare + 1).zfill(
                3) + "_03ero1.png", img)

        se = cv2.getStructuringElement(cv2.MORPH_CROSS, (1, 7))  # horizontal
        img = cv2.morphologyEx(img, cv2.MORPH_ERODE, se)
        if DEBUG: cv2.imwrite(
            "_findBoxesAnwsersHor" + "_p" + str(countPage + 1).zfill(3) + "_" + str(countSquare + 1).zfill(
                3) + "_03ero2.png", img)

        se = cv2.getStructuringElement(cv2.MORPH_RECT, (15, 1))  # vertical
        img = cv2.morphologyEx(img, cv2.MORPH_OPEN, se)
        if DEBUG: cv2.imwrite(
            "_findBoxesAnwsersHor" + "_p" + str(countPage + 1).zfill(3) + "_" + str(countSquare + 1).zfill(
                3) + "_04ope1.png", img)

        se = cv2.getStructuringElement(cv2.MORPH_CROSS, (1, 15))  # horizontal
        img = cv2.morphologyEx(img, cv2.MORPH_OPEN, se)
        if DEBUG: cv2.imwrite(
            "_findBoxesAnwsersHor" + "_p" + str(countPage + 1).zfill(3) + "_" + str(countSquare + 1).zfill(
                3) + "_04open2.png", img)

        img = cv2.distanceTransform(img, cv2.DIST_L2, cv2.DIST_MASK_PRECISE)
        img = cvMCTest.imfillhole(img)
        labels = label(img)

        if DEBUG: cv2.imwrite(
            "_findBoxesAnwsersHor" + "_p" + str(countPage + 1).zfill(3) + "_" + str(countSquare + 1).zfill(
                3) + "_05fill.png", img)

        img = np.zeros(img.shape, dtype='uint8')
        for region in regionprops(labels):
            x0, y0 = region.centroid
            if 200 < region.area < 700 and x0 > 280:
                img[labels == region.label] = 255
            else:
                continue

        if DEBUG: cv2.imwrite(
            "_findBoxesAnwsersHor" + "_p" + str(countPage + 1).zfill(3) + "_" + str(countSquare + 1).zfill(
                3) + "_05region.png", img)

        img = cvMCTest.imclearborder(img, 1)
        if DEBUG: cv2.imwrite(
            "_findBoxesAnwsersHor" + "_p" + str(countPage + 1).zfill(3) + "_" + str(countSquare + 1).zfill(
                3) + "_06.png", img)

        cvMCTest.imgAnswersSegment = img

        # return img

    @staticmethod
    def findCirclesAnwsers(img, countPage, countSquare):  # count Columns, define automat. o nÃºmero de respostas

        # blur the image
        # img=cv2.GaussianBlur(img,(3,3),0)

        DEBUG = False

        if DEBUG: cv2.imwrite(
            "_findCirclesAnwsers" + "_p" + str(countPage + 1).zfill(3) + "_" + str(countSquare + 1).zfill(
                3) + "_01.png", img)

        # binarizaÃ§Ã£o por otsu
        b = 3;
        img[:, -b:] = img[:, :b] = img[:b, :] = img[-b:, :] = 255

        ret, img = cv2.threshold(img, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
        # img0 = img

        if DEBUG: cv2.imwrite(
            "_findCirclesAnwsers" + "_p" + str(countPage + 1).zfill(3) + "_" + str(countSquare + 1).zfill(
                3) + "_02.png", img)

        se = cv2.getStructuringElement(cv2.MORPH_CROSS, (3, 1))
        img = cv2.morphologyEx(img, cv2.MORPH_DILATE, se)

        if DEBUG: cv2.imwrite(
            "_findCirclesAnwsers" + "_p" + str(countPage + 1).zfill(3) + "_" + str(countSquare + 1).zfill(
                3) + "_03.png", img)

        se = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 1))
        img = cv2.morphologyEx(img, cv2.MORPH_CLOSE, se)
        img = cv2.morphologyEx(img, cv2.MORPH_CLOSE, se)

        if DEBUG: cv2.imwrite(
            "_findCirclesAnwsers" + "_p" + str(countPage + 1).zfill(3) + "_" + str(countSquare + 1).zfill(
                3) + "_04.png", img)

        # prenche buracos
        img = cv2.distanceTransform(img, cv2.DIST_L2, cv2.DIST_MASK_PRECISE)

        labels = label(cvMCTest.imfillhole(img))

        # encontra circulos
        img = np.zeros(img.shape, dtype='uint8')
        for region in regionprops(labels):
            if 230 < region.area < 410:  # alterei
                img[labels == region.label] = 255
            else:
                # print(region.area)
                continue

        if DEBUG: cv2.imwrite(
            "_findCirclesAnwsers" + "_p" + str(countPage + 1).zfill(3) + "_" + str(countSquare + 1).zfill(
                3) + "_05.png", img)

        img = cvMCTest.imclearborder(img, 1)
        if DEBUG: cv2.imwrite(
            "_findCirclesAnwsers" + "_p" + str(countPage + 1).zfill(3) + "_" + str(countSquare + 1).zfill(
                3) + "_06.png", img)

        return img

    @staticmethod
    def setColumnsHor(img, countPage, countSquare):  # count Columns, define automat. o nÃºmero de respostas
        H, W = img.shape
        DEBUG = False

        # img = cvMCTest.findBoxesAnwsersHorQi(img,countPage,-1)

        # ret, img = cv2.threshold(img,0,255,cv2.THRESH_BINARY_INV+cv2.THRESH_OTSU)
        if DEBUG: cv2.imwrite(
            "_testCol" + "_p" + str(countPage + 1).zfill(3) + "_" + str(countSquare + 1) + "_q_00.png", img)

        b = 1;
        img[:, -b:] = img[:, :b] = img[:b, :] = img[-b:, :] = 0
        se = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (4, 4))
        img = cv2.morphologyEx(img, cv2.MORPH_OPEN, se)
        if DEBUG: cv2.imwrite(
            "_testCol" + "_p" + str(countPage + 1).zfill(3) + "_" + str(countSquare + 1) + "_q_01.png", img)

        se = cv2.getStructuringElement(cv2.MORPH_RECT, (1, int(H / 2)))
        # img[:,W-1]=img[:,1]=img[1,:]=img[H-1,:]=0
        img = cv2.morphologyEx(img, cv2.MORPH_CLOSE, se)
        b = 3;
        img[:, -b:] = img[:, :b] = img[:b, :] = img[-b:, :] = 0
        if DEBUG: cv2.imwrite(
            "_testCol" + "_p" + str(countPage + 1).zfill(3) + "_" + str(countSquare + 1) + "_q_02.png", img)

        (_, contours, _) = cv2.findContours(img.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        contours = sorted(contours, key=cv2.contourArea, reverse=True)[:len(contours)]
        NUM = len(contours)
        if DEBUG: print("NUM_COLUMNS=", NUM)
        return [NUM, img]

    @staticmethod
    def setColumns(img, countPage, countSquare):  # count Columns, define automat. o nÃºmero de respostas
        H, W = img.shape
        DEBUG = False

        img = cvMCTest.findCirclesAnwsers(img, countPage, countSquare)

        b = 1;
        img[:, -b:] = img[:, :b] = img[:b, :] = img[-b:, :] = 0
        se = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (15, 15))
        img = cv2.morphologyEx(img, cv2.MORPH_OPEN, se)

        if DEBUG: cv2.imwrite(
            "_testCol" + "_p" + str(countPage + 1).zfill(3) + "_" + str(countSquare + 1) + "_q_01.png", img)

        # Morphological Opening
        se = cv2.getStructuringElement(cv2.MORPH_RECT, (1, int(H / 2)))
        # img[:,W-1]=img[:,1]=img[1,:]=img[H-1,:]=0
        img = cv2.morphologyEx(img, cv2.MORPH_CLOSE, se)

        b = 3;
        img[:, -b:] = img[:, :b] = img[:b, :] = img[-b:, :] = 0

        (_, contours, _) = cv2.findContours(img.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        contours = sorted(contours, key=cv2.contourArea, reverse=True)[:len(contours)]
        NUM = len(contours)
        if DEBUG: print("NUM_COLUMNS=", NUM)
        return [NUM, img]

    @staticmethod
    def setLinesHor(img, countPage, countSquare):  # count Lines, define automaticamente o nÃºmero de questoes
        H, W = img.shape
        DEBUG = False

        # img = cvMCTest.findBoxesAnwsersHorQi(img,countPage,-1)

        b = 1;
        img[:, -b:] = img[:, :b] = img[:b, :] = img[-b:, :] = 0
        se = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (4, 4))
        img = cv2.morphologyEx(img, cv2.MORPH_OPEN, se)
        if DEBUG: cv2.imwrite(
            "_testLines" + "_p" + str(countPage + 1).zfill(3) + "_" + str(countSquare + 1) + "_q_01.png", img)

        se = cv2.getStructuringElement(cv2.MORPH_RECT, (2 * W, 1))
        img = cv2.morphologyEx(img, cv2.MORPH_CLOSE, se)
        if DEBUG: cv2.imwrite(
            "_testLines" + "_p" + str(countPage + 1).zfill(3) + "_" + str(countSquare + 1) + "_q_02.png", img)

        b = 3;
        img[:, -b:] = img[:, :b] = img[:b, :] = img[-b:, :] = 0

        se = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
        img = cv2.morphologyEx(img, cv2.MORPH_ERODE, se)
        if DEBUG: cv2.imwrite(
            "_testLines" + "_p" + str(countPage + 1).zfill(3) + "_" + str(countSquare + 1) + "_q_03.png", img)

        b = 3;
        img[:, -b:] = img[:, :b] = img[:b, :] = img[-b:, :] = 0

        (_, contours, _) = cv2.findContours(img.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        contours = sorted(contours, key=cv2.contourArea, reverse=True)[:len(contours)]
        NUM = len(contours)
        if DEBUG: print("NUM_LINES=", NUM)
        return [NUM, img]

    @staticmethod
    def setLines(img, countPage, countSquare):  # count Lines, define automaticamente o nÃºmero de questoes
        H, W = img.shape
        DEBUG = False

        img = cvMCTest.findCirclesAnwsers(img, countPage, countSquare)

        b = 1;
        img[:, -b:] = img[:, :b] = img[:b, :] = img[-b:, :] = 0
        se = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (15, 15))
        img = cv2.morphologyEx(img, cv2.MORPH_OPEN, se)
        if DEBUG: cv2.imwrite(
            "_testLines" + "_p" + str(countPage + 1).zfill(3) + "_" + str(countSquare + 1) + "_q_01.png", img)

        # Morphological Opening
        se = cv2.getStructuringElement(cv2.MORPH_RECT, (2 * W, 1))
        img = cv2.morphologyEx(img, cv2.MORPH_CLOSE, se)
        if DEBUG: cv2.imwrite(
            "_testLines" + "_p" + str(countPage + 1).zfill(3) + "_" + str(countSquare + 1) + "_q_02.png", img)

        b = 3;
        img[:, -b:] = img[:, :b] = img[:b, :] = img[-b:, :] = 0

        se = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
        img = cv2.morphologyEx(img, cv2.MORPH_ERODE, se)
        if DEBUG: cv2.imwrite(
            "_testLines" + "_p" + str(countPage + 1).zfill(3) + "_" + str(countSquare + 1) + "_q_03.png", img)

        b = 3;
        img[:, -b:] = img[:, :b] = img[:b, :] = img[-b:, :] = 0

        (_, contours, _) = cv2.findContours(img.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        contours = sorted(contours, key=cv2.contourArea, reverse=True)[:len(contours)]
        NUM = len(contours)
        if DEBUG: print("NUM_LINES=", NUM)
        return [NUM, img]

    @staticmethod
    def segmentAnswersHor(img, countPage, countSquare, NUM_QUESTOES, qr):
        DEBUG = False
        notas = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'O', 'P']
        imgNC = img[1]
        img = img[0]
        H, W = img.shape

        if DEBUG: cv2.imwrite("_test_segmentAnswersHor" + "_p" + str(countPage + 1).zfill(3) + "_" + str(
            countSquare + 1) + "_p_01bin.png", img)
        if DEBUG: cv2.imwrite(
            "_test_segmentAnswersHor" + "_p" + str(countPage + 1).zfill(3) + "_" + str(countSquare + 1) + "_p_01nc.png",
            imgNC)
        if qr['idStudent'] == 'ERROR':
            pass
        idTest = qr['idStudent']
        NUM_RESPOSTAS = int(qr['answer'])
        [NUM, imgLines] = cvMCTest.setLinesHor(img, countPage, countSquare)
        [NUM, imgCols] = cvMCTest.setColumnsHor(img, countPage, countSquare)

        if DEBUG: cv2.imwrite("_test_segmentAnswersHor" + "_p" + str(countPage + 1).zfill(3) + "_" + str(
            countSquare + 1) + "_p_02imgCols.png", imgCols)
        if DEBUG: cv2.imwrite("_test_segmentAnswersHor" + "_p" + str(countPage + 1).zfill(3) + "_" + str(
            countSquare + 1) + "_p_02imgLines.png", imgLines)

        img = cv2.GaussianBlur(imgNC, (7, 7), 0)
        if DEBUG: cv2.imwrite("_test_segmentAnswersHor" + "_p" + str(countPage + 1).zfill(3) + "_" + str(
            countSquare + 1) + "_p_02Blur.png", img)

        img = cv2.adaptiveThreshold(img, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, 175, 1)
        if DEBUG: cv2.imwrite(
            "_test_segmentAnswersHor" + "_p" + str(countPage + 1).zfill(3) + "_" + str(countSquare + 1) + "_q_03.png",
            img)
        img[:, W - 1] = img[:, 1] = img[1, :] = img[H - 1, :] = 0

        img3 = cv2.bitwise_and(imgCols, imgLines)
        if DEBUG: cv2.imwrite("_test_segmentAnswersHor" + "_p" + str(countPage + 1).zfill(3) + "_" + str(
            countSquare + 1) + "_p_03and1.png", img3)

        img = cv2.bitwise_and(img, img3)
        if DEBUG: cv2.imwrite("_test_segmentAnswersHor" + "_p" + str(countPage + 1).zfill(3) + "_" + str(
            countSquare + 1) + "_p_03and2.png", img)

        if DEBUG: lixo = []
        q = 1
        jfim = 0
        jini = 0
        mr = []
        invalida = 0

        while 1:  # para cada COLUNA/QUESTAO da imagem

            count = 0
            while jfim < W and imgCols[10, jfim] == 0:
                jfim += 1
                jini = jfim
            while jfim < W and imgCols[10, jfim]:
                jfim += 1
            if jfim >= W:
                break
            if jini > 4:
                jini -= 4
            ## verifica qual foi a resposta em cada coluna/questao
            im = img[:, jini:jfim]

            if DEBUG: cv2.imwrite(
                "_test_segmentAnswersHor" + "_p" + str(countPage + 1).zfill(3) + "_" + str(
                    countSquare + 1) + "_p_04_" + str(jfim) + ".png",
                im)

            (_, contours, _) = cv2.findContours(im.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

            # ordenar pelo eixo vertical
            boundingBoxes = [cv2.boundingRect(c) for c in contours]
            (contoursOrder, boundingBoxes) = zip(
                *sorted(zip(contours, boundingBoxes), key=lambda b: b[1][1], reverse=False))

            answers_area = []  # em questões duplicadas, pegar a com maior area
            if DEBUG: rect = []
            answers_n = []
            countQuestions = 0
            count_aux = 0
            for cnt in contoursOrder:  # loop over the contours
                area = cv2.contourArea(cnt)
                if area > 100:  ################################# SENSIVEL!!!!!
                    count_aux += 1
                    x, y, w, h = cv2.boundingRect(cnt)
                    iii = im[y:y + h, x:x + w]

                    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))
                    iii = cv2.morphologyEx(iii, cv2.MORPH_CLOSE, kernel)

                    area = 110 - int(sum(sum(iii == 0)))

                    if DEBUG:
                        cv2.imwrite(
                            "_test_segmentAnswersHor" + "_p" + str(countPage + 1).zfill(3) + "_" + str(
                                countSquare + 1) +
                            "_p_04_q" + str(q) + "_" + str(count_aux) + "_area_" + str(area) + ".png", iii)

                    if area > 58:  ################################# SENSIVEL!!!!!
                        if DEBUG: rect.append([x, y, w, h])

                        n = notas[countQuestions]

                        answers_n.append(n)
                        answers_area.append(area)

                        count += 1

                    countQuestions += 1

            if DEBUG: lixo.append([countPage, q, NUM_RESPOSTAS, H, W, jini, jfim, count, rect, answers_area, answers_n])

            if count == 1:  # somente uma marcação ==> OK
                if count_aux == NUM_RESPOSTAS:
                    mr.append(n)
                else:  ################## ERRO na segmentacao das respostas
                    mr.append('#')

            elif count == 0:  # sem marcação ==> questão inválida!
                mr.append(str(count))  # questao invÃ¡lida
                invalida += 1

            else:  # se mais de uma marcação, analisar pela área desconsiderando as marcações fracas, com área < percOK% da área máxima
                # print "questÃ£o=",q+1,countSquare,jini,jfim
                percOK = 0.8  # < porcentagem da area maxima sera descartada
                aux = answers_area / np.max(answers_area) * 1.0 < percOK
                # verdade para áreas < percOK%, ex. [250 130 230] aux=[False True False]
                aaux = {x: list(aux).count(x) for x in set(list(aux))}  # conta False e True

                if count > 1 and False in aaux:  # salva somente as questoes com respostas duplicadas = areas > percOK
                    impath = BASE_DIR + "/tmp/_e" + str(qr['idExam']) + '_' + str(qr['user']) + '_' + str(qr['file'])[
                                                                                                      :-4]
                    impath += "_RETURN_p" + str(countPage + 1).zfill(3) + "_s" + str(countSquare + 1) + "_q" + str(
                        q).zfill(3)
                    if aaux[False] > 1:  # se tem mais que uma marcacao forte > percOK => questão inválida
                        impath += ".png"
                        if DEBUG:
                            print(">>>INVALIDA: ", impath)
                            print(">>>>>>>>>>>>>", answers_area)
                            print(">>>>>>>>>>>>>", answers_n)

                        cv2.imwrite(impath, imgNC[:, jini:jfim])

                        mr.append(str(count))  # questao invÃ¡lida
                        invalida = invalida + 1

                    elif True in aaux and aaux[False] == 1:
                        # se tem uma marcacao forte e uma ou mais marcacoes fracas < percOK, desconsidero, pegando somente a mais forte
                        if DEBUG:
                            print(">>>RECONSIDERAMOS: ", impath)
                            print(">>>>>>>>>>>>>>>>>>>", answers_area)
                            print(">>>>>>>>>>>>>>>>>>>", answers_n)
                            print(">>>>>>>>>>>>>>>>>>>", aux, answers_n[list(aux).index(False)])

                        respostaConsiderada = answers_n[
                            list(aux).index(False)]  # pego o conceito com marcacao mais forte > percOK!!!
                        impath += "_" + respostaConsiderada + "_OK.png"

                        cv2.imwrite(impath, imgNC[:, jini:jfim])
                        mr.append(respostaConsiderada)
            q += 1
            jfim += 1
        return ([countPage, idTest, countSquare, NUM_RESPOSTAS, NUM_QUESTOES, invalida, 0, mr])

    @staticmethod
    def segmentAnswers(img, countPage, countSquare, NUM_QUESTOES, qr):
        DEBUG = False
        imgNC = img[1]
        img0 = img = img[0]
        H, W = img.shape
        notas = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'O', 'P']
        if qr['idStudent'] == 'ERROR':
            pass
        idTest = qr['idStudent']
        NUM_RESPOSTAS = int(qr['answer'])
        [NUM, imgLins] = cvMCTest.setLines(img, countPage, countSquare)

        if DEBUG: cv2.imwrite(
            "_test_segmentAnswers" + "_p" + str(countPage + 1).zfill(3) + "_" + str(countSquare + 1) + "_q_01.png",
            img0)

        img = cv2.GaussianBlur(img0, (9, 9), 0)
        if DEBUG: cv2.imwrite(
            "_test_segmentAnswers" + "_p" + str(countPage + 1).zfill(3) + "_" + str(countSquare + 1) + "_q_02.png", img)

        ret, img = cv2.threshold(img, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
        if DEBUG: cv2.imwrite(
            "_test_segmentAnswers" + "_p" + str(countPage + 1).zfill(3) + "_" + str(countSquare + 1) + "_q_03.png", img)

        img[:, W - 1] = img[:, 1] = img[1, :] = img[H - 1, :] = 0
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (9, 9))
        img2 = cv2.morphologyEx(img, cv2.MORPH_OPEN, kernel)
        if DEBUG: cv2.imwrite(
            "_test_segmentAnswers" + "_p" + str(countPage + 1).zfill(3) + "_" + str(countSquare + 1) + "_q_04.png",
            img2)

        img[:, W - 1] = img[:, 1] = img[1, :] = img[H - 1, :] = 0

        q = 1
        jfim = 0
        jini = 0
        mr = []
        invalida = 0
        while 1:  # para cada linha da imagem
            count = 0
            while jfim < H and imgLins[jfim, 5] == 0:
                jfim = jfim + 1
                jini = jfim
            while jfim < H and imgLins[jfim, 5]:
                jfim = jfim + 1
            if jfim >= H:
                break
            # print q,j
            ## verifica qual foi a resposta
            im = img2[jini:jfim, :]

            if DEBUG: cv2.imwrite(
                "_test_segmentAnswers" + "_p" + str(countPage + 1).zfill(3) + "_" + str(
                    countSquare + 1) + "_q_04_" + str(jfim) + ".png",
                im)

            (_, contours, _) = cv2.findContours(im.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            answers_area = []  # em questões duplicadas, pegar a com maior area
            answers_n = []
            for cnt in contours:  # loop over the contours
                area = cv2.contourArea(cnt)
                if area > 50:
                    count = count + 1
                    x, y, w, h = cv2.boundingRect(cnt)
                    resp = int(x * NUM_RESPOSTAS / (W - 10))
                    n = notas[resp]
                    answers_n.append(n)
                    answers_area.append(area)
                    # print (NUM_RESPOSTAS,W,x,resp,n,count)

            if count == 1:  # somente uma marcação ==> OK
                mr.append(n)
            elif count == 0:  # sem marcação ==> questão inválida!
                mr.append(str(
                    count))  # questao invÃ¡lida
                invalida = invalida + 1
            else:
                # se mais de uma marcação, analisar pela área desconsiderando as marcações fracas, com área < percOK% da área máxima
                # print "questÃ£o=",q+1,countSquare,jini,jfim

                percOK = 0.75  # < porcentagem da area maxima sera descartada

                aux = answers_area / np.max(answers_area) * 1.0 < percOK
                # verdade para áreas < percOK%, ex. [250 130 230] aux=[False True False]  
                aaux = {x: list(aux).count(x) for x in set(list(aux))}  # conta False e True

                # return HttpResponse(str(answers_area),str(aux),str(aaux))

                if count > 1 and False in aaux:  # salva somente as questoes com respostas duplicadas = areas > percOK

                    impath = BASE_DIR + "/tmp/_e" + str(qr['idExam']) + '_' + str(qr['user']) + '_' + str(qr['file'])[
                                                                                                      :-4]
                    impath += "_RETURN_p" + str(countPage + 1).zfill(3) + "_s" + str(countSquare + 1) + "_q" + str(
                        q).zfill(3)
                    if aaux[False] > 1:  # se tem mais que uma marcação forte > percOK => questão inválida
                        impath += ".png"
                        if DEBUG:
                            print(">>>INVALIDA: ", impath)
                            print(">>>>>>>>>>>>>", answers_area)
                            print(">>>>>>>>>>>>>", answers_n)

                        cv2.imwrite(impath, img0[jini:jfim, :])

                        mr.append(str(
                            count))  # questao invÃ¡lida
                        invalida = invalida + 1

                    elif True in aaux and aaux[False] == 1:
                        # se tem uma marcacao forte e uma ou mais marcacoes fracas < percOK, desconsidero, pegando somente a mais forte

                        if DEBUG:
                            print(">>>RECONSIDERAMOS: ", impath)
                            print(">>>>>>>>>>>>>>>>>>>", answers_area)
                            print(">>>>>>>>>>>>>>>>>>>", answers_n)
                            print(">>>>>>>>>>>>>>>>>>>", aux, answers_n[list(aux).index(False)])

                        respostaConsiderada = answers_n[
                            list(aux).index(False)]  # pego o conceito com marcacao mais forte > percOK!!!

                        impath += "_" + respostaConsiderada + "_OK.png"

                        cv2.imwrite(impath, img0[jini:jfim, :])
                        # filePath=""
                        # impath=""
                        mr.append(respostaConsiderada)
            q = q + 1
            jfim = jfim + 1

        return ([countPage, idTest, countSquare, NUM_RESPOSTAS, NUM_QUESTOES, invalida, 0, mr])

    @staticmethod
    def setAnswarsOneLine(testAnswars, qr):
        i = 0
        # testAnswarsOneLine = []
        qr['answers'] = []

        # print('testAnswars=',testAnswars,len(testAnswars))
        invalida = nota = numquest = 0
        try:
            while i < len(testAnswars):
                test = testAnswars[i]
                resp = []
                invalida = nota = numquest = 0
                while (i < len(testAnswars) and str(test[0]) == str(testAnswars[i][0])):
                    resp.extend(testAnswars[i][7:])
                    numquest += int(testAnswars[i][4])
                    invalida += int(testAnswars[i][5])
                    nota += int(testAnswars[i][6])
                    i += 1

                r = []
                for j in resp:
                    r = np.concatenate((r, j), axis=0)

                qr['answers'] = ','.join(x for x in r)
                # qr['numquest']=numquest
                # qr['invalid']=invalida
                # qr['grade']=nota
        except:
            pass

        qr['numquest'] = numquest
        qr['invalid'] = invalida
        qr['grade'] = nota
        return qr

    @staticmethod
    def studentGrade(qr, qr0):
        notas = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'O', 'P']

        if qr['idStudent'] == 'ERROR' or (qr['exam_print'] == 'answ' and int(qr['page'])):
            if not 'correct' in qr:
                qr['correct'] = ''  # qr['answers']
            # return qr
            pass

        if qr['idStudent'] == 'ERROR' and qr['exam_print'] == 'both':
            qr['correct'] = qr['answers']
            return qr

        if qr['correct'][0:5] == 'ERROR':
            qr['correct'] = qr['answers'] + ',' + qr['correct']
            # print(qr)
            return qr

        resp = str(qr['answers']).split(',')
        nota = count = 0
        coresp = []

        try:
            student = Student.objects.filter(student_ID=qr['idStudent'])
            for s in StudentExam.objects.filter(exam=qr['idExam']).filter(student=student[0]): s.delete()
            # print(qr)
            studentExam = StudentExam.objects.create(
                exam=Exam.objects.get(pk=int(qr['idExam'])),
                student=student[0],
            )
            for q in StudentExamQuestion.objects.filter(studentExam=studentExam): q.delete()
        except:
            pass

        try:  # tenta salvar no BD a prova do aluno
            # if True:

            for q in qr['correct']:
                print(">>>>a", qr['answer'])
                print(">>>>q", q)
                a = q[len(q) - int(qr['answer']):]
                qID = int(q[:len(q) - int(qr['answer'])])
                print(">>>>q", q, len(qr['answer']))
                print("a", a)
                print("qID", qID)

                n = notas[a.find('0')]

                if n == resp[count]:
                    nota += 1
                    coresp.append(n)
                else:
                    coresp.append(resp[count] + '/' + n)
                try:
                    if not len(StudentExamQuestion.objects.filter(studentExam=studentExam).filter(question=q)):
                        StudentExamQuestion.objects.create(
                            studentExam=studentExam,
                            question=Question.objects.get(pk=qID),
                            studentAnswer=str(resp[count]),
                            answersOrder=a,
                        )
                except:
                    pass

                count += 1

        except:
            pass
            count += 1

        qr['respgrade'] = coresp

        if not count and qr['exam_print'] == 'answ':
            if not qr['correct'] and int(qr['page']):  # comparar com o gabarito da primeira pagina

                str2 = ''
                ss0 = qr0['answers'].split(',')
                ss1 = qr['answers'].split(',')

                if len(ss0) != len(ss1):
                    str2 = 'ERRO'
                else:
                    for i in range(0, len(ss0)):
                        if ss0[i] == ss1[i]:
                            nota += 1
                            str2 += ss0[i] + ','
                        else:
                            str2 += ss1[i] + "/" + ss0[i] + ','

                qr['correct'] = str2

            elif not int(qr['page']):  # se eh 1a pagina
                try:
                    a = int(qr['correct'][0])  # verifico as respostas estao no qrcode
                except:
                    qr['correct'] = qr0['answers']  # senao as respostas corretas <= respostas

        qr['grade'] = nota
        try:
            studentExam.grade = str(nota)
            studentExam.save()
        except:
            pass

        # for s in StudentExam.objects.all(): print(s.grade)
        # for q in StudentExamQuestion.objects.all(): print(q.studentAnswer,q.answersOrder)
        # print(qr)
        return qr

    @staticmethod
    def drawImageGAB(qr, strGAB, img):
        notas = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'O', 'P']
        qra = qr['answers'].split(',')

        flagQuestions = False  # somente respostas
        if len(qr['respgrade']):
            flagQuestions = True  # questoes no BD
        elif int(qr['page']) == 0:
            return 0

        if len(qra) != int(qr['numquest']):  # nao corrigiu corretamente
            cv2.imwrite(strGAB, img)
            return 0

        if int(qr['stylesheet']) == 1:  # and flagQuestions: # quadro vertical
            if flagQuestions:
                respostas = qr['respgrade']  # exame com questoes
            else:
                respostas = qr['correct'].split(',')  # somente respostas

            countQuestions = 0
            for squa in qr['squares']:
                p1, p2 = squa
                myFlag = True
                while myFlag and countQuestions < int(qr['numquest']):
                    q = countQuestions % int(qr['max_questions_square'])
                    lin = int(p1[0] + 15 + 22.7 * q)
                    if lin < p2[0]:
                        try:
                            if len(respostas[countQuestions]) == 3:
                                col = int(p1[1] + 31 * (notas.index(respostas[countQuestions][2]) + 1) - 14)
                                if col < p2[1]:
                                    cv2.circle(img, (col, lin), 11, (255, 0, 255), 2)
                        except:
                            pass
                    countQuestions += 1
                    if (countQuestions) % int(qr['max_questions_square']) == 0:
                        myFlag = False

        elif int(qr['stylesheet']) == 0:  # and not flagQuestions: # quadro horizontal e somente respostas
            if flagQuestions:
                respostas = qr['respgrade']  # exame com questoes
            else:
                respostas = qr['correct'].split(',')  # somente respostas
            countQuestions = 0
            for squa in qr['squares']:
                p1, p2 = squa
                myFlag = True
                while myFlag and countQuestions < int(qr['numquest']):
                    q = countQuestions % int(qr['max_questions_square'])
                    col = int(p1[1] + 17 + 31.4 * q)
                    if col < p2[1]:
                        try:
                            if len(respostas[countQuestions]) == 3:
                                lin = int(p1[0] - 13 + 28.6 * (notas.index(respostas[countQuestions][2]) + 1))
                                if lin < p2[0]:
                                    cv2.circle(img, (col, lin + 5), 11, (255, 0, 255), 2)
                        except:
                            pass
                    countQuestions += 1
                    if (countQuestions) % int(qr['max_questions_square']) == 0:
                        myFlag = False

        cv2.imwrite(strGAB, img)

    @staticmethod
    def writeCSV(qr):  # imprime conteÃºdo do arquivo csv
        with open(qr['file'][:-4] + '.csv', 'rb') as f:
            pass
            # reader = csv.reader(f)
            # for row in reader:
            #    print(','.join(row))

    @staticmethod
    def saveCSVone(qr):  # salva em disco todos os gabaritos e os testes num arquivo csv
        f = qr['file'][:-4] + '.csv'

        # conteudosStr = []

        if not os.path.exists(f):
            with open(f, 'w') as csvfile:
                spamWriter = csv.writer(csvfile, delimiter=' ', quotechar=' ', quoting=csv.QUOTE_MINIMAL)
                print(f + ' criado no HD')
                L1 = ['Pag', 'ID', 'Resp', 'Quest', 'Inv', 'Grade']

                try:  # add in 31/3/2023
                    i = int(qr['correct'][0])  # se for inteiro entao tem questoes no BD
                    # L1.extend(range(1, 1 + len(qr['correct'])))  # questoes
                    # L1.extend(range(1, 1 + len(qr['correct'])))  # id das questoes no BD
                    L1.extend(['Q' + str(i) for i in range(1, 1 + len(qr['correct']))])
                    L1.extend(['K' + str(i) for i in range(1, 1 + len(qr['correct']))])
                except:
                    L1.extend(['Q' + str(i) for i in range(1, 1 + len(qr['correct']))])
                    pass

                spamWriter.writerow([','.join([str(x) for x in L1])])

        if os.path.exists(f):
            with open(f, 'a') as csvfile:
                spamWriter = csv.writer(csvfile, delimiter=' ', quotechar=' ', quoting=csv.QUOTE_MINIMAL)
                try:
                    s = [str(int(qr['page']) + 1), qr['idStudent'], qr['answer'], qr['numquest'], qr['invalid'],
                         qr['grade']]
                    t = [','.join(str(x) for x in s)]
                except:
                    t = [int(qr['page']) + 1, ',', 'ERROR']
                    spamWriter.writerow(t)
                    return None

                t.append(',')

                try:
                    if len(qr['respgrade']) > 1:
                        t.append(','.join(x for x in qr['respgrade']))
                        t.append(',')
                except:
                    pass

                try:
                    a = int(qr['correct'][1])
                    t.append(','.join(x for x in qr['correct']))
                except:
                    t.append(''.join(x for x in qr['correct']))

                spamWriter.writerow(t)

    ####################################

    @staticmethod
    def studentSendEmail(qr, choiceReturnQuestions):  # gera pdf de feedback p/c/ aluno
        notas = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'O', 'P']
        try:
            s = Student.objects.filter(student_ID=qr['idStudent'])[0]
        except:
            return ""

        str1 = ""
        str1 += "\\noindent\\textbf{%s:} %s \n\n" % (_("Student"), str(s.student_name))
        str1 += "\\noindent\\textbf{%s:} %s \n\n" % (_("ID"), s.student_ID)
        str1 += "\\noindent\\textbf{%s:} %s \n\n \\vspace{0mm} \n" % (_("Email"), s.student_email)

        try:
            sex0 = StudentExam.objects.filter(exam=qr['idExam'])
            sex = sex0.filter(student=s)
            sex = sex[0]
        except:
            return ""

        if sex:
            aux = len(StudentExamQuestion.objects.filter(studentExam=sex))
            percent = round(100*int(sex.grade) / aux, 3)
            # str1 += "\\noindent\\textbf{%s:} %s/%s ($\\qty\{{%.3f}\}\{\\percent\}) \n\n" % (
            # _("Grade"), str(sex.grade), str(aux), percent)
            str1 += "\\noindent\\textbf{%s:} %s/%s ({%.3f}___percent___) \n\n" % (
            _("Grade"), str(sex.grade), str(aux), percent)
            str1 = str1.replace("___percent___", "\%")
            if choiceReturnQuestions:  # mostrar as questões com os gabaritos
                titl = _("Multiple Choice Questions")
                str1 += "\\noindent\\textbf{%s:}\\vspace{2mm}" % titl

                count = 0
                for qe in StudentExamQuestion.objects.filter(studentExam=sex):
                    count += 1

                    str1 += "\n\n\\noindent \\textbf{%s.} \t%s\n\n" % (str(count), qe.question.question_text)
                    ###### VALIDAR ISSO !!!!!!
                    aa = [a for a in qe.question.answers2.all()]  ###### VALIDAR ISSO !!!!!!
                    str1 += "\\textbf{%s:} \t%s\n\n" % (_("Correct answer"), aa[0].answer_text)

                    if qe.studentAnswer in notas:
                        index1 = notas.index(qe.studentAnswer)
                        if aa[0].answer_text != aa[int(qe.answersOrder[index1])].answer_text:
                            str1 += "\\textbf{%s:} \t[(%s)-%s]: %s \n\n" % (_("Your answer"),
                                                                            qe.studentAnswer,
                                                                            _("INCORRECT"),
                                                                            aa[int(
                                                                                qe.answersOrder[index1])].answer_text)
                        if aa[index1].answer_feedback:
                            str1 += "\\textbf{%s:} \t%s\n\n" % (_("Feedback"), aa[index1].answer_feedback)
                    else:
                        str1 += "\\textbf{%s}\n\n" % _("Invalid answer!")

        file_name = "studentEmail_e" + qr['idExam'] + "_r" + qr['idClassroom'] + "_s" + s.student_ID
        fileExameName = file_name + '.tex'

        strGAB = './pdfStudentEmail/studentEmail_e' + qr['idExam'] + '_r' + qr['idClassroom'] + '_s' + qr[
            'idStudent'] + '_GAB.png'

        with open(fileExameName, 'w') as fileExam:
            fileExam = open(fileExameName, 'w')
            # instrucoes = 'asdfasdf asdf afd '
            fileExam.write(Utils.getBegin())
            # fileExam.write(strHeader)
            strFig = "\\includegraphics[scale=%s]{%s}} \\\\ \n" % (0.3, strGAB)
            fileExam.write(strFig)
            fileExam.write(str1)
            fileExam.write("\\end{document}")
            fileExam.close()

        cmd = ['pdflatex', '-interaction', 'nonstopmode', fileExameName]
        proc = subprocess.Popen(cmd)
        proc.communicate()

        enviaOK = cvMCTest.sendMail(file_name + ".pdf", "Exam Correction by MCTest", s.student_email,
                                    str(s.student_name))

        path = os.getcwd()
        os.system("cp " + file_name + ".pdf " + path + "/pdfStudentEmail/")
        try:
            os.remove("{}.aux".format(file_name))
            os.remove("{}.log".format(file_name))
            os.remove("{}.tex".format(file_name))
            os.remove("{}.pdf".format(file_name))
            os.remove("{}.out".format(file_name))
            os.remove("temp.txt")
            pass
        except Exception as e:
            pass

    # funcao para envio do email
    @staticmethod
    def envia_email(servidor, porta, FROM, PASS, TO, subject, texto, anexo=[]):
        msg = MIMEMultipart()
        msg['From'] = FROM
        msg['To'] = TO
        msg['Subject'] = subject
        msg.attach(MIMEText(texto))

        # Anexa os arquivos
        for f in anexo:
            if isinstance(f, list):
                f = f[0]
            try:
                part = MIMEBase('application', 'octet-stream')
                part.set_payload(open(f, 'rb').read())
                encoders.encode_base64(part)
                part.add_header('Content-Disposition', 'attachment;filename="%s"' % os.path.basename(f))
                msg.attach(part)
            except Exception:
                return "****ERROR****"

        try:
            gm = smtplib.SMTP(servidor, porta)
            gm.ehlo()
            gm.starttls()
            gm.ehlo()
            gm.login(FROM, PASS)
            gm.sendmail(FROM, TO, msg.as_string())
            gm.close()
        except Exception:
            return "****ERROR****"
        return ''

    @staticmethod
    def sendMail(arquivo, msg_str, mailSend, aluno):
        destinatario = mailSend
        # destinatario = 'fzampirolli@gmail.com'

        # porta smtp do gmail e ufabc
        myporta = 587

        # Assunto do email
        assunto = "Mensagem automática enviada pelo MCTest"

        mensagem = "\n"
        mensagem += "Prezado(a) "
        mensagem += aluno + "\n"
        # mensagem += msg_str + "\n\n"
        mensagem += '''
Segue em anexo a sua atividade: Lista de Exercícios ou Exame.

Se receber em anexo um arquivo '.bin', renomear para '.pdf'.

***
Não retornar este email para webmctest@ufabc.edu.br, pois não será monitorado.
***

Se tiver alguma dúvida, entre em contato com o seu professor.

===
O MCTest é um software de código aberto (disponível no GitHub) para gerar e 
corrigir questões (em especial as parametrizadas - com variações) de forma 
automática e está sendo desenvolvido com apoio das instituições públicas: 
* Universidade Federal do ABC (UFABC)
* FAPESP
===
'''

        # chamada a funcao de envio do email
        return cvMCTest.envia_email(webMCTest_SERVER,
                                    myporta,
                                    webMCTest_FROM,
                                    webMCTest_PASS,
                                    destinatario,
                                    assunto,
                                    mensagem,
                                    [arquivo])
