import shutil #salvar arq no disco
from typing import List #lista de imagens
import os
from fastapi import FastAPI, UploadFile, File

from fastapi.responses import HTMLResponse #pagina

app = FastAPI()
#receber id img
#retornar csv final

@app.post("/obras/")
async def upload_images(files: List[UploadFile] = File(...)):
    #remover pasta com dados anteriores
    shutil.rmtree('api/img/')
    #criar a pasta api/img/
    mypath = 'api/img/'
    if not os.path.isdir(mypath):
        os.makedirs(mypath)

    for file in files:
        #salvar imagens na pasta "img/"
        with open(f'api/img/{file.filename}', "wb") as buffer:
            shutil.copyfileobj(file.file, buffer) 

    #rodar o modelo nas imgs baixadas
    os.system("python3 Framework.py --path api/img/  --single_folder True")
    
    #retornar arquivo csv
    f = open("api/img/predictions.csv","r")
    response = f.read()
    return {response}
    #return {"filename": "DEU"}

@app.post("/pavimento/")
async def upload_images(files: List[UploadFile] = File(...)):
    #remover pasta com dados anteriores
    shutil.rmtree('api/img_pavimento/')
    #criar a pasta api/img/
    mypath = 'api/img_pavimento/'
    if not os.path.isdir(mypath):
        os.makedirs(mypath)

    for file in files:
        #salvar imagens na pasta "img/"
        with open(f'api/img_pavimento/{file.filename}', "wb") as buffer:
            shutil.copyfileobj(file.file, buffer) 

    #rodar o modelo nas imgs baixadas
    os.system("python3 pavimentacao/mpmg_prediction.py --path api/img_pavimento")

    #f = open("api/img_pavimento/predictions.csv","r")
    #response = f.read()
    #return {response}
    return {"filename": "DEU"}

#chama o post
@app.get("/")
async def main():
    #os h1 são provisorios
    content = """
<body>
<h2>.</h2>
<h1>obras</h1>
<form action="/obras/" enctype="multipart/form-data" method="post">
    <input name="files" type="file" multiple>
    <input type="submit">
</form>
<h1>pavimentação</h1>
<form action="/pavimento/" enctype="multipart/form-data" method="post">
    <input name="files" type="file" multiple>
    <input type="submit">
</form>
</body>
    """
    return HTMLResponse(content=content)