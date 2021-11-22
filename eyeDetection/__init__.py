from collections import namedtuple
from numpy.lib.function_base import average

_BoxLoc = namedtuple("BoxLoc", ['x1', 'y1', 'x2', 'y2'])


class DetectBox(object):
    def __init__(self, x1, y1, x2, y2) -> None:
        super().__init__()
        self._boxLoc = _BoxLoc(x1, y1, x2, y2)

    def area(self) -> int:
        ydiff = self._boxLoc.y2 - self._boxLoc.y1
        xdiff = self._boxLoc.x2 - self._boxLoc.x1
        return xdiff * ydiff

    def zoomIn(self, ratiox, ratioy) -> None:
        w = self._boxLoc.x2 - self._boxLoc.x1
        h = self._boxLoc.y2 - self._boxLoc.y1
        x1 = int(self._boxLoc.x1 + w * (1.0-ratiox/2.0))
        x2 = int(self._boxLoc.x2 - w * (1.0-ratiox/2.0))
        y1 = int(self._boxLoc.y1 + h * (1.0-ratioy/2.0))
        y2 = int(self._boxLoc.y2 - h * (1.0-ratioy/2.0))
        self._boxLoc = _BoxLoc(x1, y1, x2, y2)

    def getBox(self):
        x1, y1 = self._boxLoc.x1, self._boxLoc.y1
        x2, y2 = self._boxLoc.x2, self._boxLoc.y2
        return (x1, y1), (x2, y2)

    def shrinkBack(self, ratio):
        x1 = int(self._boxLoc.x1 / ratio)
        x2 = int(self._boxLoc.x2 / ratio)
        y1 = int(self._boxLoc.y1 / ratio)
        y2 = int(self._boxLoc.y2 / ratio)
        self._boxLoc = _BoxLoc(x1, y1, x2, y2)

    def isEmpty(self) -> bool:
        return self._boxLoc.x1 == 0 and self._boxLoc.x2 == 0 \
            and self._boxLoc.y1 == 0 and self._boxLoc.y2 == 0
    
    
class StableKeeper(object):
    """
        To maintain the size of detected faces, keep it from large variation
    """
    THRESH = 0.8
    N_KEEP = 5
    def __init__(self) -> None:
        super().__init__()
        self.ls = []
        
    def keep(self, detect_box: DetectBox) -> DetectBox:
        if len(self.ls) < StableKeeper.N_KEEP:
            self.ls.append(detect_box)
        else:
            avg = average([i.area() for i in self.ls])
            area = detect_box.area()
            variation = abs(area - avg) / max(area, avg)
            if variation > StableKeeper.THRESH: ## unstable
                return self.ls[-1]
            else:
                self.ls.pop(0)
                self.ls.append(detect_box)
        return detect_box      