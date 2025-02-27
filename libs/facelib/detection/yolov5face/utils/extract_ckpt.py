import torch
import sys, os
sys.path.insert(0,'./facelib/detection/yolov5face')
model = torch.load('facelib/detection/yolov5face/yolov5n-face.pt', map_location='cpu')['model']

import folder_paths
facedetection_model_dir = os.path.join(folder_paths.models_dir, "facedetection")

torch.save(model.state_dict(), facedetection_model_dir)