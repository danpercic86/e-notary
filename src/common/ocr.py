import imutils
import numpy as np
from cv2 import cv2
from numpy.typing import NDArray
from pytesseract import pytesseract

roi = [
    [(982, 45), (1264, 102), "id_series", "0123456789ABCDEFGHJKLMNOPQRSTUVWZ"],
    [(460, 221), (1218, 274), "last_name"],
    [(463, 305), (1171, 354), "first_name"],
    # [(843, 384), (1019, 434), 'Sex', 'MF'],
    [(468, 464), (853, 515), "birthday"],
    [(468, 543), (853, 595), "id_emitted_at"],
    # [(468, 623), (853, 675), 'Data expirării'],
    [(557, 713), (1243, 770), "id_emitted_by"],
]

orb = cv2.ORB_create(5000)

percentage = 25


def match(img: NDArray, template: NDArray):
    key_points1, descriptors1 = orb.detectAndCompute(template, None)
    key_points2, descriptors2 = orb.detectAndCompute(img, None)
    bf = cv2.BFMatcher(cv2.NORM_HAMMING)
    matches = list(bf.match(descriptors2, descriptors1))
    matches.sort(key=lambda x: x.distance)
    good = matches[: int(len(matches) * (percentage / 100))]
    img_match = cv2.drawMatches(
        img, key_points2, template, key_points1, good[:100], None, flags=2
    )
    src_points = np.float32([key_points2[m.queryIdx].pt for m in good]).reshape(
        -1, 1, 2
    )
    dst_points = np.float32([key_points1[m.trainIdx].pt for m in good]).reshape(
        -1, 1, 2
    )

    M, _ = cv2.findHomography(src_points, dst_points, cv2.RANSAC, 5.0)

    return M, img_match


def ocr(filepath: str, templatepath: str):
    img = cv2.imread(filepath)
    template = cv2.imread(templatepath)
    height, width, _ = template.shape
    m, _ = match(img, template)
    img_scan = cv2.warpPerspective(img, m, (width, height))
    img_show = img_scan.copy()
    img_mask = np.zeros_like(img_show)

    result = {}

    for _, r in enumerate(roi):
        cv2.rectangle(img_mask, (r[0][0], r[0][1]), (r[1][0], r[1][1]), (0, 255, 0), 2)
        img_show = cv2.addWeighted(img_show, 0.99, img_mask, 0.1, 0)
        img_crop = img_scan[r[0][1]: r[1][1], r[0][0]: r[1][0]]
        img_crop = cv2.cvtColor(img_crop, cv2.COLOR_BGR2GRAY)
        thresh = cv2.threshold(
            img_crop, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU
        )[1]

        dist = cv2.distanceTransform(thresh, cv2.DIST_L2, 0)
        dist = cv2.normalize(dist, dist, 0, 1, cv2.NORM_MINMAX)
        dist = (dist * 255).astype("uint8")
        dist = cv2.threshold(dist, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)[1]

        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (1, 1))
        opening = cv2.morphologyEx(dist, cv2.MORPH_OPEN, kernel)

        cnts = cv2.findContours(dist.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        cnts = imutils.grab_contours(cnts)
        chars = []
        for c in cnts:
            (_, _, w, h) = cv2.boundingRect(c)
            if w >= 10 and h >= 15:
                chars.append(c)

        chars = np.vstack([chars[i] for i in range(0, len(chars))])
        hull = cv2.convexHull(chars)
        mask = np.zeros(img_crop.shape[:2], dtype="uint8")
        cv2.drawContours(mask, [hull], -1, 255, -1)
        mask = cv2.dilate(mask, None, iterations=2)
        final = cv2.bitwise_and(opening, opening, mask=mask)

        config = "--psm 8 "
        if len(r) >= 4:
            config += f"-c tessedit_char_whitelist={r[3]}"

        string: str = pytesseract.image_to_string(final, lang="ron", config=config)
        result.update({r[2]: string.strip().replace("\n", "")})

    return result
