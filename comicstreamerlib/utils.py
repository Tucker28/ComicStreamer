# coding=utf-8

import sys
import os
import re
import platform
import locale
import codecs
import calendar
import hashlib
import time
import base64
from PIL import Image
try:
    from PIL import WebPImagePlugin
except:
    pass

import StringIO
from comicstreamerlib.folders import AppFolders
import imghdr

from datetime import datetime, timedelta
	
class UtilsVars:
	already_fixed_encoding = False

def get_actual_preferred_encoding():
	preferred_encoding = locale.getpreferredencoding()
	if platform.system() == "Darwin":	
		preferred_encoding = "utf-8"
	return preferred_encoding
	
def fix_output_encoding( ):
	if not UtilsVars.already_fixed_encoding:
		# this reads the environment and inits the right locale
		locale.setlocale(locale.LC_ALL, "")

		# try to make stdout/stderr encodings happy for unicode printing
		preferred_encoding = get_actual_preferred_encoding()
		sys.stdout = codecs.getwriter(preferred_encoding)(sys.stdout)
		sys.stderr = codecs.getwriter(preferred_encoding)(sys.stderr)
		UtilsVars.already_fixed_encoding = True
	
def touch(fname, times=None):
    with open(fname, 'a'):
        os.utime(fname, times)

def getDigest(password):
    digest = hashlib.sha256(password).hexdigest()
    for x in range(0, 1002):
        digest = hashlib.sha256(digest).hexdigest()
    time.sleep(.5)
    return digest


def encode(key, clear):
    enc = []
    for i in range(len(clear)):
        key_c = key[i % len(key)]
        enc_c = chr((ord(clear[i]) + ord(key_c)) % 256)
        enc.append(enc_c)
    return base64.urlsafe_b64encode("".join(enc))

def decode(key, enc):
    dec = []
    enc = base64.urlsafe_b64decode(enc)
    for i in range(len(enc)):
        key_c = key[i % len(key)]
        dec_c = chr((256 + ord(enc[i]) - ord(key_c)) % 256)
        dec.append(dec_c)
    return "".join(dec)

def utc_to_local(utc_dt):
    # get integer timestamp to avoid precision lost
    timestamp = calendar.timegm(utc_dt.timetuple())
    local_dt = datetime.fromtimestamp(timestamp)
    assert utc_dt.resolution >= timedelta(microseconds=1)
    return local_dt.replace(microsecond=utc_dt.microsecond)

def alert(title, msg):
    if getattr(sys, 'frozen', None):
        if platform.system() == "Darwin":
            import Tkinter, tkMessageBox
            root = Tkinter.Tk()
            root.lift()
            root.attributes('-topmost', 1)
            root.withdraw()
            tkMessageBox.showinfo(title, msg)
        elif platform.system() == "Windows":
            import win32gui
            win32gui.MessageBox(0,msg,title,0)

def collapseRepeats(string, ch):
	return re.sub("/"+ ch + "*", ch, string) 

def resizeImage(max, image_data):
    # disable WebP for now, due a memory leak in python library
    imtype = imghdr.what(StringIO.StringIO(image_data))
    if imtype == "webp":
        with open(AppFolders.imagePath("missing.png"), 'rb') as fd:
            image_data = fd.read()

    im = Image.open(StringIO.StringIO(image_data)).convert('RGB')
    w,h = im.size
    if max < h:
        im.thumbnail((w,max), Image.ANTIALIAS)
        output = StringIO.StringIO()
        im.save(output, format="JPEG")
        return output.getvalue()
    else:
        return image_data

# optimized thumbnail generation
# simple comparison with resizeImage:
# >>> start = time.time(); foo = [utils.resizeImage(200, f) for i in range(1,100)]; print time.time() - start;
# 10.9432790279
# >>> start = time.time(); foo = [utils.resize(f, (200,200), StringIO.StringIO()) for i in range(1,100)]; print time.time() - start;
# 2.90805196762
#
# taken from http://united-coders.com/christian-harms/image-resizing-tips-every-coder-should-know/
def resize(img, box, out, fit=False):
    '''Downsample the image.
    @param img: Image -  an Image-object
    @param box: tuple(x, y) - the bounding box of the result image
    @param fix: boolean - crop the image to fill the box
    @param out: file-like-object - save the image into the output stream
    '''

    if type(img) != Image and type(img) == str:
        img = Image.open(StringIO.StringIO(img))

    #preresize image with factor 2, 4, 8 and fast algorithm
    factor = 1
    while img.size[0]/factor > 2*box[0] and img.size[1]*2/factor > 2*box[1]:
        factor *=2
    if factor > 1:
        try:
            img.thumbnail((img.size[0]/factor, img.size[1]/factor), Image.NEAREST)
        except IOError:
            print >> sys.stderr, u"Error reading in page. Image Corrupted"

    #calculate the cropping box and get the cropped part
    if fit:
        x1 = y1 = 0
        x2, y2 = img.size
        wRatio = 1.0 * x2/box[0]
        hRatio = 1.0 * y2/box[1]
        if hRatio > wRatio:
            y1 = int(y2/2-box[1]*wRatio/2)
            y2 = int(y2/2+box[1]*wRatio/2)
        else:
            x1 = int(x2/2-box[0]*hRatio/2)
            x2 = int(x2/2+box[0]*hRatio/2)
        img = img.crop((x1,y1,x2,y2))

    #Resize the image with best quality algorithm ANTI-ALIAS
    img.thumbnail(box, Image.ANTIALIAS)

    img = img.convert('RGB')

    #save it into a file-like object
    img.save(out, "JPEG", quality=65)
