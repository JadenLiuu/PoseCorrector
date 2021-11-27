import cv2
import torch.hub
import os
from PIL import Image
from torchvision import transforms
from torchsummary import summary
from torchvision.transforms import ToTensor
from eyeDetection.validate.model.model import Model

DEVICE = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
CLASS_LABLES = ['Closed','Opened']
NUM_CLASSES = len(CLASS_LABLES)
INPUT_SHAPE = (24,24)


class Validation(object):
    Net = None
    def __init__(self, modelPath, doSummary=False) -> None:
        super().__init__()
        if Validation.Net is None:
            Validation.Net = Validation.load_model(modelPath, doSummary)
            Validation.Net.zero_grad()
        
        self.transform = transforms.Compose([
            ToTensor(),
        ])
        self.ii = 0
    
    def preprocess_image(self, img):
        alpha = 1 # Contrast control
        beta = 0 # Brightness control
        img = cv2.resize(img, INPUT_SHAPE)
        img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        img = cv2.convertScaleAbs(img, alpha=alpha, beta=beta)
        # cv2.imwrite(f'tmp/12#{self.ii}.jpg', img)
        self.ii +=1
        imgTensor = self.transform(img).to(DEVICE)
        imgTensor = imgTensor.unsqueeze(0)
        return imgTensor

    def predict_one(self, img) -> int:
        imgTensor = self.preprocess_image(img)
        with torch.no_grad():
            res = Validation.Net(imgTensor)
            # print(res, torch.argmax(res.data).data)
            return torch.argmax(res.data).data

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
    from model.model import Model

    imgNames = os.listdir("./tests/")
    v = Validation('modelEye.t7', True)
    for imgName in imgNames:
        imgPath = os.path.join("./tests/", imgName)
        label = 0 if imgName.startswith("close") else 1
        labelStr = CLASS_LABLES[label]
        img = cv2.imread(imgPath)
        prediction = CLASS_LABLES[v.predict_one(img)]
        if prediction != labelStr:
            print(f"img: {imgName} lable={labelStr}, predic={prediction}")
