import os
import shutil
import unittest
import filecmp
from PIL import Image
import numpy as np
import cv2
import logging

from imageprocessing.image_tools import crop_region
from imageprocessing.image_blend import elem_bbox
from imageprocessing.image_blend import draw_polygon
from imageprocessing.image_blend import compute_scale
from imageprocessing.image_blend import get_img_rect
from imageprocessing.image_blend import coords2rect
from imageprocessing.image_blend import rect2dim

from collections import namedtuple
Rect = namedtuple('Rect', 'l t r b')

PATH = 'data/temp/'
DEBUG = False


def show(image, title=''):
    if DEBUG:
        cv2.imshow(title, image)
        cv2.waitKey()
    else:
        pass


class ImageToolsTest(unittest.TestCase):
    def setUp(self):
        if os.path.exists(PATH):
            shutil.rmtree(PATH)
        os.makedirs(PATH)
        pass

    def test_crop_region_file(self):
        entity_list = ['sketch', 'signatures']
        xml_file = 'data/input/OMNI-0083-OC.xml'
        for entity in entity_list:
            logging.debug(entity)
            gt_file = 'data/output/{}.png'.format(entity)
            pr_file = os.path.join(PATH, '{}.png'.format(entity))
            crop_region(xml_file, entity, pr_file)
            equal = filecmp.cmp(gt_file, pr_file, False)
            logging.debug(equal)
            self.assertTrue(equal)

    def test_crop_region_img(self):
        entity_list = ['sketch', 'signatures']
        xml_file = 'data/input/OMNI-0083-OC.xml'
        for entity in entity_list:
            logging.debug(entity)
            gt_file = 'data/output/{}.png'.format(entity)
            gt_img = cv2.imread(gt_file)
            show(gt_img, 'gt')

            pr_img = crop_region(xml_file, entity)
            pr_img = pr_img[:, :, 0:3]
            show(pr_img, 'pr')

            diff_img = gt_img - pr_img
            logging.debug(diff_img.sum())
            diff_file = os.path.join(PATH, 'diff.bmp')
            show(diff_img, 'diff')

            equal = np.allclose(gt_img, pr_img)
            logging.debug(equal)
            self.assertTrue(equal)

    # TODO write unit test for crop_region based on an imagename, which differs from the imagename inside the pagexml.
    #  This enables us to cropped from a different image then the original pagefilename of the pagexml.

    def test_get_img_rect(self):
        image = cv2.imread('data/input/OMNI-0083-OC.jpg')
        rect = get_img_rect(image)
        self.assertEqual(rect, Rect(l=0, t=0, r=2480, b=3504))

    def test_coords2rect(self):
        coords = np.array([[2, 2], [4, 2], [4, 1], [2, 1]])
        rect = coords2rect(coords)
        self.assertEqual(rect, Rect(l=2, t=2, r=4, b=1))


if __name__ == "__main__":

    unittest.main()
