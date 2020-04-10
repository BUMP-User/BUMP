import cv2
import pyqtgraph as pg

class ImageDisplay:

    def __init__(self, view_box, view, data_item, event_handler=None):
        self.view_box = view_box
        self.data_item = data_item
        self.view = view
        self.view.setCentralItem(self.view_box)
        self.view_box.setAspectLocked(True)
        self.view_box.addItem(self.data_item)
        # Contrast/color control
        self.hist = None
        self.event_handler = event_handler
        self.mouseMovedSignal = pg.SignalProxy(self.view_box.scene().sigMouseMoved, rateLimit=60, slot=self.mouseMoved)
        self.mouseClickedSignal = pg.SignalProxy(self.view_box.scene().sigMouseClicked, rateLimit=60, slot=self.mouseClicked)

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
        output = cv2.transpose(data)
        self.data_item.setImage(output, autoLevels=False, levels=scale, autoDownsample=True)

class ImageView:

    def __init__(self, image_view, event_handler=None):
        self.image_view = image_view
        self.event_handler = event_handler

    def draw(self, data, color_scale=255, size_scale=1):

        scale = [0, color_scale]
        output = cv2.transpose(data)
        self.image_view.setImage(output)

