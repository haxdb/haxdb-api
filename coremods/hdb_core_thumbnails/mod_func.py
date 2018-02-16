from PIL import Image
import StringIO

haxdb = None


def thumbnail_create(img=None, file=None):
    if img:
        thumb_big = img.copy()
        thumb_small = img.copy()
        w, h = img.size
    elif file:
        try:
            thumb_big = Image.open(file)
            thumb_small = thumb_big.copy()
            w, h = thumb_big.size
        except Exception:
            return False, False
    else:
        return False, False

    ratio = w / h
    smallw = int(w)
    smallh = int(h)
    bigw = int(w)
    bigh = int(h)

    if bigh > haxdb.config["THUMBNAILS"]["BIG_H"]:
        bigh = haxdb.config["THUMBNAILS"]["BIG_H"]
        bigw = bigh * ratio

    if bigw > haxdb.config["THUMBNAILS"]["BIG_W"]:
        bigw = haxdb.config["THUMBNAILS"]["BIG_W"]
        bigh = bigh / ratio

    if smallh > haxdb.config["THUMBNAILS"]["SMALL_H"]:
        smallh = haxdb.config["THUMBNAILS"]["SMALL_H"]
        smallw = smallh * ratio

    if smallw > haxdb.config["THUMBNAILS"]["SMALL_W"]:
        smallw = haxdb.config["THUMBNAILS"]["SMALL_W"]
        smallh = smallh / ratio

    thumb_big = thumb_big.resize((bigw, bigh), Image.ANTIALIAS)
    thumb_small = thumb_small.resize((smallw, smallh), Image.ANTIALIAS)

    big = StringIO.StringIO()
    small = StringIO.StringIO()
    thumb_big.save(big, format="JPEG")
    thumb_small.save(small, format="JPEG")
    return big.getvalue(), small.getvalue()


def init(app_haxdb):
    global haxdb
    haxdb = app_haxdb
    haxdb.func("THUMB:CREATE", thumbnail_create)


def run():
    pass
