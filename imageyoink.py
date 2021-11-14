import re
import requests


def is_url_image(image_url):
    image_formats = ("image/png", "image/jpeg",
                     "image/jpg", "image/webp")

    r = requests.head(image_url)
    if r.headers["content-type"] in image_formats:
        return True
    return False


def sorter(url):
    fixedurl = ""
    if "imgflip" in url:
        fixedurl = imgflip(url)
    elif "imgur" in url:
        fixedurl = imgur(url)
    else:
        fixedurl = url
    if is_url_image(fixedurl):
        return fixedurl
    else:
        return False


def imgflip(url):
    content = str(requests.get(url).text)
    regex = re.compile(
        """src='(//i.imgflip.com/.+)'""")
    img_url = regex.search(content).group(1)
    return "https:" + img_url.replace("\\", "//")


def imgur(url):
    content = str(requests.get(url).text)
    regex = re.compile(
        'content="(https://i.imgur.com/.+\.jpg)"')
    img_url = regex.search(content).group(1)
    return img_url.replace("\\", "//")
