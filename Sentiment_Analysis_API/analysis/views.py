import os
import pandas as pd
from groq import Groq
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render

# Initialize the Groq client with the API key
client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

def home(request):
    """Renders the file upload page."""
    return render(request, 'file_upload.html')

def process_file(file):
    """
    Processes the uploaded file (CSV or XLSX) and extracts reviews from it.

    Args:
        file: The uploaded file object.

    Returns:
        A tuple: (list of reviews, error message).
    """
    extension = file.name.split('.')[-1].lower()
    try:
        if extension == 'csv':
            df = pd.read_csv(file)
        elif extension == 'xlsx':
            df = pd.read_excel(file)
        else:
            return None, "Invalid file format. Please upload a CSV or XLSX file."

        if 'Review' not in df.columns:
            return None, "'Review' column is missing from the file."

        return df['Review'].tolist(), None
    except Exception as e:
        return None, f"Error processing file: {str(e)}"

def analyze_sentiment(reviews):
    """
    Sends reviews to Groq API for sentiment analysis.

    Args:
        reviews: List of review strings.

    Returns:
        A tuple: (sentiment result dictionary, error message).
    """
    positive, negative, neutral = 0, 0, 0

    # Loop through reviews and send each one to the Groq API for analysis
    for review in reviews:
        try:
            # Send a chat completion request with the review as the input message
            chat_completion = client.chat.completions.create(
                messages=[{"role": "user", "content": review}],
                model="llama3-8b-8192"  # Replace with the correct model name if different
            )

            # Extract sentiment from the response (adjust parsing based on response format)
            response_content = chat_completion.choices[0].message.content.lower()

            if "positive" in response_content:
                positive += 1
            elif "negative" in response_content:
                negative += 1
            else:
                neutral += 1

        except Exception as e:
            return None, f"Error analyzing sentiment with Groq API: {str(e)}"

    return {
        "positive": positive,
        "negative": negative,
        "neutral": neutral
    }, None

@csrf_exempt
def upload_file(request):
    """
    Handles file upload and triggers sentiment analysis.

    Args:
        request: HTTP request object.

    Returns:
        JSON response with sentiment analysis results or error message.
    """
    if request.method == 'POST':
        # Get file from request
        uploaded_file = request.FILES.get('file')
        if not uploaded_file:
            return JsonResponse({'error': 'No file provided.'}, status=400)

        # Process the uploaded file to extract reviews
        reviews, error = process_file(uploaded_file)
        if error:
            return JsonResponse({'error': error}, status=400)

        # Perform sentiment analysis using Groq API
        sentiment_result, error = analyze_sentiment(reviews)

        if error:
            return JsonResponse({'error': error}, status=500)

        # Return sentiment analysis results
        return JsonResponse(sentiment_result)

    # If method is not POST, return an error
    return JsonResponse({'error': 'Invalid request method.'}, status=405)
