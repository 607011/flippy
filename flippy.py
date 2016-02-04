#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Generate flip-books from videos and animated GIFs
#
# Copyright (c) 2016 Oliver Lau <ola@ct.de>, Heise Medien GmbH & Co. KG
# All rights reserved.

import string
import os
import sys
import argparse
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


class Margin:
    """ Class to store the margins of a rectangular boundary."""

    def __init__(self, top, right, bottom, left):
        self.top = top
        self.right = right
        self.bottom = bottom
        self.left = left


class FlipbookCreator:
    PAPER_SIZES = {
        'a5': Size(210, 148),
        'a4': Size(297, 210),
        'a3': Size(420, 297),
        'letter': Size(279.4, 215.9),
        'legal': Size(355.6, 215.9)
    }
    PAPER_CHOICES = PAPER_SIZES.keys()

    def __init__(self, **kwargs):
        self.verbosity = kwargs.get('verbosity', 0)
        self.input_file_name = kwargs.get('input')
        if self.verbosity > 0:
            print 'Opening {} ...'.format(self.input_file_name)
        self.clip = VideoFileClip(self.input_file_name)

    def process(self, **kwargs):
        output_file_name = kwargs.get('output')
        dpi = kwargs.get('dpi', 150)
        height_mm = float(kwargs.get('height', 50))
        margins = kwargs.get('margin', Margin(10, 10, 10, 10))
        paper_format = kwargs.get('paper_format', 'a4')
        paper = self.PAPER_SIZES[string.lower(paper_format)]
        printable_area = Size(paper.width - margins.left - margins.right,
                              paper.height - margins.top - margins.bottom)
        clip_size = Size.from_tuple(self.clip.size)
        frame_mm = Size(height_mm / clip_size.height * clip_size.width, height_mm)
        frame = Size(int(frame_mm.width / 25.4 * dpi),
                     int(frame_mm.height / 25.4 * dpi))
        nx = int(printable_area.width / frame_mm.width)
        ny = int(printable_area.height / frame_mm.height)
        frame_count = int(self.clip.duration * self.clip.fps)
        if self.verbosity > 0:
            print 'Input:  {} fps, {}x{}, {} frames'\
                '\n        from: {}'\
                .format(
                    self.clip.fps,
                    clip_size.width,
                    clip_size.height,
                    frame_count,
                    self.input_file_name
                )
            print 'Output: {}dpi, {}x{}, {:.2f}mm x {:.2f}mm, {}x{} tiles'\
                '\n        to: {}'\
                .format(
                    dpi,
                    frame.width, frame.height,
                    frame_mm.width, frame_mm.height,
                    nx, ny,
                    output_file_name
                )
        pdf = FPDF(unit='mm', format=paper_format.upper(), orientation='L')
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
        x0 = margins.left
        y0 = margins.top
        x1 = x0 + nx * frame_mm.width
        y1 = y0 + ny * frame_mm.height
        pdf.set_draw_color(128, 128, 128)
        pdf.set_line_width(0.1)
        for f in self.clip.iter_frames():
            ready = float(i + 1) / frame_count
            if self.verbosity:
                sys.stdout.write('\rProcessing frames |{:30}| {:}%'
                                 .format('X' * int(30 * ready), int(100 * ready)))
                sys.stdout.flush()
            temp_file = 'tmp-{}-{}-{}.jpg'.format(page, x, y)
            tmp_files.append(temp_file)
            im = Image.fromarray(f)
            im.thumbnail((frame.to_tuple()))
            i += 1
            x += 1
            if x == nx:
                x = 0
                y += 1
                if y == ny:
                    y = 0
                    for ix in range(0, nx + 1):
                        xx = x0 + ix * frame_mm.width
                        pdf.line(xx, y0, xx, y1)
                    for iy in range(0, ny + 1):
                        yy = y0 + iy * frame_mm.height
                        pdf.line(x0, yy, x1, yy)
                    pdf.add_page()
                    page += 1
            im.save(temp_file)
            pdf.image(temp_file,
                      x=x0 + x * frame_mm.width,
                      y=y0 + y * frame_mm.height,
                      w=frame_mm.width,
                      h=frame_mm.height)

        if self.verbosity > 0:
            print '\nGenerating PDF ...'
        pdf.output(name=output_file_name)
        if self.verbosity > 0:
            print 'Removing temporary files ...'
        for temp_file in tmp_files:
            os.remove(temp_file)


def main():
    parser = argparse.ArgumentParser(description='Generate flip-books from videos.')
    parser.add_argument('video', type=str, help='file name of video to process.')
    parser.add_argument('--out', type=str, help='name of PDF file to write to.', default='flip-book.pdf')
    parser.add_argument('--height', type=float, help='height of flip-book.', default=30)
    parser.add_argument('--paper', type=str, choices=FlipbookCreator.PAPER_CHOICES, help='paper size.', default='a4')
    parser.add_argument('--dpi', type=int, help='DPI', default=200)
    parser.add_argument('-v', type=int, help='verbosity level.', default=1)
    args = parser.parse_args()

    flippy = FlipbookCreator(
        input=args.video,
        verbosity=args.v)
    flippy.process(
        paper_format=args.paper,
        output=args.out,
        height=args.height,
        dpi=150)

if __name__ == '__main__':
    main()


