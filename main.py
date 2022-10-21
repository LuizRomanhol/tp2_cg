from fastapi import FastAPI, File, UploadFile
from fastapi.responses import HTMLResponse
import cv2
import numpy as np

app = FastAPI()


def bts_to_img(bts):
    '''
    :param bts: results from image_to_bts
    '''
    buff = np.fromstring(bts, np.uint8)
    buff = buff.reshape(1, -1)
    img = cv2.imdecode(buff, cv2.IMREAD_COLOR)
    return img
    
@app.post("/files/")
async def create_files(
    files: list[bytes] = File(description="Multiple files as bytes"),
):
    for file in files:
        cv2.imwrite("download.jpg",bts_to_img(file))
        #print("formato da matrix")
        #print(bts_to_img(file).shape)
    return {"file_sizes": [len(file) for file in files]}


@app.get("/")
async def main():
    content = """
<body>
<form action="/files/" enctype="multipart/form-data" method="post">
<input name="files" type="file" multiple>
<input type="submit">
</form>
</body>
    """
    return HTMLResponse(content=content)
