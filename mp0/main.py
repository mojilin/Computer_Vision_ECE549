import matplotlib.pyplot as plt
from PIL import Image
import numpy as np


def crop_boarder(image, black, white):
    h, w = image.shape
    upper = 0
    bottom = h-1
    left = 0
    right = w-1
    while np.mean(image[upper]) < white or np.mean(image[upper]) > black:
        upper += 1
    while np.mean(image[bottom]) < white or np.mean(image[bottom]) > black:
        bottom -= 1
    while np.mean(image[left]) < white or np.mean(image[left]) > black:
        left += 1
    while np.mean(image[right]) < white or np.mean(image[right]) > black:
        right -= 1
    image = image[upper:bottom, left:right]
    return image


def divide_images(image):
    w, h = image.shape
    height = w // 3
    blue = image[0:height, :]
    green = image[height:2 * height, :]
    red = image[2 * height:3 * height, :]
    return blue, green, red


def zncc(c, d, dx, dy):
    if dx >= 0:
        c = c[dx:, :]
        d = d[dx:, :]
    else:
        c = c[:dx, :]
        d = d[:dx, :]
    if dy >= 0:
        c = c[:, dy:]
        d = d[:, dy:]
    else:
        c = c[:, :dy]
        d = d[:, :dy]
    c = (c - c.mean()) #/ np.linalg.norm(c)
    d = (d - d.mean()) #/ np.linalg.norm(d)
    return np.sum((c / np.linalg.norm(c)) * (d / np.linalg.norm(d)))
    # return np.sum(c * d)


def ssd(a, b):
    return np.sum(np.power(a - b, 2))


def get_move(b, dx, dy):
    a = np.copy(b)
    a = np.roll(a, dx, axis=0)
    a = np.roll(a, dy, axis=1)
    # if dx > 0:
    #     a[:dx, :] = np.zeros(a[:dx, :].shape)
    # elif dx < 0:
    #     a[dx:, :] = np.zeros(a[dx:, :].shape)
    # if dy > 0:
    #     a[:, :dy] = np.zeros(a[:, :dy].shape)
    # elif dy < 0:
    #     a[:, dy:] = np.zeros(a[:, dy:].shape)
    return a


def adjust_image(a, b, range_value, func_type, gdx, gdy):
    dx = 0
    dy = 0
    ssd_min = float('inf')
    for i in range(gdx - range_value, range_value + gdx + 1):
        for j in range(gdy - range_value, range_value + gdy + 1):
            new = get_move(b, i, j)
            if func_type == "ssd":
                ssd_value = ssd(a, new)
            else:
                ssd_value = -zncc(a, new, i, j)
            if ssd_value < ssd_min:
                ssd_min = ssd_value
                dx = i
                dy = j
    return dx, dy


def coarse_adjust(image, func_type, range_value):
    blue, green, red = divide_images(image)
    gdx, gdy = adjust_image(blue, green, range_value, func_type, 0, 0)
    rdx, rdy = adjust_image(blue, red, range_value, func_type, 0, 0)
    print(gdx, gdy, rdx, rdy)
    g = get_move(green, gdx, gdy)
    r = get_move(red, rdx, rdy)
    print(blue.shape)
    # blue = boarder_handler(blue, gdx, gdy, rdx, rdy)
    # g = boarder_handler(g, gdx, gdy, rdx, rdy)
    # r = boarder_handler(r, gdx, gdy, rdx, rdy)
    print(blue.shape)
    color = Image.merge('RGB', (Image.fromarray(r), Image.fromarray(g), Image.fromarray(blue)))
    return color, (gdx, gdy, rdx, rdy)


def high_quality_adjust(image, func_type, range_value, gdx, gdy, rdx, rdy):
    blue, green, red = divide_images(image)
    print(blue.shape)
    gdx, gdy = adjust_image(blue, green, range_value, func_type, gdx, gdy)
    rdx, rdy = adjust_image(blue, red, range_value, func_type, rdx, rdy)
    print(gdx, gdy, rdx, rdy)
    g = get_move(green, gdx, gdy)
    r = get_move(red, rdx, rdy)

    blue = boarder_handler(blue, gdx, gdy, rdx, rdy)
    g = boarder_handler(g, gdx, gdy, rdx, rdy)
    r = boarder_handler(r, gdx, gdy, rdx, rdy)
    print(blue.shape)
    color = Image.merge('RGB', (Image.fromarray(r), Image.fromarray(g), Image.fromarray(blue)))
    return color, (gdx, gdy, rdx, rdy)


def boarder_handler(a, gdx, gdy, rdx, rdy):
    if gdx >= 0 and rdx >= 0:
        b = a[max(gdx, rdx):, :]
    elif gdx < 0 and rdx < 0:
        b = a[:min(gdx, rdx), :]
    else:
        b = a[max(gdx, rdx):min(gdx, rdx), :]

    if gdy >= 0 and rdy >= 0:
        c = b[:, max(gdy, rdy):]
    elif gdy < 0 and rdy < 0:
        c = b[:, :min(gdy, rdy)]
    else:
        c = b[:, max(gdy, rdy):min(gdy, rdy)]
    return c


def gen_image(imageName, func_type, isHighQuality):
    img = Image.open(imageName)
    if isHighQuality:
        coarse_image = img.resize((img.width // 2, img.height // 2))
        image = np.asarray(coarse_image)
        _, (gdx, gdy, rdx, rdy) = coarse_adjust(image, func_type, 30)

        image = np.asarray(img)
        color, _ = high_quality_adjust(image, func_type, 15, 2*gdx, 2*gdy, 2*rdx, 2*rdy)
    else:
        image = np.asarray(img)
        w, h = image.shape
        image = image[int(w * 0.018):int(w - w * 0.018), int(h * 0.08):int(h - h * 0.08)]
        # image = crop_boarder(image, 180, 10)
        # plt.imshow(image)
        # plt.show()
        color, _ = coarse_adjust(image, func_type, 15)
    color.save(imageName+"new.jpg", "JPEG")
    plt.imshow(color)
    plt.show()


imageName = r'mp0-data/vancouver_tableau.jpg'
gen_image(imageName, "zncc", True)





