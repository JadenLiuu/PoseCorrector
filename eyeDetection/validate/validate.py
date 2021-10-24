import cv2
import torch.hub
import os
from PIL import Image

from model.model import Model
from torchvision import transforms
from torchsummary import summary
from torchvision.transforms import ToTensor

DEVICE = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
CLASS_LABLES = ['Closed','Opened']
NUM_CLASSES = len(CLASS_LABLES)
INPUT_SHAPE = (28,24)


class Validation(object):
    Net = None
    def __init__(self, modelPath, doSummary=False) -> None:
        super().__init__()
        if Validation.Net is None:
            Validation.Net = Validation.load_model(modelPath, doSummary)
        
        self.transform = transforms.Compose([
            ToTensor(),
        ])
    
    def preprocess_image(self, img):
        img = cv2.resize(img, INPUT_SHAPE)
        img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        imgTensor = self.transform(img).to(DEVICE)
        return imgTensor

    def predict_one(self, img_path) -> str:
        img = cv2.imread(img_path)
        imgTensor = self.preprocess_image(img)
        imgTensor = imgTensor.unsqueeze(0)
        with torch.no_grad():
            res = Validation.Net(imgTensor)
            pred = torch.argmax(res.data).data
            return CLASS_LABLES[pred]

    @classmethod
    def load_model(cls, modelPath, doSummary):
        net = Model(num_classes=NUM_CLASSES)
        if torch.cuda.is_available():
            net = net.cuda()
        checkpoint = torch.load(os.path.join(modelPath), map_location=torch.device(DEVICE))
        net.load_state_dict(checkpoint['net'])
        net.eval()
        if doSummary:
            # print the model architecture and info with the given input shape
            summary(net, (1, INPUT_SHAPE[0], INPUT_SHAPE[1]))
        return net

if __name__ == '__main__':
    imgNames = ['open1.png','open2.png','open3.png','open4.png','open5.png']
    imgNames += ['close1.png', 'close2.png', 'close3.png']
    v = Validation('modelEye.t7', True)
    for imgName in imgNames:
        imgPath = os.path.join("./tests/", imgName)
        label = 0 if imgName.startswith("close") else 1
        labelStr = CLASS_LABLES[label]
        prediction = v.predict_one(imgPath)
        print(f"lable={labelStr}, predic={prediction}")
