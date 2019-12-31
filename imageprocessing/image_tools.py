#%%
import os
import pagexml
import numpy as np
import fire
import cv2

def read_pagexml(xml_file):
    """Read PageXML from file or string.

    Args:
        xml_file (str): PageXML file or string

    Returns:
        pxml: PageXML object for further use
    """
    pxml = pagexml.PageXML()
    if os.path.exists(xml_file):
        pxml.loadXml(xml_file)
    else:
        pxml.loadXmlString(xml_file)
    return pxml

def crop_region(xml_file, entity, out_file=None, im_file=None):
    """Crop text region with entity from PageXML file.
    
    Args:
        xml_file (str): PageXML file or string
        entity (str): Entity tag to be extracted
        out_file (str): Image file to be written
        im_file (str): (Optional) an imagename that should be used to map with the pagexml. If not given, it uses the
        image name within the pagexml Page property
    """
    pxml = read_pagexml(xml_file)
    if im_file is not None:
        pxml.setPageImageFilename(0, im_file)

    #%% Crop element with specific ID
    xpath = '//_:TextRegion[_:Property/@value="{}"]/_:Coords'.format(entity)
    cropped = pxml.crop(xpath)[0]

    #%% Save image to disk
    img = np.asarray(cropped.image)
    img = np.copy(img)
    if out_file != None:
        #pagexml.imwrite(out_file, img)
        cv2.imwrite(out_file, img)
    return img


#%%
if __name__ == "__main__":
    fire.Fire()
