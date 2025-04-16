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

## Deployment on Render

1. Create a new Web Service on Render
2. Connect your GitHub repository
3. Use the following settings:
   - **Environment**: Python 3.9
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn app.main:app`
   - **Plan**: Choose an appropriate plan (at least 512MB RAM recommended)

The deployment will:
1. Automatically download the model from Google Drive
2. Install all required dependencies
3. Start the server using gunicorn

## API Endpoints

- `GET /` - Home endpoint, shows API status and available endpoints
- `GET /health` - Health check endpoint
- `POST /predict` - Upload an image to get disease prediction
  - Request: Form data with 'file' field containing the image
  - Response: JSON with prediction results and confidence scores

## CORS Support

The API supports Cross-Origin Resource Sharing (CORS) and can be accessed from any domain.

## Error Handling

The API includes proper error handling for:
- 400 Bad Request - Invalid input or missing files
- 500 Internal Server Error - Server-side issues

## Environment Variables

No additional environment variables are required. The server automatically uses the PORT provided by Render.

## Android Integration

The API can be easily integrated with Android applications. Here's an example using Retrofit:

```kotlin
// API Interface
interface SoyabeanApi {
    @Multipart
    @POST("predict")
    suspend fun predictDisease(
        @Part image: MultipartBody.Part
    ): Response<PredictionResponse>
}

// Response data class
data class PredictionResponse(
    val prediction: String,
    val confidence: Double
)

// Add these dependencies to your app's build.gradle
dependencies {
    implementation "com.squareup.retrofit2:retrofit:2.9.0"
    implementation "com.squareup.retrofit2:converter-gson:2.9.0"
}
```

Example API call:
```kotlin
// Initialize Retrofit
val retrofit = Retrofit.Builder()
    .baseUrl("YOUR_RENDER_API_URL")
    .addConverterFactory(GsonConverterFactory.create())
    .build()

val api = retrofit.create(SoyabeanApi::class.java)

// Make API call
val file = File(imagePath)
val requestFile = RequestBody.create("image/*".toMediaTypeOrNull(), file)
val body = MultipartBody.Part.createFormData("file", file.name, requestFile)

try {
    val response = api.predictDisease(body)
    if (response.isSuccessful) {
        val result = response.body()
        // Handle prediction result
    }
} catch (e: Exception) {
    // Handle error
}
