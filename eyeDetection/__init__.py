from collections import namedtuple
from numpy.lib.function_base import average

_BoxLoc = namedtuple("BoxLoc", ['x1', 'y1', 'x2', 'y2'])


class DetectBox(object):
    def __init__(self, x1, y1, x2, y2) -> None:
        super().__init__()
        self._box_locations = _BoxLoc(x1, y1, x2, y2)

    def area(self) -> int:
        ydiff = self._box_locations.y2 - self._box_locations.y1
        xdiff = self._box_locations.x2 - self._box_locations.x1
        return xdiff * ydiff
    
    def getBox(self):
        x1, y1 = self._box_locations.x1, self._box_locations.y1
        x2, y2 = self._box_locations.x2, self._box_locations.y2
        return (x1, y1), (x2, y2)
    
    
class StableKeeper(object):
    """
        To maintain the size of detected faces, keep it from large variation
    """
    THRESH = 0.8
    N_KEEP = 3
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