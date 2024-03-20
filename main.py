import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from io import BytesIO
from fastapi.responses import StreamingResponse

app = FastAPI()

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get('/')
def index():
    return {'info': 'Welcome to the API'}

@app.get('/file_count')
async def file_count(directory: str):
    try:
        file_list = os.listdir(directory)
        file_count = len(file_list)
        return {"file_count": file_count}
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Directory not found")

@app.get('/vidsrc/{dbid}')
async def vidsrc(dbid:str,s:int=None,e:int=None):
    if dbid:
        return await vidsrctoget(dbid,s,e)
    else:
        raise HTTPException(status_code=400, detail=f"Invalid id: {dbid}")

@app.get('/vsrcme/{dbid}')
async def vsrcme(dbid:str = '',s:int=None,e:int=None,l:str='eng'):
    if dbid:
        return await vidsrcmeget(dbid,s,e)
    else:
        raise HTTPException(status_code=400, detail=f"Invalid id: {dbid}")

@app.get("/subs")
async def subs(url: str):
    try:
        response = requests.get(url)
        response.raise_for_status()  # Raise HTTPError for bad responses

        with gzip.open(BytesIO(response.content), 'rt', encoding='utf-8') as f:
            subtitle_content = f.read()

        async def generate():
            yield subtitle_content.encode("utf-8")

        return StreamingResponse(generate(), media_type="application/octet-stream", headers={"Content-Disposition": "attachment; filename=subtitle.srt"})

    except requests.exceptions.RequestException as e:
        raise HTTPException(status_code=500, detail=f"Error fetching subtitle: {e}")

    raise HTTPException(status_code=404, detail="Subtitle not found")

@app.get('/info')
async def vidsrc():
    return {'info':'This api is a fork of api written by github.com/cool-dev-guy.'}

if __name__ == '__main__':
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", 8000))
    import uvicorn
    uvicorn.run(app, host=host, port=port)
