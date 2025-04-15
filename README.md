# Soyabean Disease Detection API

This API provides endpoints for detecting diseases in soyabean plants using a deep learning model.

## Setup

1. Clone the repository:
```bash
git clone https://github.com/TheAryan77/soyabean_api.git
cd soyabean_api
```

2. Create a virtual environment and install dependencies:
```bash
python -m venv venv
source venv/bin/activate  # On Windows use: venv\Scripts\activate
pip install -r requirements.txt
```

3. Run the application:
```bash
python app/main.py
```

## Deployment

This application is configured to be deployed on Render. The deployment process will:
1. Automatically download the model from Google Drive
2. Install all required dependencies
3. Start the server using gunicorn

## API Endpoints

- `POST /predict`: Upload an image to get disease prediction
  - Request: Form data with 'file' field containing the image
  - Response: JSON with prediction results
