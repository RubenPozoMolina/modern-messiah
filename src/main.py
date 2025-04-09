import requests
import json


# Example of a chat completion request
def get_completion(prompt):
    headers = {
        "Content-Type": "application/json"
    }

    data = {
        "messages": [
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.7,
        "max_tokens": 500
    }

    try:
        response = requests.post(
            f"{BASE_URL}/chat/completions",
            headers=headers,
            json=data
        )
        response.raise_for_status()  # Raise an exception for bad status codes

        result = response.json()
        return result['choices'][0]['message']['content']
    except requests.exceptions.RequestException as e:
        print(f"Error making request: {e}")
        return None


# Example usage
if __name__ == "__main__":
    prompt = "What is the capital of France?"
    response = get_completion(prompt)
    if response:
        print("Response:", response)