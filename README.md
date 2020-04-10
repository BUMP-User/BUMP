# BUMP Image
A GUI and command line tool for viewing and exporting images and associated data from BUMP camera *.bin files

# Installation
- Install and use Powershell: https://github.com/PowerShell/PowerShell
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
