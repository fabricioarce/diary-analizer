import requests
import sys

def test_stats():
    url = "http://localhost:8000/api/stats"
    print(f"Testing stats endpoint: {url}")
    
    try:
        response = requests.get(url)
        if response.status_code != 200:
            print(f"Error: Status code {response.status_code}")
            print(response.text)
            return
            
        data = response.json()
        print("Success! Response data:")
        print("Total Entries:", data.get("total_entries"))
        print("Top 5 Emotions:", data.get("top_emotions"))
        print("Emotion Counts (sample):", list(data.get("emotion_counts", {}).keys())[:5])
        
    except requests.exceptions.ConnectionError:
        print("Error: Could not connect to server. Is it running on port 8000?")

if __name__ == "__main__":
    test_stats()
