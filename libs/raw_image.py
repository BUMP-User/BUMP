# -*- coding: utf-8 -*-
"""
raw_image.py -- class to handle loading and exporting raw bin files from BUMP (PCAM) camera
Author Paul L. D. Roberts
Copyright 2020  Scripps Institution of Oceanography
Distributed under MIT license. See license.txt for more information.
"""

import os
import json
import struct
import datetime
import numpy as np
import pyqtgraph as pg
from tifffile import TiffWriter
from psutil import virtual_memory
from libs.logger import LOG


class RawImage:

    def __init__(self, filepath):

        self.filepath = filepath

        self.file_header_format = 'HHiHHffffffHHBBHHHiiii'
        self.file_header_params = [
            'length',
            'format',
            'camera_id',
            'pixel_format',
            'illumination_type',
            'flash_duration',
            'flash_delay',
            'exposure_time',
            'gain',
            'red_gain',
            'blue_gain',
            'vert_offset',
            'horz_offset',
            'vert_binning',
            'horz_binning',
            'binning_mode',
            'raw_image_height',
            'raw_image_width',
            'unused1',
            'unused2',
            'unused3',
            'unused4'
        ]

        self.frame_header_format = 'QQQIII'
        self.frame_header_params = [
            'unixtime',
            'system_micros',
            'camera_micros,',
            'frame_number',
            'width',
            'height'
        ]

        self.can_to_ram = False

        # lists for frame headers and data
        self.file_header_length = 0
        self.frame_header_size = 36
        self.file_header = None
        self.frame_headers = []
        self.frame_data = []

        # actual image width and height with raw size and binning
        self.img_width = 0
        self.img_height = 0

        # Try to open the file and read
        try:
            self.file_handle = open(self.filepath, "rb")
            self.file_valid = True
            self.file_size = os.path.getsize(self.filepath)
        except FileNotFoundError as e:
            LOG.error(e)
            self.file_valid = False

        # read the file header and set image sizes accordingly
        self.read_file_header()

        # check if we can load all frames into RAM
        self.ram_available = virtual_memory().available

        # Get the number of frames in the file
        self.frames_in_file = int((self.file_size - self.file_header_length) / self.frame_size_in_bytes())
        LOG.info('Found ' + str(self.frames_in_file) + ' frames in ' + self.filepath)

    def unpack(self, format_string, names, raw_data):

        data = struct.unpack(format_string, raw_data)
        output = {}

        for ind, d in enumerate(data):
            output[names[ind]] = d

        return output

    def export_as_tiff(self, output_path=None):
        file_info = {}
        file_info['file_header'] = self.file_header
        file_info['frame_headers'] = []

        if output_path is None:
            tiff_path = self.filepath[:-4] + '.tiff'
            json_path = self.filepath[:-4] + '.json'
        else:
            tiff_path = os.path.join(output_path, os.path.basename(self.filepath)[:-4]) + '.tiff'
            json_path = os.path.join(output_path, os.path.basename(self.filepath)[:-4]) + '.json'

        with TiffWriter(tiff_path, append=True) as tif:

            for i in range(0, self.frames_in_file):
                header, data = self.read_frame(i)
                timestamp = float(header['system_micros']) / 1000000
                dt = datetime.datetime.fromtimestamp(int(timestamp))
                file_info['frame_headers'].append(header)
                frame_header_string = json.dumps(header)
                xtag = (65000, 's', 0, frame_header_string, False)
                tif.save(
                    data,
                    description=json.dumps(file_info),
                    datetime=dt,
                    extratags=[xtag]
                )

        with open(json_path, "w") as f:
            json.dump(file_info, f, indent=4, sort_keys=True)

    def read_file_header(self):

        if self.file_valid:

            self.file_handle.seek(0)
            res = self.file_handle.read(2)
            self.file_header_length = struct.unpack('H', res)[0]

            # read the rest of the header
            self.file_handle.seek(0)
            res = self.file_handle.read(self.file_header_length)
            self.file_header = self.unpack(self.file_header_format, self.file_header_params, res)

            self.img_height = int(self.file_header['raw_image_height'] / self.file_header['vert_binning'])
            self.img_width = int(self.file_header['raw_image_width'] / self.file_header['horz_binning'])

    def frame_size_in_bytes(self):

        bpp = self.file_header['pixel_format']

        return self.frame_header_size + bpp * self.img_width*self.img_height

    def frame_pixels(self):

        return self.img_width*self.img_height

    def read_frame(self, index):

        frame_offset = self.file_header_length + index * self.frame_size_in_bytes()
        bpp = self.file_header['pixel_format']
        frame_pixels = self.frame_pixels()

        if self.file_valid:

            # seek to the start of the frame
            self.file_handle.seek(frame_offset, 0)

            # read the header
            frame_header = self.unpack(
                self.frame_header_format,
                self.frame_header_params,
                self.file_handle.read(self.frame_header_size)
            )

            # read the frame pixels
            if bpp == 1:
                res = np.fromfile(self.file_handle, dtype='uint8', count=frame_pixels)
            else:
                res = np.fromfile(self.file_handle, dtype='uint16', count=frame_pixels)
            if len(res) <= 0:
                LOG.error('Error reading frame ' + str(index) + " from file " + self.filepath)
                return None
            else:
                # reshape into image
                image = np.reshape(res, (self.img_height, self.img_width))
                return frame_header, image
