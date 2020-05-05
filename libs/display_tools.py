import cv2
import numpy as np
import pyqtgraph as pg

pg.setConfigOptions(imageAxisOrder='row-major')

class ImageDisplay:

    def __init__(self, view_box, view, event_handler=None):
        self.view_box = view_box
        self.data_item = pg.ImageItem()
        self.view = view
        self.view.setCentralItem(self.view_box)
        self.view_box.setAspectLocked(True)
        self.line_tool = pg.LineSegmentROI([(10, 10), (10, 100)])
        self.view_box.addItem(self.line_tool)
        self.view_box.addItem(self.data_item)
        # Contrast/color control
        self.hist = None
        self.event_handler = event_handler
        self.mouseMovedSignal = pg.SignalProxy(self.view_box.scene().sigMouseMoved, rateLimit=60, slot=self.mouseMoved)
        self.mouseClickedSignal = pg.SignalProxy(self.view_box.scene().sigMouseClicked, rateLimit=60, slot=self.mouseClicked)

    def get_line(self, image):

        return self.line_tool.getArrayRegion(image, self.data_item)


    def mouseClicked(self, evt):
        pos = evt[0].pos()
        if self.view_box.sceneBoundingRect().contains(pos):
            mousePoint = self.view_box.mapSceneToView(pos)
            if self.event_handler is not None:
                self.event_handler([mousePoint.x(), mousePoint.y()])

    def mouseMoved(self, evt):
        pos = evt[0]
        if self.view_box.sceneBoundingRect().contains(pos):
            mousePoint = self.view_box.mapSceneToView(pos)


    def draw(self, data, color_scale=255, size_scale=1):

        scale = [0, color_scale]
        data = np.flipud(data)
        self.data_item.setImage(data, autoLevels=False, levels=scale, autoDownsample=True)

class ImageView:

    def __init__(self, image_view, event_handler=None):
        self.image_view = image_view
        self.event_handler = event_handler

    def draw(self, data, color_scale=255, size_scale=1):

        scale = [0, color_scale]
        output = cv2.transpose(data)
        self.image_view.setImage(output)

