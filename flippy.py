#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Generate flip-books from videos and animated GIFs
#
# Copyright (c) 2016 Oliver Lau <ola@ct.de>, Heise Medien GmbH & Co. KG
# All rights reserved.

import string
from PIL import Image, ImageFont, ImageDraw, ImageColor
from fpdf import FPDF
from moviepy.editor import *


def mm2pt(mm):
    return 72 * mm / 2.54 / 10


def pt2mm(mm):
    return 2.54 * mm / 72 * 10


class Size:
    """ Class to store the size of a rectangle."""

    def __init__(self, width, height):
        self.width = width
        self.height = height

    def to_tuple(self):
        return self.width, self.height

    @staticmethod
    def from_tuple(sz):
        return Size(sz[0], sz[1])


class Point:
    """ Class to store a point on a 2D plane."""

    def __init__(self, x, y):
        self.x = x
        self.y = y

    @staticmethod
    def from_tuple(p):
        return Point(p[0], p[1])


class Margin:
    """ Class to store the margins of a rectangular boundary."""

    def __init__(self, top, right, bottom, left):
        self.top = top
        self.right = right
        self.bottom = bottom
        self.left = left


class Flipper:
    PAPER_SIZES = {
        'a5': Size(210, 148),
        'a4': Size(297, 210),
        'a3': Size(420, 297),
        'letter': Size(279.4, 215.9),
        'legal': Size(355.6, 215.9)
    }
    PAPER_CHOICES = PAPER_SIZES.keys()

    def __init__(self, **kwargs):
        self.video_file_name = kwargs.get('input')
        self.output_file_name = kwargs.get('output')
        self.frame_max_size = kwargs.get('frame_size', Size(40, 30))
        self.margins = kwargs.get('margin', Margin(10, 10, 10, 10))
        self.paper_format = kwargs.get('paper_format', 'a4')
        self.paper = self.PAPER_SIZES[string.lower(self.paper_format)]
        self.printable_area = Size(self.paper.width - self.margins.left - self.margins.right,
                                   self.paper.height - self.margins.top - self.margins.bottom)
        self.clip = VideoFileClip(self.video_file_name)
        self.frame_size = Size.from_tuple(self.clip.size)
        self.nx = int(self.printable_area.width / self.frame_max_size.width)
        self.ny = int(self.printable_area.height / self.frame_max_size.height)
        print 'FPS = {}, SIZE = {}x{}, xy = {}x{}'.format(
            self.clip.fps,
            self.frame_size.width, self.frame_size.height,
            self.nx, self.ny
        )
        self.pdf = FPDF(unit='mm', format=self.paper_format.upper(), orientation='L')
        self.pdf.set_compression(True)
        self.pdf.set_title('Funny video')
        self.pdf.set_author('Oliver Lau <ola@ct.de> - Heise Medien GmbH & Co. KG')
        self.pdf.set_creator('flippy')
        self.pdf.set_keywords('flip-book, video, animated GIF')

    def add_page(self):
        self.pdf.add_page()
        x0 = self.margins.left
        y0 = self.margins.top
        x1 = x0 + self.nx * self.frame_max_size.width
        y1 = y0 + self.ny * self.frame_max_size.height
        self.pdf.set_draw_color(0, 0, 0)
        self.pdf.set_line_width(pt2mm(0.1))
        for x in range(0, self.nx + 1):
            xx = x0 + x * self.frame_max_size.width
            self.pdf.line(xx, y0, xx, y1)
        for y in range(0, self.ny + 1):
            yy = y0 + y * self.frame_max_size.height
            self.pdf.line(x0, yy, x1, yy)

    def process(self):
        self.add_page()
        i = 0
        x = 0
        y = 0
        page = 0
        x0 = self.margins.left
        y0 = self.margins.top
        w = int(self.paper.width - self.margins.left - self.margins.right) / self.nx
        for frame in self.clip.iter_frames():
            temp_file = 'out/{}-{}-{}.jpg'.format(page, x, y)
            print temp_file
            im = Image.fromarray(frame)
            i += 1
            x += 1
            if x == self.nx:
                x = 0
                y += 1
                if y == self.ny:
                    y = 0
                    self.add_page()
                    page += 1
            im.save(temp_file)
            im.close()
            self.pdf.image(temp_file,
                           x=x0 + x * self.frame_max_size.width,
                           y=y0 + y * self.frame_max_size.height,
                           w=w)

        self.pdf.output(name=self.output_file_name)


def main():
    flipper = Flipper(input='samples/lemoncat.mp4', output='out/flip-book.pdf')
    flipper.process()

if __name__ == '__main__':
    main()


