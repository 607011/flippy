#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Generate flip-books from videos and animated GIFs
#
# Copyright (c) 2016 Oliver Lau <ola@ct.de>, Heise Medien GmbH & Co. KG
# All rights reserved.

import string, os
from PIL import Image
from fpdf import FPDF
from moviepy.editor import *


def mm2pt(mm):
    return 72 * mm / 2.54 / 10


def pt2mm(mm):
    return 2.54 * mm / 72 * 10


class Size:
    """ Class to store the size of a rectangle."""

    def __init__(self, width=0, height=0):
        self.width = width
        self.height = height

    def to_tuple(self):
        return self.width, self.height

    def aspect_ratio(self):
        return float(self.width) / float(self.height)

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
        dpi = kwargs.get('dpi', 300)
        height_mm = float(kwargs.get('height', 32))
        self.margins = kwargs.get('margin', Margin(10, 10, 10, 10))
        self.paper_format = kwargs.get('paper_format', 'a4')
        self.paper = self.PAPER_SIZES[string.lower(self.paper_format)]
        self.printable_area = Size(self.paper.width - self.margins.left - self.margins.right,
                                   self.paper.height - self.margins.top - self.margins.bottom)
        self.clip = VideoFileClip(self.video_file_name)
        frame = Size.from_tuple(self.clip.size)
        self.frame_mm = Size(height_mm / frame.height * frame.width, height_mm)
        self.frame = Size(int(self.frame_mm.width / 25.4 * dpi),
                          int(self.frame_mm.height / 25.4 * dpi))
        self.nx = int(self.printable_area.width / self.frame_mm.width)
        self.ny = int(self.printable_area.height / self.frame_mm.height)
        print 'FPS = {}, SIZE = {}x{}, dpi={}, SIZE = {}x{} {}x{}, tiles = {}x{}'.format(
            self.clip.fps,
            frame.width, frame.height,
            dpi,
            self.frame.width, self.frame.height,
            self.frame_mm.width, self.frame_mm.height,
            self.nx, self.ny
        )

    def process(self):
        pdf = FPDF(unit='mm', format=self.paper_format.upper(), orientation='L')
        pdf.set_compression(True)
        pdf.set_title('Funny video')
        pdf.set_author('Oliver Lau <ola@ct.de> - Heise Medien GmbH & Co. KG')
        pdf.set_creator('flippy')
        pdf.set_keywords('flip-book, video, animated GIF')
        pdf.add_page()
        tmp_files = []
        i = 0
        x = 0
        y = 0
        page = 0
        x0 = self.margins.left
        y0 = self.margins.top
        x1 = x0 + self.nx * self.frame_mm.width
        y1 = y0 + self.ny * self.frame_mm.height
        for frame in self.clip.iter_frames():
            temp_file = 'tmp-{}-{}-{}.jpg'.format(page, x, y)
            tmp_files.append(temp_file)
            print '{}@{}'.format(i, page),
            im = Image.fromarray(frame)
            im.thumbnail((self.frame.to_tuple()))
            i += 1
            x += 1
            if x == self.nx:
                x = 0
                y += 1
                if y == self.ny:
                    y = 0
                    pdf.add_page()
                    page += 1
            im.save(temp_file)
            im.close()
            pdf.image(temp_file,
                           x=x0 + x * self.frame_mm.width,
                           y=y0 + y * self.frame_mm.height,
                           w=self.frame_mm.width,
                           h=self.frame_mm.height)
            pdf.set_draw_color(128, 128, 128)
            pdf.set_line_width(0.1)
            for ix in range(0, self.nx + 1):
                xx = x0 + ix * self.frame_mm.width
                pdf.line(xx, y0, xx, y1)
            for iy in range(0, self.ny + 1):
                yy = y0 + iy * self.frame_mm.height
                pdf.line(x0, yy, x1, yy)

        pdf.output(name=self.output_file_name)
        print 'Removing temporary files ...'
        for temp_file in tmp_files:
            os.remove(temp_file)


def main():
    flipper = Flipper(input='samples/lemoncat.mp4', output='flip-book.pdf')
    flipper.process()

if __name__ == '__main__':
    main()


