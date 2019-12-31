#!/usr/bin/env python3

import pagexml
import glob
import random
import numpy as np
import cv2
import os
import fire

from collections import namedtuple
Point = namedtuple('Point', 'x y')
Rect = namedtuple('Rect', 'l t r b')
Color = namedtuple('Color', 'b g r')

def elem_bbox(pxml, xpath):
    """gets x,y coordinates of bounding box
    
    Args:
        pxml (pagexml.PageXML): pagexml document
        xpath (str): to select a region in pagexml
    
    Returns:
        numpy.ndarray: x and y coordinates of bounding box
    """
    elem = pxml.selectNth(xpath, 0)
    points = pxml.getPoints(elem)
    bbox = pxml.pointsBBox(points)
    coords = np.array([(bbox[0].x, bbox[0].y), (bbox[1].x, bbox[1].y),
                       (bbox[2].x, bbox[2].y), (bbox[3].x, bbox[3].y)], np.int32)
    return coords

def draw_rectangle(img, rect, color=(0, 255, 0)):
    """draw rectangle on image
    
    Args:
        img (numpy.ndarray): image on which rectangle is to drawn
        rect (Rect): coordinates of rectangle
        color (tuple, optional): color of choice. Defaults to (0, 255, 0).
    
    Returns:
        numpy.ndarray: image with drawn rectangle
    """
    lt = (rect[0], rect[1])
    br = (rect[2], rect[3])
    cv2.rectangle(img, lt, br, color)
    return img

def draw_polygon(img, points, color=(0, 255, 0)):
    """draw a polygon around a region (for debugging)
    
    Args:
        img (numpy.ndarray): image where polygon is to be drawn
        points (list): points of location
        color (tuple, optional): desired color. Defaults to (0, 255, 0).
    
    Returns:
        numpy.ndarray: returns an image with a polygon drawn
    """
    if type(points) is list:
        points = np.array(points)
    pts = points.reshape((-1, 1, 2))
    cv2.polylines(img, [pts], True, color)
    return img

def blend_images(bg, fg):
    """multply forground and background
    
    Args:
        bg (numpy.ndarray): background image
        fg (numpy.ndarray): foreground image
    
    Returns:
        numpy.ndarray: resultant of multiplication
    """
    blending = 'multiply'
    if blending == 'alpha':
        out = cv2.addWeighted(bg, 0.5, fg, 0.5, 0)
    elif blending == 'mask':
        mask = cv2.cvtColor(fg, cv2.COLOR_BGR2GRAY)
        mask = cv2.cvtColor(mask, cv2.COLOR_GRAY2BGR)
        mask = mask.astype(float) / 255
    
        fg = fg.astype(float)
        bg = bg.astype(float)
    
        bg = cv2.multiply(mask, bg)
        fg = cv2.multiply(1.0 - mask, fg)
        out = cv2.add(bg, fg)
    elif blending == 'multiply':
        fg = fg.astype(float) / 255
        bg = bg.astype(float) / 255
        out = np.multiply(bg, fg)
        out = out * 255
        out = out.astype(int)
    else:
        print('default')
        out = fg
    return out

def compute_scale(dim_doc, dim_sig):
    """computes scale fit and scale fill with respect to two image dimensions
    
    Args:
        dim_doc (numpy.ndarray): dimensions of an image in which second image is to be blend in
        dim_sig (numpy.ndarray): dimensions of second image which is to be blended
    
    Returns:
        numpy.float: scale fit and scale fill  
    """
    dim_scale = dim_doc/dim_sig
    scale_fit = dim_scale.min()
    return scale_fit

def get_img_rect(img):
    """gets the rectangle of image
    
    Args:
        img (numpy.ndarray): Image as a numpy array
    
    Returns:
        Rect: left, top, right, bottom points of rectangle
    """
    shape = img.shape
    rect = Rect(0, 0, shape[1], shape[0])
    return rect

def coords2rect(coords):
    """computes coordinates of rectangle
    
    Args:
        coords (numpy.ndarray): coordinates of rectangle
    
    Returns:
        Rect: Rectangle as left, top, right, bottom
    """
    rect = Rect(coords[0][0],coords[0][1],coords[2][0],coords[2][1])
    return rect

def rect2dim(rect):
    """computes dimension of rectangle
    
    Args:
        rect (Rect): rectangular coordinates as tuple
    
    Returns:
        numpy.ndarray: dimension as minomum as maximum
    """
    dim = np.array([rect.r - rect.l, rect.b - rect.t])
    return dim

def compute_rect(doc_rect, image_rect, scale_range = (0, 1), x_range = (0, 1), y_range= (0,1)):
    """computes a rectangle of blend region with randomness  
    
    Args:
        doc_rect (Rect): rectangular coordinates of target image as a tuple
        image_rect (Rect): rectangular coordinates of image to be blend into target image as a tuple
        scale_range (tuple, optional): scaling range . Defaults to (0, 1).
        x_range (tuple, optional): randomness along x-axis. Defaults to (0, 1).
        y_range (tuple, optional): randomness along y-axis. Defaults to (0, 1).
    
    Returns:
        Rect: rectangle coordinates 
    """
    dim_image = rect2dim(image_rect)
    dim_doc = rect2dim(doc_rect)
    scale_fit = compute_scale(dim_doc, dim_image)
    dim_randon = dim_image * scale_fit * random.randrange(scale_range[0] * 1000, scale_range[1] * 1000)/1000
    dim_randon = dim_randon.astype(int)
    x_doc = doc_rect.l
    y_doc = doc_rect.t
    x = random.randrange(x_range[0] * 1000, x_range[1] * 1000) / 1000 * (dim_doc[0] - dim_randon[0])
    y = random.randrange(y_range[0] * 1000, y_range[1] * 1000) / 1000 * (dim_doc[1] - dim_randon[1])
    rect_random = Rect(int(x_doc + x), int(y_doc + y),
                     int(x_doc + x + dim_randon[0]), int(y_doc + y + dim_randon[1]))
    return rect_random

def blend_single_xml(xmlfile, loc, img_list, xpath):
    """blends two images in a third image (taken from xml document) 
    
    Args:
        xmlfile (str): path to xml file from where third image is taken
        loc (str): 'left', 'right', 'top', 'bottom',  'top_bottom', 'left_right', 'centre'
        img_list (list): a list of image files
        xpath (str): xpath of xml file as blending target region corresponding third image 
    
    Returns:
        numpy.ndarray: blended document 
    """
    img_file = random.choice(img_list)
    image = cv2.imread(img_file)
    image_rect = get_img_rect(image)

    pxml = pagexml.PageXML(xmlfile)
    coords = elem_bbox(pxml, xpath)
    doc_rect = coords2rect(coords)
    filename = pxml.getPageImageFilename(0)
    filepath = os.path.join(os.path.dirname(xmlfile), filename)

    document = cv2.imread(filepath)
    if loc == 'left':
        rect = Rect(doc_rect.l, doc_rect.t, int((doc_rect.l  + doc_rect.r) / 2), doc_rect.b)
        document = blend(document, rect, image_rect, image)
    elif loc == 'right':
        rect = Rect(int((doc_rect.l  + doc_rect.r) / 2), doc_rect.t, doc_rect.r, doc_rect.b)
        document = blend(document, rect, image_rect, image)
    elif loc == 'top':
        rect = Rect(doc_rect.l, doc_rect.t, doc_rect.r, int((doc_rect.t  + doc_rect.b) / 2))
        document = blend(document, rect, image_rect, image)
    elif loc == 'bottom':
        rect = Rect(doc_rect.l, int((doc_rect.t  + doc_rect.b) / 2), doc_rect.r, doc_rect.b)
        document = blend(document, rect, image_rect, image)
    elif loc == 'centre':
        rect = doc_rect
        document = blend(document, rect, image_rect, image)
    elif loc == 'left_right':
        rect = Rect(doc_rect.l, doc_rect.t, int((doc_rect.l  + doc_rect.r) / 2), doc_rect.b)
        document = blend(document,rect,image_rect,image)

        img_file = random.choice(img_list)
        image = cv2.imread(img_file)
        image_rect = get_img_rect(image)
        rect = Rect(int((doc_rect.l + doc_rect.r) / 2), doc_rect.t, doc_rect.r, doc_rect.b)
        document = blend(document,rect,image_rect,image)
    elif loc == 'top_bottom':
        rect = Rect(doc_rect.l, doc_rect.t, doc_rect.r, int((doc_rect.t  + doc_rect.b) / 2))
        document = blend(document, rect, image_rect, image)

        img_file = random.choice(img_list)
        image = cv2.imread(img_file)
        image_rect = get_img_rect(image)
        rect = Rect(doc_rect.l, int((doc_rect.t  + doc_rect.b) / 2), doc_rect.r, doc_rect.b)
        document = blend(document, rect, image_rect, image)
    else:
        print('Insert location')
    return document

def blend(document, rect, image_rect, image):
    """Blends one image into another image (document) with bicubic interpolation
    
    Args:
        document (numpy.ndarray): Target image where another image is to be blend
        rect (__main__.Rect): rectangular coordinates of target image as tuple (i.e. 'Rect(l=0, t=0, r=216, b=234)')
        image_rect (__main__.Rect): rectangular coordinates of image to blend into target image as tuple (i.e. 'Rect(l=0, t=0, r=216, b=234)')
        image (str): image to blend in
    
    Returns:
        numpy.ndarray: blended image
    """
    rand_rect = compute_rect(rect, image_rect, (0.7,1.0))
    doc_region = document[rand_rect.t: rand_rect.b, rand_rect.l: rand_rect.r]
    dim = rect2dim(rand_rect)
    image_region = cv2.resize(image, (dim[0], dim[1]), cv2.INTER_CUBIC)
    blend_region = blend_images(doc_region, image_region)
    document[rand_rect.t: rand_rect.b, rand_rect.l: rand_rect.r] = blend_region
    return document

def create_dataset(xml_list, img_list, loc, number, outdir, xpath='//*[_:Property[@key="entity" and @value="signature"]]'):
    """creates one or more blend of images
    
    Args:
        xml_list (str): a list of xml files
        img_list (str): a list of image files
        loc (str): 'top', 'bottom', 'left', 'right', 'top_bottom', 'left_right', 'centre'
        number (int): number of target images
        outdir (str): path to save target images
        xpath (str, optional): xpath of region to blend. Defaults to '//*[_:Property[@key="entity" and @value="signature"]]'.
    """
    img_list = [line.rstrip('\n') for line in open(img_list)]
    xml_list = [line.rstrip('\n') for line in open(xml_list)]
    k = 0
    random.seed(10)
    for k in range (0, number):
        xmlfile = random.choice(xml_list)
        out_file = loc + '-%05d.png' %k
        document = blend_single_xml(xmlfile, loc, img_list, xpath)
        cv2.imwrite(os.path.join(outdir, out_file), document)
        k = k+1

if __name__ == "__main__":
    fire.Fire(create_dataset)
