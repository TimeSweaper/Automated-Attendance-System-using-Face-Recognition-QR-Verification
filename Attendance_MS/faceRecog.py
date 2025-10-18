import os
import json
import cv2
import numpy as np
from PIL import Image

import torch
from facenet_pytorch import MTCNN, InceptionResnetV1
import torchvision.transforms as tv_transforms




FaceDIR = "face_data"
AlignedDIR = os.path.join(FaceDIR, "face_aligned")
EmbedDIR = os.path.join(FaceDIR, "embeddings")



def CreateDIR():
    if not os.path.exists(FaceDIR):
        os.makedirs(FaceDIR)
    
    if not os.path.exists(AlignedDIR):
        os.makedirs(AlignedDIR)
    
    if not os.path.exists(EmbedDIR):
        os.makedirs(EmbedDIR)



def Face_Modals():
    mtcnn = MTCNN(image_size=160, margin=20,keep_all=False,post_process=True,device='cpu')
    
    facenet = InceptionResnetV1(pretrained='vggface2').eval()
    
    return mtcnn, facenet



def CaptureImage():
    cap = cv2.VideoCapture(1)
    

    if not cap.isOpened():
        print("Webcam not aviable")
        return None

    print("Press C to Capture, Q to quit")
    frame_out = None

    while True:
        success,  frame = cap.read()
        if not success:
            continue

        cv2.putText(frame,text="Press C to Capture, Q to quit",org=(18,30),fontFace=cv2.FONT_HERSHEY_SIMPLEX, fontScale=0.7, color=(0,0,255),thickness=2,lineType=cv2.LINE_AA)
        cv2.imshow("Webcam", frame)

        key = cv2.waitKey(1) & 0xFF

        if key == ord('c'):
            frame_out = frame.copy()
            break
        if key == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()
    return frame_out



def Allign(mtcnn, bgr_frame):
    rgb = cv2.cvtColor(bgr_frame,cv2.COLOR_BGR2RGB)
    img = Image.fromarray(rgb)
    aligned = mtcnn(img)

    if aligned is None:
        print("No Face Detected")
        return None
    
    return aligned


def saveAllignFace(aligned,  out_path):
    to = tv_transforms.ToPILImage()
    img = to(aligned)
    img.save(out_path, format="JPEG", quality=95)


def getEmbedding(facenet, aligned):
    batch = aligned.unsqueeze(0)
    with torch.no_grad():
        Remb = facenet(batch)
    emb = Remb.squeeze(0).cpu().numpy()
    return emb




def EmbeddedVal(arr):
    Elist = []
    index = 0
    length = arr.shape[0]

    while index < length:
        value = float(arr[index])
        Elist.append(value)
        index = index + 1
    
    return Elist


def saveEmbedding(studentID, studentName, embedding, out_path):
    data = {}
    data["student ID"], data["student Name"] = str(studentID), str(studentName)
    data["model"],data["embedding_size"] = "InceptionResnetV1_vggface2", int(embedding.shape[0])
    data["embedding"] = EmbeddedVal(embedding)

    file = open(out_path, "w",encoding="utf-8")
    try:
        json.dump(data, file, ensure_ascii=False, indent=2)
    finally:
        file.close()





def capture_embed(studentID, studentName):
    CreateDIR()
    mtcnn,  facenet = Face_Modals()

    frame = CaptureImage()
    if frame is None:
        print("No frame capture")
        return None, None
    
    aligned = Allign(mtcnn, frame)
    if aligned is None:
        print("No Alligned face")
        return None, None
    
    base = str(studentName) + '_' +  str(studentID)
    alignedPath = os.path.join(AlignedDIR, base + "_aligned.jpg")
    saveAllignFace(aligned, alignedPath)

    emb = getEmbedding(facenet, aligned)
    jsonPath = os.path.join(EmbedDIR, base + "_embedding.json")
    saveEmbedding(studentID,studentName,emb,jsonPath)

    embList = EmbeddedVal(emb)
    return alignedPath,  embList