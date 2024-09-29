from torchvision import datasets
from torchvision import transforms
import groundingdino.datasets.transforms as T
import os
from torch.utils.data import DataLoader
from lang_sam import LangSAM
import torch
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from torch.utils.data import Dataset
import json
import time
import gc
import lang_sam.utils as utils
from PIL import Image
from segment_anything.utils.transforms import ResizeLongestSide



from tqdm import tqdm

model = LangSAM()

H,W=600,800

root="train2017"
files=sorted(os.listdir(root))
with open("result.json","r") as f:
    json_dict=json.load(f)


new_dict={}
files_count=len(files)
i=10
subset=10000
begin=i*subset
end=begin+subset
for index in tqdm(range(begin,len(files))):
    image_pil=Image.open(root+"/"+files[index])
    image_pil=image_pil.resize((800,600))
    if image_pil.mode != "RGB":
        continue
    key=int(files[index].split(".")[0])
    if str(key) in json_dict.keys():
        new_dict[key]={}
        new_dict[key]["caption"]=json_dict[str(key)]["caption"]
        new_dict[key]["objects"]=json_dict[str(key)]["objects"]
        new_dict[key]["found_objects"]={}
        for object in json_dict[str(key)]["found_objects"].keys():
            
            box=torch.tensor(json_dict[str(key)]["found_objects"][object]["coords"])
            box_area=json_dict[str(key)]["found_objects"][object]["area"]
            masks=model.predict_sam(image_pil,box)
            masks = masks.squeeze(1)
            if len(masks)>0:
                mask_area=masks.sum()
                new_dict[key]["found_objects"][object]={"coords":box.tolist(),"box_area":box_area,"mask_area":mask_area.item()}
    with open(f"new_results{str(i)}.json","w") as f:
        r=json.dumps(new_dict)
        f.write(r)