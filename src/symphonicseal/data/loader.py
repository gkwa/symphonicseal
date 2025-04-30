import os
import requests
import urllib.parse


def load_data(file_path, url=None):
    """
    Load data either from file, URL, or file:// URL

    Args:
        file_path: Path to local file
        url: URL to fetch data from if local file doesn't exist (supports http://, https://, file://)

    Returns:
        List of product titles or None if data couldn't be loaded
    """
    # Try to load from local file first
    if os.path.exists(file_path):
        print(f"Loading data from local file: {file_path}")

        with open(file_path, "r", encoding="utf-8") as f:
            return [line.strip() for line in f if line.strip()]

    # If file doesn't exist but URL is provided, try to fetch from URL
    if url:
        try:
            # Check if it's a file:// URL
            if url.startswith("file://"):
                local_path = urllib.parse.unquote(
                    url[7:]
                )  # Remove 'file://' and decode

                print(f"Loading data from file:// URL: {local_path}")

                if os.path.exists(local_path):
                    with open(local_path, "r", encoding="utf-8") as f:
                        lines = [line.strip() for line in f if line.strip()]
                else:
                    print(f"Error: File not found at path: {local_path}")
                    return None
            else:
                # Regular HTTP/HTTPS URL
                print(f"Local file not found. Fetching data from URL: {url}")

                response = requests.get(url)
                response.raise_for_status()
                lines = [
                    line.strip() for line in response.text.split("\n") if line.strip()
                ]

            # Save to local file for future use
            with open(file_path, "w", encoding="utf-8") as f:
                f.write("\n".join(lines))

            return lines

        except Exception as e:
            print(f"Error loading data from URL: {e}")
            return None

    print(f"Error: Could not find file {file_path} and no URL provided")
    return None
