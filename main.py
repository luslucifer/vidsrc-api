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

# Your other endpoints go here

if __name__ == '__main__':
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", 8000))
    import uvicorn
    uvicorn.run(app, host=host, port=port)
