import cv2 as cv

def draw_str(img, pos, s, color=(0, 255, 0), scale=0.5, thickness=1):
    """Draw a string on the image."""
    cv.putText(img, s, pos, cv.FONT_HERSHEY_SIMPLEX, scale, color, thickness)

class RectSelector:
    """Simple rectangle selector using mouse events."""
    def __init__(self, window_name, onrect):
        self.window_name = window_name
        self.onrect = onrect
        cv.namedWindow(window_name)
        cv.setMouseCallback(window_name, self.onmouse)
        self.drag_start = None
        self.rect = None

    def onmouse(self, event, x, y, flags, param):
        if event == cv.EVENT_LBUTTONDOWN:
            self.drag_start = (x, y)
        elif event == cv.EVENT_LBUTTONUP:
            self.rect = (self.drag_start[0], self.drag_start[1], x, y)
            self.onrect(self.rect)
            self.drag_start = None

    def draw(self, img):
        if self.drag_start:
            x1, y1 = self.drag_start
            x2, y2 = cv.getWindowImageRect(self.window_name)[2:]
            cv.rectangle(img, (x1, y1), (x2, y2), (0, 255, 0), 2)
