from PIL import Image

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

    if w > h:
        bigw = haxdb.config["THUMBNAILS"]["BIG_MAX"]
        bigh = int(h * (float(bigw)/w))
        smallw = haxdb.config["THUMBNAILS"]["SMALL_MAX"]
        smallh = int(h * (float(smallw)/w))
    else:
        bigh = haxdb.config["THUMBNAILS"]["BIG_MAX"]
        bigw = int(w * (float(bigh)/h))
        smallh = haxdb.config["THUMBNAILS"]["SMALL_MAX"]
        smallw = int(w * (float(smallh)/h))

    thumb_big = thumb_big.resize((bigw, bigh), Image.ANTIALIAS)
    thumb_small = thumb_small.resize((smallw, smallh), Image.ANTIALIAS)

    big = StringIO.StringIO()
    small = StringIO.StringIO()
    thumb_big.save(big, "JPG")
    thumb_small.save(small, "JPG")
    return big.getvalue(), small.getvalue()


def init(app_haxdb):
    global haxdb
    haxdb = app_haxdb


def run():
    haxdb.func("THUMBNAIL_CREATE"), thumbnail_create)
