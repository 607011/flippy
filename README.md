# flippy

Generate flip-books from videos and animated GIFs

Published in [YouTube analog
Kinderleicht vom Video zum Daumenkino in vier Schritten (c't 11/2016 S. 140-142; c't 12/2016 S. 176-179)](https://www.heise.de/select/ct/2016/11/1463992613915244).

![grafik](https://user-images.githubusercontent.com/1151915/209465947-5e52a1ed-0630-4be1-bda6-92b053e54320.png)

## Prerequisites

 - Python 3 or later
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

### macOS

You want to install [Brew](https://brew.sh) package manager first:

```
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/master/install.sh)"
```

Then install pipenv to host a virtual environment:

```
brew install pipenv
```

Enter the project's directory and install the required modules into Pipenv's virtual environment:

```
cd flippy
pipenv install
```

You can now run flippy as shown below from inside the Pipenv shell (`pipenv shell`).

### Linux

Install [Pipenv](https://github.com/pypa/pipenv) with your distribution specific package manager.

Enter the project's directory and install the required modules into Pipenv's virtual environment:

```
cd flippy
pipenv install
```

You can now run flippy as shown below from inside the Pipenv shell (`pipenv shell`).

## Usage

### General usage

```
flippy.py 
  [-h] [--help]
  --input INPUT
  --output OUTPUT
  --height HEIGHT
  --paper {a2,a3,a4,a5,letter,legal}
  --offset
  --dpi DPI
  --fps FPS
```

`INPUT`: filename of video or GIF image to be converted

`OUTPUT`: name of file to write PDF to

`HEIGHT`: Height of flip-book (default: 30.0 mm)

`PAPER`: paper format (default: a3); only valid for PDF output

`OFFSET`: Margin left to each frame (default: 15.0 mm)
 
`DPI`: convert video/GIF to the given resolution in dots per inch (default: 200 dpi)
 
`FPS`: convert video/GIF to this many frames per second before PDF generation (default: 10 fps)
