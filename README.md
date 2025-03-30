# FFProbe API

A lightweight API that accepts a URL and returns FFProbe data in JSON format.

## Requirements

- Python 3.8+
- FFmpeg/FFprobe
- Docker (optional)

## Local Development

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Make sure FFprobe is installed on your system:
   ```bash
   # On Ubuntu/Debian
   sudo apt-get install ffmpeg
   
   # On macOS with Homebrew
   brew install ffmpeg
   ```

3. Run the server:
   ```bash
   uvicorn main:app --reload
   ```

## Docker Deployment

1. Build the Docker image:
   ```bash
   docker build -t ffprobe-api .
   ```

2. Run the container:
   ```bash
   docker run -p 8000:8000 ffprobe-api
   ```

## API Usage

### Probe Media File

```bash
curl -X POST "http://127.0.0.1:8000/probe" \
     -H "Content-Type: application/json" \
     -d '{"url": "https://cdn.zappy.app/e9f24d32e2b0cdf9a7ecdf7fc11af34b.mp4"}'
```

### Health Check

```bash
curl "http://localhost:8000/health"
```

## Deployment to Render

1. Create a new Web Service on Render
2. Connect your repository
3. Choose "Docker" as the environment
4. Set the following:
   - Build Command: (leave empty, will use Dockerfile)
   - Start Command: (leave empty, will use CMD from Dockerfile)
5. Click "Create Web Service" 