#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from PIL import Image


def crop_cover(filename):
    with Image.open(filename) as im:
        width, height = im.size

        # width divide height must be equal 3/4
        if width / height > 0.75:
            w = width - height * 0.75
            im.crop((w // 2, 0, width - w // 2, height)).save(filename)
            im.crop((0, 10, 300, 400)).save()
        elif width / height < 0.75:
            h = height - width // 0.75
            im.crop((0, h // 2, width, height - h // 2)).save(filename)


def quote(string):
    return string.replace('/', '／')
