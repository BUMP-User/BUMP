# -*- coding: utf-8 -*-
"""
bump_image.py -- view and export images from BUMP bin files
Author Paul L. D. Roberts
Copyright 2020  Scripps Institution of Oceanography
Distributed under MIT license. See license.txt for more information.
"""

import os
import glob
import json
import time
import logging
import numpy as np
import pyqtgraph as pg
from pyqtgraph.Qt import QtCore, QtGui
from libs.logger import LOG, LOG_CONSOLE_HANDLER
from libs.display_tools import ImageDisplay
from libs.thread_tools import RawImageLoader, RawImageExporter
from libs.argparse_tools import parse_args


pg.mkQApp()

"""
Define main window class from template
The .ui file is created in Qt Designer and loaded
here. It must be on the same path as this file.
"""
path = os.path.dirname(os.path.abspath(__file__))
uiFile = os.path.join(path, 'bump_image.ui')
WindowTemplate, TemplateBaseClass = pg.Qt.loadUiType(uiFile)


class MainWindow(TemplateBaseClass):

    previousFrameSignal = QtCore.Signal(int)
    nextFrameSignal = QtCore.Signal(int)
    setFrameSignal = QtCore.Signal(int)

    def __init__(self, argv):

        self.filepath = None
        self.exportpath = None
        self.bindir = None
        self.all_bin_files = []
        self.playing = False


        self.captured_clicks = None

        self.frame_index = 0

        TemplateBaseClass.__init__(self)
        self.setWindowTitle('BUMP Image - Python - Qt')

        self.rawImageDisplayScale = 255
        self.lastImage = []
        self.rawFrames = []

        # Create the main window
        self.ui = WindowTemplate()
        self.ui.setupUi(self)

        self.raw_file_handler = None
        self.image_header = None
        self.image = None

        self.rawDataDisplay = None

        # setup handlers and events for UI
        self.set_ui_handlers()

        self.ui.playbackRate.setText('30.0')

        # timer used to play video, call playback in a separate thread
        self.playback_timer = QtCore.QTimer()
        self.playback_timer.timeout.connect(self.playback)

        ## build an initial namespace for console commands to be executed in (this is optional;
        ## the user can always import these modules manually)
        namespace = {'pg': pg, 'np': np}
        self.ui.pythonConsole.namespace=namespace

        # Show the main window
        self.show()

    def set_ui_handlers(self):
        # UI handlers
        self.ui.frameSelector.valueChanged.connect(self.ui.frameNumberSpinBox.setValue)
        self.ui.playButton.clicked.connect(self.togglePlay)
        self.ui.prevButton.clicked.connect(self.prevFrame)
        self.ui.nextButton.clicked.connect(self.nextFrame)
        self.ui.exportButton.clicked.connect(self.export_bin_file)
        self.ui.frameSelector.valueChanged.connect(self.setFrame)
        self.ui.playbackRate.editingFinished.connect(self.updatePlaybackRate)
        self.ui.rawDisplayScale.valueChanged.connect(self.setRawScale)

        # menu
        self.ui.actionOpen_File.triggered.connect(self.open_bin_file)
        self.ui.actionOpen_Directory.triggered.connect(self.open_dirs)

        self.ui.fileListComboBox.currentIndexChanged.connect(self.get_bin_file_from_dir)

    def open_dirs(self):

        dir_path = QtGui.QFileDialog.getExistingDirectory(self, 'Select Bin Directory',
                                                          'c:\\Users\\paul\\Downloads')

        if dir_path:
            self.bindir = dir_path

            self.all_bin_files = glob.glob(os.path.join(self.bindir, '**', '*.bin'), recursive=True)

            self.ui.fileListComboBox.clear()
            for bin_file in self.all_bin_files:
                self.ui.fileListComboBox.addItem(os.path.basename(bin_file))

    def get_bin_file_from_dir(self, file_index):

        if file_index < len(self.all_bin_files):
            file_path = self.all_bin_files[file_index]
            self.load_bin_file(file_path)

    def open_bin_file(self):
        file_path = QtGui.QFileDialog.getOpenFileName(self, 'Open Bin File',
                                                      'c:\\Users\\paul\\Downloads', "Bin files (*.bin)")
        if file_path:
            self.ui.fileListComboBox.clear()
            self.ui.fileListComboBox.addItem(os.path.basename(file_path[0]))
            self.load_bin_file(file_path[0])

    def export_bin_file(self):
        if self.filepath is not None:
            dir_path = QtGui.QFileDialog.getExistingDirectory(self, 'Select Export Directory',
                                                              os.path.dirname(self.filepath))
            if dir_path:
                LOG.info('Exporting: ' + self.filepath)
                raw_export = RawImageExporter(self.filepath, dir_path)
                self.exportpath = os.path.join(dir_path,os.path.basename(self.filepath)[:-4] + '.tiff')
                raw_export.start()
                raw_export.exportDone.connect(self.export_finished)

    def export_finished(self, done=True):
        if done and self.exportpath:
            ret = QtGui.QMessageBox.information(self, 'Bin File Export', 'Exported bin file to: ' + self.exportpath)

    def load_bin_file(self, file_path):

        print(file_path)

        if file_path:
            self.filepath = file_path
            LOG.info('File selected: ' + self.filepath)
            self.raw_file_handler = RawImageLoader(self.filepath)
            self.raw_file_handler.start()

            time.sleep(0.5)

            self.rawDataDisplay = ImageDisplay(pg.ViewBox(), self.ui.rawImageView)
            self.rawDataDisplay.line_tool.sigRegionChanged.connect(self.updateLine)

            self.setFrameIndex(0)

            self.ui.rawDisplayScale.setValue(np.max(self.image))
            self.drawRawFrame()

            # update file header info
            self.ui.fileInfo.clear()
            self.ui.fileInfo.insertPlainText(
                json.dumps(self.raw_file_handler.raw_image.file_header, indent=4)
            )

    def playback(self):
        self.setFrameIndex(self.frame_index+1)
        self.drawRawFrame()

    def setFrameIndex(self, index):

        self.frame_index = index % self.raw_file_handler.raw_image.frames_in_file
        if self.frame_index < 0:
            self.frame_index = 0
        # keep spingbox up to date with window
        self.ui.frameNumberSpinBox.setValue(self.frame_index)
        (self.image_header, self.image) = self.raw_file_handler.get_frame(int(self.frame_index))

    def updatePlaybackRate(self):
        if self.playing:
            self.playback_timer.stop()
            self.playback_timer.start(1000 / float(self.ui.playbackRate.text()))

    def togglePlay(self):
        if self.playing:
            self.playing = False
            self.ui.playButton.setStyleSheet("")
            self.playback_timer.stop()
        else:
            self.playing = True
            self.ui.playButton.setStyleSheet("background-color: #999;")
            self.playback_timer.start(1000/float(self.ui.playbackRate.text()))

    def setScale(self):
        self.rawImageDisplayScale = self.ui.rawDisplayScale.value()
        self.drawRawFrame()

    def setFrame(self):
        self.setFrameIndex(self.ui.frameSelector.value())
        self.drawRawFrame()

    def prevFrame(self):
        self.setFrameIndex(self.frame_index - 1)
        self.drawRawFrame()

    def nextFrame(self):
        self.setFrameIndex(self.frame_index + 1)
        self.drawRawFrame()

    def updateLine(self):
        line_data = self.rawDataDisplay.get_line(self.image)
        self.ui.linePlot.clear()
        self.ui.linePlot.plot(line_data[:, 0], pen='r')
        self.ui.linePlot.plot(line_data[:, 1], pen='b')
        self.ui.linePlot.plot(line_data[:, 2], pen='g')

    def drawRawFrame(self):
        self.rawDataDisplay.draw(self.image, self.ui.rawDisplayScale.value())
        self.ui.linePlot.clear()
        self.updateLine()
        # update frame info
        self.ui.frameInfo.clear()
        self.ui.frameInfo.insertPlainText(json.dumps(self.image_header, indent=4, sort_keys=True))

    def setRawScale(self, scale):
        self.rawDataDisplay.data_item.setLevels([0, scale])



###########################################################################
#  Main program
###########################################################################
## Start Qt event loop unless running in interactive mode or using pyside.
if __name__ == '__main__':
    import sys

    # check arguments first
    args = parse_args()

    if args.export:

        # elevate console log level
        LOG_CONSOLE_HANDLER.setLevel(logging.DEBUG)

        threads = []
        LOG.info('Exporting images, no GUI will be displayed.')
        for bin_file in glob.glob(os.path.join(args.export, '**', '*.bin'), recursive=True):
            LOG.info('Exporting: ' + bin_file)
            raw_export = RawImageExporter(bin_file, args.output_dir)
            raw_export.start()
            threads.append(raw_export)

        all_done = False
        while not all_done:
            for t in threads:
                if not t.isRunning():
                    all_done = True

    else:

        win = MainWindow(sys.argv)

        if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
            QtGui.QApplication.instance().exec_()