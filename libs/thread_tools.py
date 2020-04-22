from pyqtgraph.Qt import QtCore
import pyqtgraph as pg
from libs.raw_image import RawImage
from libs.logger import LOG
import multiprocessing
import time
import cv2

class RawImageExporter(QtCore.QThread):

    exportDone = QtCore.Signal(bool)

    def __init__(self, bin_path, output_path=None):
        QtCore.QThread.__init__(self)
        self.bin_path = bin_path
        self.output_path = output_path

    def __del__(self):
        self.wait()

    def run(self):

        rw = RawImage(self.bin_path)
        rw.export_as_tiff(output_path=self.output_path)
        self.exportDone.emit(True)
        self.deleteLater()


class RawImageLoader(QtCore.QThread):

    # signals
    #rawFrame = QtCore.Signal(object)
    imagesLoaded = QtCore.Signal(float)
    loadingDone = QtCore.Signal(bool)
    setRawFrames = QtCore.Signal(object)

    def __init__(self, bin_path, pycon=None):
        QtCore.QThread.__init__(self)
        self.bin_path = bin_path
        self.bin_loaded = False
        self.playing = False
        self.frame_rate = 30
        self.frame_index = 0
        self.last_displayed_index = 0
        self.raw_image = None

        self.raw_image = RawImage(self.bin_path)
        self.frame_header = []
        self.frame_data = []
        self.display_data = []

        for ind in range(0, self.raw_image.frames_in_file):
            self.frame_header.append(None)
            self.frame_data.append(None)
            self.display_data.append(None)

    def __del__(self):
        self.wait()

    def get_frame(self, index):
        if index < self.raw_image.frames_in_file:
            while self.frame_header[index] is None:
                time.sleep(0.1)
                LOG.info('Waiting for frame: ' + str(index) + '...')

            return self.frame_header[index], self.display_data[index]
        else:
            LOG.error('Frame index ' + str(index) + ' is out of bounds [0,' + str(self.raw_image.frames_in_file) + ']')

    def run_load_frames(self):
        index = 0

        while index < self.raw_image.frames_in_file:
            if self.frame_header[index] is None:
                (self.frame_header[index], self.frame_data[index]) = self.raw_image.read_frame(index)
                #TODO: add controls from UI to adjust color and resolution conversion
                if self.raw_image.file_header['pixel_format'] == 2:
                    image = (self.frame_data[index] / 256).astype('uint8')
                image = cv2.cvtColor(image, cv2.COLOR_BayerRG2BGR)
                scale = 1080/image.shape[0]
                image = cv2.resize(image, (int(image.shape[1]*scale), int(image.shape[0]*scale)))
                self.display_data[index] = image
            index += 1
            LOG.info('Loading frame: ' +str(index) + '...')
        self.bin_loaded = True
        self.loadingDone.emit(True)

    def run(self):

        while self.isRunning:

            if not self.bin_loaded:
                self.run_load_frames()

            time.sleep(0.1)
