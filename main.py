from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, HttpUrl
import subprocess
import json
import tempfile
import aiohttp
import os
from typing import Optional
import shutil
from urllib.parse import urlparse, urlunparse

app = FastAPI(title="FFProbe API")

class URLInput(BaseModel):
    url: HttpUrl

def normalize_url(url: str) -> str:
    """Normalize URL by removing double slashes in the path."""
    parsed = urlparse(str(url))
    # Reconstruct the URL with normalized path
    return urlunparse((
        parsed.scheme,
        parsed.netloc,
        parsed.path.replace('//', '/'),
        parsed.params,
        parsed.query,
        parsed.fragment
    ))

async def download_file(url: str) -> str:
    # Create a temporary file
    temp_file = tempfile.NamedTemporaryFile(delete=False)
    temp_filename = temp_file.name
    
    # Normalize the URL
    normalized_url = normalize_url(url)
    
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(normalized_url) as response:
                if response.status != 200:
                    raise HTTPException(
                        status_code=400, 
                        detail=f"Could not download file. Status code: {response.status}"
                    )
                
                # Stream the file to disk
                with open(temp_filename, 'wb') as f:
                    while True:
                        chunk = await response.content.read(8192)
                        if not chunk:
                            break
                        f.write(chunk)
        except aiohttp.ClientError as e:
            raise HTTPException(
                status_code=400,
                detail=f"Failed to download file: {str(e)}"
            )
    
    return temp_filename

@app.post("/probe")
async def probe_media(input: URLInput):
    try:
        # Check if ffprobe is installed
        if not shutil.which('ffprobe'):
            raise HTTPException(
                status_code=500,
                detail="ffprobe is not installed on the system"
            )
        
        # Download the file
        temp_file = await download_file(str(input.url))
        
        try:
            # Run ffprobe
            cmd = [
                'ffprobe',
                '-v', 'quiet',
                '-print_format', 'json',
                '-show_format',
                '-show_streams',
                temp_file
            ]
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True
            )
            
            if result.returncode != 0:
                raise HTTPException(
                    status_code=400,
                    detail="Failed to analyze media file"
                )
            
            # Parse the JSON output
            probe_data = json.loads(result.stdout)
            
            return probe_data
            
        finally:
            # Clean up the temporary file
            try:
                os.unlink(temp_file)
            except:
                pass
                
    except json.JSONDecodeError:
        raise HTTPException(
            status_code=500,
            detail="Failed to parse ffprobe output"
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )

@app.get("/health")
async def health_check():
    return {"status": "healthy"} 