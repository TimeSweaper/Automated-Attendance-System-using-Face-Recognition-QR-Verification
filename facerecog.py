import os
import json
import io
from datetime import datetime
from PIL import Image
import torch
import torchvision.transforms as tv_transforms
from facenet_pytorch import MTCNN, InceptionResnetV1

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

def Face_Modals(device='cpu'):
    mtcnn = MTCNN(image_size=160, margin=20, keep_all=False, post_process=True, device=device)
    facenet = InceptionResnetV1(pretrained='vggface2').eval()
    return mtcnn, facenet

def saveAllignFace(aligned, out_path):
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
    return [float(x) for x in arr]

def saveEmbedding(studentID, studentName, embedding, out_path):
    data = {
        "student ID": str(studentID),
        "student Name": str(studentName),
        "model": "InceptionResnetV1_vggface2",
        "embedding_size": int(embedding.shape[0]),
        "embedding": EmbeddedVal(embedding)
    }
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def get_embedding_from_bytes(image_bytes, studentID=None, studentName=None, save_files=True, device='cpu'):
    """
    Accepts raw JPEG/PNG bytes, returns (aligned_path_or_None, embedding_list_or_None).
    """
    CreateDIR()
    mtcnn, facenet = Face_Modals(device=device)
    try:
        pil_img = Image.open(io.BytesIO(image_bytes)).convert('RGB')
    except Exception as e:
        print("Error loading image:", e)
        return None, None
    aligned = mtcnn(pil_img)
    if aligned is None:
        return None, None
    timestamp = datetime.utcnow().strftime('%Y%m%d%H%M%S%f')
    base = f"{studentName or 'unknown'}_{studentID or timestamp}"
    alignedPath = None
    if save_files:
        alignedPath = os.path.join(AlignedDIR, base + "_aligned.jpg")
        saveAllignFace(aligned, alignedPath)
    emb = getEmbedding(facenet, aligned)
    if save_files:
        jsonPath = os.path.join(EmbedDIR, base + "_embedding.json")
        saveEmbedding(studentID or '', studentName or '', emb, jsonPath)
    embList = EmbeddedVal(emb)
    return alignedPath, embList
