#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Daumenkinos aus Videos und animierten GIFs herstellen
#
# Copyright (c) 2016 Oliver Lau <ola@ct.de>, Heise Medien GmbH & Co. KG
# Alle Rechte vorbehalten.

import os
import sys
import argparse
from PIL import Image, GifImagePlugin
from fpdf import FPDF
from moviepy.editor import *


class Size:
    """ Class to store the size of a rectangle """

    def __init__(self, width=0, height=0):
        self.width = width
        self.height = height

    def to_tuple(self):
        return self.width, self.height

    def __str__(self):
        return 'Size({}x{})'.format(self.width, self.height)

    @staticmethod
    def from_tuple(sz):
        return Size(sz[0], sz[1])


class Point:
    """ Class to store a point on a 2D plane """

    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __str__(self):
        return 'Point({}, {})'.format(self.x, self.y)


class Margin:
    """ Class to store the margins of a rectangular boundary """

    def __init__(self, top, right, bottom, left):
        self.top = top
        self.right = right
        self.bottom = bottom
        self.left = left

    def __str__(self):
        return 'Margin({}, {}, {}, {})'.format(self.topx, self.right, self.bottom, self.left)


class AnimatedGif:
    """ Generator for a sequence of Image objects from an animated GIF """

    def __init__(self, im):
        self.im = im

    def __getitem__(self, ix):
        try:
            if ix:
                self.im.seek(ix)
            return self.im
        except EOFError:
            raise IndexError

    def open(self, file_name):
        self.im = Image.open(file_name)


class FlipbookCreator:
    PAPER_SIZES = {
        'a5': Size(210, 148),
        'a4': Size(297, 210),
        'a3': Size(420, 297),
        'letter': Size(279.4, 215.9),
        'legal': Size(355.6, 215.9)
    }
    PAPER_CHOICES = PAPER_SIZES.keys()

    def __init__(self, verbosity=0, input_file_name=''):
        self.verbosity = verbosity
        self.input_file_name = input_file_name
        self.frames = None
        self.clip = None
        if self.input_file_name.endswith('.gif'):
            self.im = Image.open(self.input_file_name)
            self.palette = self.im.getpalette()
            self.frames = AnimatedGif(self.im)
            self.frame_count = len(list(AnimatedGif(self.im)))
            self.fps = 0
            self.last_im = Image.new('P', self.im.size)
            for i in range(0, 2):
                for f in AnimatedGif(self.im):
                    self.last_im.putpalette(self.palette)
                    im = self.last_im.copy()
                    im.paste(f)
                    self.last_im = im.copy()
        else:
            self.clip = VideoFileClip(self.input_file_name)
            self.fps = self.clip.fps
            self.frame_count = int(self.clip.duration * self.clip.fps)
        if self.verbosity > 0:
            print ('Oeffnen von {} ...'.format(self.input_file_name))

    def process(
        self,
        output_file_name=None,
        dpi=150,
        offset=0,
        fps=10,
        height_mm=50,
        margins=Margin(10, 10, 10, 10),
        paper_format='a4'
    ):

        def draw_raster():
            for ix in range(0, nx + 1):
                xx = x0 + ix * total.width
                pdf.line(xx, y0, xx, y1)
                if offset > 0 and ix != nx:
                    pdf.line(xx + offset, y0, xx + offset, y1)
            for iy in range(0, ny + 1):
                yy = y0 + iy * total.height
                pdf.line(x0, yy, x1, yy)

        height_mm = float(height_mm)
        tmp_files = []
        if self.clip:
            if fps != self.clip.fps:
                if self.verbosity > 0:
                    print ('Transkodierung von {} fps nach {} fps ...'.format(self.clip.fps, fps))
                self.clip.write_videofile('tmp.mp4', fps=fps, audio=False)
                tmp_files.append('tmp.mp4')
                self.clip = VideoFileClip('tmp.mp4')
                self.fps = self.clip.fps
                self.frame_count = int(self.clip.duration * self.fps)
            clip_size = Size.from_tuple(self.clip.size)
        elif self.frames:
            clip_size = Size.from_tuple(self.im.size)

        paper = self.PAPER_SIZES[paper_format.lower()]
        printable_area = Size(paper.width - margins.left - margins.right,
                              paper.height - margins.top - margins.bottom)
        frame_mm = Size(height_mm / clip_size.height * clip_size.width, height_mm)
        total = Size(offset + frame_mm.width, frame_mm.height)
        frame = Size(int(frame_mm.width / 25.4 * dpi),
                     int(frame_mm.height / 25.4 * dpi))
        nx = int(printable_area.width / total.width)
        ny = int(printable_area.height / total.height)
        if self.verbosity > 0:
            print ('Eingabe:  {} fps, {}x{}, {} Einzelbilder'
                   '\n        von: {}'
                   .format(
                       self.fps,
                       clip_size.width,
                       clip_size.height,
                       self.frame_count,
                       self.input_file_name
                   ))
            print ('Ausgabe: {}dpi, {}x{}, {:.2f}mm x {:.2f}mm, {}x{} Kacheln'
                   '\n        nach: {}'
                   .format(
                       dpi,
                       frame.width, frame.height,
                       frame_mm.width, frame_mm.height,
                       nx, ny,
                       output_file_name
                   ))
        pdf = FPDF(unit='mm', format=paper_format.upper(), orientation='L')
        pdf.set_compression(True)
        pdf.set_title('Lustiges Daumenkino')
        pdf.set_author('Oliver Lau <ola@ct.de> - Heise Medien GmbH & Co. KG')
        pdf.set_creator('flippy')
        pdf.set_keywords('Daumenkino, Video, Animiertes GIF')
        pdf.set_draw_color(128, 128, 128)
        pdf.set_line_width(0.1)
        pdf.set_font('Helvetica', '', 12)
        pdf.add_page()
        i = 0
        page = 0
        tx, ty = -1, 0
        x0, y0 = margins.left, margins.top
        x1, y1 = x0 + nx * total.width, y0 + ny * total.height

        if self.clip:
            all_frames = self.clip.iter_frames()
        elif self.frames:
            all_frames = AnimatedGif(self.im)
        else:
            all_frames = []
        for f in all_frames:
            ready = float(i + 1) / self.frame_count
            if self.verbosity:
                sys.stdout.write('\rVerarbeiten der Einzelbilder |{:30}| {}%'
                                 .format('X' * int(30 * ready), int(100 * ready)))
                sys.stdout.flush()
            tx += 1
            if type(f) == GifImagePlugin.GifImageFile:
                f.putpalette(self.palette)
                self.last_im.paste(f)
                im = self.last_im.convert('RGBA')
            else:
                im = Image.fromarray(f)
                im.thumbnail(frame.to_tuple())
            if tx == nx:
                tx = 0
                ty += 1
                if ty == ny:
                    ty = 0
                    draw_raster()
                    pdf.add_page()
                    page += 1
            temp_file = 'tmp-{}-{}-{}.jpg'.format(page, tx, ty)
            im.save(temp_file)
            tmp_files.append(temp_file)
            x = x0 + tx * total.width
            y = y0 + ty * total.height
            pdf.image(temp_file,
                      x=x + offset,
                      y=y,
                      w=frame_mm.width,
                      h=frame_mm.height)
            text = Point(x, y + frame_mm.height - 2)
            if offset > 0:
                pdf.rotate(90, text.x, text.y)
                pdf.text(text.x, text.y + 5, '{}'.format(i))
                pdf.rotate(0)
            i += 1

        if y != 0 and x != 0:
            draw_raster()

        if self.verbosity > 0:
            print ('\nGenerieren des PDFs ...')
        pdf.output(name=output_file_name)
        if self.verbosity > 0:
            print ('Entfernen temporaerer Dateien ...')
        for temp_file in tmp_files:
            os.remove(temp_file)


def main():
    parser = argparse.ArgumentParser(description='Daumenkinos aus Videos erzeugen.')
    parser.add_argument('--input', type=str, help='Name der Video-/GIF-Datei, die verarbeitet werden soll')
    parser.add_argument('--output', type=str, help='Name der PDF-Datei', default='flip-book.pdf')
    parser.add_argument('--height', type=float, help='Hoehe des Daumenkinos [mm]', default=30)
    parser.add_argument('--paper', type=str, choices=FlipbookCreator.PAPER_CHOICES, help='Papierformat', default='a4')
    parser.add_argument('--offset', type=float, help='Breite des linken Randes [mm]', default=15.0)
    parser.add_argument('--dpi', type=int, help='DPI', default=200)
    parser.add_argument('--fps', type=int, help='Bilder pro Sekunde', default=10)
    parser.add_argument('--license', nargs='?', const=True, help='Lizenz anzeigen')
    parser.add_argument('-v', type=int, nargs='?', help='Ausgabedetailstufe (Vorgabe: 1)', default=1)
    args = parser.parse_args()

    if args.license:
        print ('\n'
               'Flippy - Daumenkinos aus Videos und GIFs herstellen.\n\n'
               'Copyright (c) 2016 Oliver Lau, Heise Medien GmbH & Co. KG.\n\n'
               'Dieses Programm ist freie Software. Sie koennen es unter den Bedingungen der '
               'GNU General Public License, wie von der Free Software Foundation veroeffentlicht, '
               'weitergeben und/oder modifizieren, entweder gemaess Version 3 der Lizenz oder '
               '(nach Ihrer Wahl) jeder spaeteren Version.\n\n'
               'Die Veroeffentlichung dieses Programms erfolgt in der Hoffnung, dass es Ihnen '
               'von Nutzen sein wird, aber OHNE JEDWEDE GARANTIE, auch ohne die implizite '
               'Garantie der MARKTREIFE oder der VERWENDBARKEIT FUER EINEN BESTIMMTEN ZWECK. '
               'Details finden Sie in der GNU General Public License.\n\n'
               'Sie sollten ein Exemplar der GNU General Public License zusammen mit diesem '
               'Programm erhalten haben. Falls nicht, siehe <http://www.gnu.org/licenses/>.\n\n'
               'Fuer mehr Informationen siehe <https://github.com/ola-ct/flippy>')
        sys.exit(0)

    flippy = FlipbookCreator(
        input_file_name=args.input,
        verbosity=args.v)
    flippy.process(
        paper_format=args.paper,
        output_file_name=args.output,
        height_mm=args.height,
        dpi=args.dpi,
        offset=args.offset)

if __name__ == '__main__':
    main()
