import os
import pandas as pd
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

def fetch_model_data():
    # Hugging Face API endpoint
    base_url = "https://huggingface.co/api/models"
    models = []
    cursor = None
    limit = 2000  # Number of models per page (adjust as needed, max may be enforced by API)

    # Set up a session with retries
    session = requests.Session()
    retries = Retry(total=3, backoff_factor=1, status_forcelist=[429, 500, 502, 503, 504])
    session.mount("https://", HTTPAdapter(max_retries=retries))

    while True:
        # Construct the URL with pagination parameters
        url = f"{base_url}?limit={limit}"
        if cursor:
            url += f"&cursor={cursor}"

        try:
            response = session.get(url, timeout=10)
            response.raise_for_status()  # Raise an exception for 4xx/5xx errors

            data = response.json()
            if not data:
                print("No more model data received from the API")
                break

            print(f"Received {len(data)} models from the API for cursor: {cursor or 'initial'}")

            # Extract model data
            for model in data:
                models.append({
                    "model_id": model.get("modelId"),
                    "description": model.get("pipeline_tag", ""),
                    "tags": ", ".join(model.get("tags", [])),
                    "downloads": model.get("downloads", 0),
                    "likes": model.get("likes", 0),
                    "language": model.get("languages", "unknown")
                })

            # Check for pagination info (cursor for next page)
            # Hugging Face API may return a 'nextCursor' or similar field
            # Adjust this based on the actual API response structure
            cursor = response.headers.get("X-Next-Cursor") or None
            if not cursor:
                print("No more pages to fetch")
                break

        except requests.exceptions.RequestException as e:
            print(f"Error fetching data: {e}")
            break

    if models:
        # Convert models to a DataFrame
        df = pd.DataFrame(models)
        print(f"Total models fetched: {len(df)}")

        # Ensure the 'data' directory exists
        if not os.path.exists('data'):
            os.makedirs('data')

        # Save the DataFrame to CSV
        df.to_csv("data/models_data.csv", index=False)
        print("Model data saved to data/models_data.csv")
    else:
        print("No models were fetched.")

# Run the function to fetch data
if __name__ == "__main__":
    fetch_model_data()