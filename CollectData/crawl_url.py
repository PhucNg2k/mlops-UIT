import os
import requests

from constant import URL_FILE, HTML_FOLDER

def main():
    urls = []

    with open(URL_FILE, 'r') as file:
        for line in file:
            urls.append(line.strip())


    
    html_files = []

    os.makedirs(HTML_FOLDER, exist_ok=True)

    for url in urls:
        tmp  = url.split("/")[-1].split("-")[:4]
        file_name = "_".join(tmp)

        print(f"Downloading {file_name} from {url}")

        try:
            response = requests.get(url=url)
            response.raise_for_status()


            file_path = os.path.join(HTML_FOLDER, f"{file_name}.html")
            html_files.append(file_path)

            with open(file_path, 'w', encoding="utf-8") as f:
                f.write(response.text)
            print(f"Successufully save {file_path}")
        except requests.exceptions.RequestException as e:
            print(f"Error downloading  {url} : {e}")


if __name__ == "__main__":
    main()