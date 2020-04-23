# BUMP Image
A GUI and command line tool for viewing and exporting images and associated data from BUMP camera *.bin files

## Installation

- (Windows) Install and use Powershell: https://github.com/PowerShell/PowerShell
- Install Miniconda: https://docs.conda.io/en/latest/miniconda.html
- Create a new virtual environment to work in
```bash
$ cd SIO_BUMP
$ mkdir software
$ cd software
$ python -m venv venv_BUMP
```
- On Windows
```bash
$ venv_BUMP\scripts\activate.ps1
```
- On Mac or Linux
```bash
$ source venv_BUMP/scripts/activate
```
- Install python packages
```bash
$ pip install pyqt5
$ pip install pyqtgraph
$ pip install opencv-python
$ pip install psutil
$ pip install tifffile
```

## Usage Examples

The tool provides two ways to work with bin files from the BUMP instrument. The first
is to load the GUI and open either a bin file or directory of bin files:

```bash
$ python bump_image.py
```

This will load the Qt GUI. From there, select File->Open File to load a bin file.

Alternatively, one can simply export images from bin files from the command line. In
this case, the `--export` flag can be used along with a path to a directory of bin
files. For example:

```bash
$ python bump_image.py --export c:\Users\paul\Data
```

In that case above, multipage Tiff files will be exported to the same location as the
bin files. If we want to use a different location:

```bash
$ python bump_image.py --export c:\Users\paul\Data --output_dir c:\Users\paul\Desktop
```

and images will be exported to the path given to --output_dir.

## Interacting with the GUI

The GUI uses PyQt (https://riverbankcomputing.com/software/pyqt/intro) 
to provide UI widgets to control its behavior and pyqtgraph (http://www.pyqtgraph.org/) 
for image display with zoom, pan, and color scale controls.

The File menu has two options for loading bin files:

* **Open File**         : Open a single bin file and display the first frame
* **Open Directory**    : Walk a directory and list all bin files

When a file is opened, the bin file name is placed in the File List dropdown,
the bin file is loaded, and the first frame is displayed.

When a directory is opened, bin files names appear in the File List dropdown
and selecting a name will case the bin file to be loaded and the first frame
displayed.

### Navigating the bin file

When a bin file is loaded, the `Play`, `Previous`, `Next`, and slider control 
the framin the bin file that is displayed in the image view. The **File Header** 
text view shows the parsed header for the file, and the **Frame Header** text view
shows the header for the displayed frame.

### Display scaling

The app currently sets the 8-bit color scale for the image based on the maximum
pixel intensity in the first frame of the file. This scale can be easily changed 
by dragging the **Display Scale** slider or entering a number between 0-255. 

For speed, the displayed image is resized to a lower resolution depending on the
raw data size. In most cases, this means the image will be downsampled to a height
of 1080.

### Exporting bin files

Currently, only a full bin file export is supported. When clicking the `Export` button,
a directory selection dialog will appear and you must select the location 
to export the bin file to. After selecting this, the exporter thread will save a 
multipage Tiff file with header information saved in the Tiff Metadata 
and also in an JSON file with the same name.


