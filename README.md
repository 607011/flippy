# flippy

Generate flip-books from videos and animated GIFs

## Prerequisites

 - Python 2.5 or later
 - Pillow 3.x
 - FPDF 1.7.x or later
 
## Download code

[Download flippy.py](https://raw.githubusercontent.com/ola-ct/flippy/master/flippy.py) from the
[flippy repository](https://github.com/ola-ct/flippy), or do

```
git clone https://github.com/ola-ct/flippy.git
```

to clone the repository into a local folder.

## Installation

### Windows

[Get Python 2.7.11](https://www.python.org/downloads/release/python-2711/) or later from
[python.org download page](https://www.python.org/downloads/).
Install Python into a folder of your choice, e.g. D:\Python27.

Then install the [Python Imaging Library](https://github.com/python-pillow/Pillow) and FPDF on the command line by typing:

```
D:\Python27\Scripts\pip.exe install Pillow fpdf
```

### Linux

Install Python 2.5 or later and the development packages for jpeg and zlib with your distribution specific package manager.

#### CentOS 7

Install required packages:

```
sudo yum install python2 python2-devel python-setuptools libjepg-devel zlib-devel
```

Then install the needed Python modules:

```
sudo pip install -r requirements.txt
```

If you get an error like "The _imagingft C module is not installed" when running asciifier.py, you have to reinstall Pillow:

```
sudo pip uninstall Pillow
sudo pip install Pillow
```


## Usage

### General usage

```
flippy.py 
  [-h] [--help]
  --out OUT
  --height HEIGHT
  --paper {a2,a3,a4,a5,letter,legal}
  --offset
  --dpi DPI
  --fps FPS
  IMAGE
```

`IMAGE`: filename of video or GIF image to be converted

`OUT`: name of file to write PDF to

`HEIGHT`: Height of flip-book (default: 30.0 mm)

`PAPER`: paper format (default: a3); only valid for PDF output

`OFFSET`: Margin left to each frame (default: 15.0 mm)
 
`DPI`: convert video/GIF to the given resolution in dots per inch (default: 200 dpi)
 
`FPS`: convert video/GIF to this many frames per second before PDF generation (default: 10 fps)
 
 ### Examples
 
 **to do**
 