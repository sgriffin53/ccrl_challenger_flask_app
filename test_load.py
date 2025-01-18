import concurrent.futures
import requests
import time

# Define the API endpoint and parameters
url = "http://localhost:8080/stream_engine"
params = {
    "fen": "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1",
    "engine_name": "stockfish",
    "time_limit": 60
}

# Disable SSL verification for local testing (WARNING: Use with caution in production)
verify_ssl = False

# Define a function to make a single request
def make_request():
    try:
        response = requests.get(url, params=params, verify=verify_ssl)
        return response.status_code, response.text
    except Exception as e:
        return "Error", str(e)

# Define a function to run multiple simultaneous requests
def test_api_concurrently(num_requests):
    start_time = time.time()
    with concurrent.futures.ThreadPoolExecutor(max_workers=num_requests) as executor:
        # Submit multiple requests concurrently
        futures = [executor.submit(make_request) for _ in range(num_requests)]
        # Collect results
        results = [future.result() for future in concurrent.futures.as_completed(futures)]
    elapsed_time = time.time() - start_time
    return results, elapsed_time

if __name__ == "__main__":
    # Number of simultaneous requests to test
    num_requests = 100

    print(f"Testing API with {num_requests} simultaneous requests...")
    results, elapsed_time = test_api_concurrently(num_requests)

    print(f"Test completed in {elapsed_time:.2f} seconds.")
    print("Results:")
    for i, result in enumerate(results):
        print(f"Request {i + 1}: {result[0]} - {result[1]}")