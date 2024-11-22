from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from seleniumbase import SB
import requests
import os
from PIL import Image
def configure_folder_structure():
    os.makedirs("mvp_data", exist_ok=True)
    os.makedirs("mvp_data/logs", exist_ok=True)
configure_folder_structure()
def save_image(url, path):
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            with open(path, "wb") as file:
                file.write(response.content)
                return True
            with Image.open(path) as img:
                # Convert to PNG
                img.save(path, 'PNG')
        else:
            print(f"Failed to fetch image from {url}: Status code {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"Error while fetching image: {e}")
        return False
def save_result(res):
    if not res or "exposeId" not in res or "images" not in res or not res["images"]:
        print("Invalid response or no images found.")
        return
    exposeId = res["exposeId"]
    os.makedirs(f"mvp_data/{exposeId}", exist_ok=True)
    for index, item in enumerate(res["images"]):
        if item and "generatedImages" in item:
            for key, value in item["generatedImages"].items():
                os.makedirs(f"mvp_data/{exposeId}/{exposeId}_{index+1}/{key}", exist_ok=True)
                save_image(item.get("originalImage"), f"mvp_data/{exposeId}/{exposeId}_{index+1}/{key}/image_{key}_empty.png")
                save_image(value, f"mvp_data/{exposeId}/{exposeId}_{index+1}/{key}/image_{key}_staged.png")
        else:
            print(f"No valid image data found for exposeId: {exposeId}")
def get_image_pairs(exposeId):
    url = f"https://static-immobilienscout24.de/ai-image-api/public/getImages?exposeId={exposeId}"
    headers = {
        "accept": "*/*",
        "accept-language": "en-GB,en-US;q=0.9,en;q=0.8",
        "content-type": "application/json",
        "priority": "u=1, i",
        "sec-ch-ua": '"Chromium";v="130", "Google Chrome";v="130", "Not?A_Brand";v="99"',
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": '"Windows"',
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "cross-site"
    }
    try:
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code == 200:
            return response.json()
        else:
            print(f"Failed to get images for exposeId {exposeId}: Status code {response.status_code}")
            return None
    except requests.exceptions.RequestException as e:
        print(f"Error while fetching image pairs: {e}")
        return None
def search_max_page_number(driver, url):
    driver.get(url)  # Open the specified URL
    WebDriverWait(driver, 20).until(lambda d: d.execute_script("return document.readyState") == "complete")
    try:
        pagination = WebDriverWait(driver, 10).until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, "li.p-items"))
        )
        if len(pagination) < 2:
            print("Not enough pagination items found.")
            return None
        max_page = pagination[-2].find_element(By.CSS_SELECTOR, "a").get_attribute("innerHTML")
        return int(max_page)
    except Exception as e:
        print(f"An error occurred: {e}")
        return None
def loop_whole_page(driver, url):
    driver.get(url)  # Open the specified URL
    WebDriverWait(driver, 20).until(lambda d: d.execute_script("return document.readyState") == "complete")
    print("Starting......")
    try:
        items = WebDriverWait(driver, 10).until(
            EC.presence_of_all_elements_located((By.CLASS_NAME, "result-list__listing"))
        )
    except TimeoutException:
        print("Timeout: The elements were not found within the specified time frame.")
        items = []  # Handle as needed
    id_list = [item.get_attribute("data-id") for item in items]
    print(id_list)
    for index, id in enumerate(id_list):
        data = get_image_pairs(id)
        if data:
            save_result(data)
            print(f"Processed: {index + 1}/{len(id_list)}")
        log_path = 'mvp_data/logs/log.txt'
    # File exists, append the list to it
    with open(log_path, 'a') as file:  # Append mode
        file.write('\n'.join(id_list) + '\n')  # Append IDs, each on a new line
def main():
    urls=[
        "https://www.immobilienscout24.de/Suche/de/berlin/berlin/wohnung-kaufen?rented=false",
        "https://www.immobilienscout24.de/Suche/de/bremen/bremen/wohnung-kaufen?rented=false",
        "https://www.immobilienscout24.de/Suche/de/sachsen/dresden/wohnung-kaufen?rented=false",
        "https://www.immobilienscout24.de/Suche/de/nordrhein-westfalen/duesseldorf/wohnung-kaufen?rented=false",
        "https://www.immobilienscout24.de/Suche/de/thueringen/erfurt/wohnung-kaufen?rented=false",
        "https://www.immobilienscout24.de/Suche/de/hamburg/hamburg/wohnung-kaufen?rented=false",
        "https://www.immobilienscout24.de/Suche/de/niedersachsen/hannover/wohnung-kaufen?rented=false",
        "https://www.immobilienscout24.de/Suche/de/schleswig-holstein/kiel/wohnung-kaufen?rented=false",
        "https://www.immobilienscout24.de/Suche/de/nordrhein-westfalen/koeln/wohnung-kaufen?rented=false",
        "https://www.immobilienscout24.de/Suche/de/sachsen-anhalt/magdeburg/wohnung-kaufen?rented=false",
        "https://www.immobilienscout24.de/Suche/de/rheinland-pfalz/mainz/wohnung-kaufen?rented=false",
        "https://www.immobilienscout24.de/Suche/de/bayern/muenchen/wohnung-kaufen?rented=false",*
        "https://www.immobilienscout24.de/Suche/de/baden-wuerttemberg/stuttgart/wohnung-kaufen?rented=false",
        "https://www.immobilienscout24.de/Suche/de/mecklenburg-vorpommern/schwerin/wohnung-kaufen?rented=false",
        "https://www.immobilienscout24.de/Suche/de/hessen/wiesbaden/wohnung-kaufen?rented=false",
        "https://www.immobilienscout24.de/Suche/de/saarland/stadtverband-saarbruecken-kreis/wohnung-kaufen?rented=false",
        "https://www.immobilienscout24.de/Suche/de/brandenburg/potsdam/wohnung-kaufen?rented=false"
        ]
    with SB(uc=True) as driver:
        try:
            for url in urls:
                max_page = search_max_page_number(driver, url)
                for i in range(1, max_page + 1):
                    page_url = f"{url}" if i == 1 else f"{url}&pagenumber={i}"
                    loop_whole_page(driver, page_url)
                    print(f"Finished page {i}.")
                print("Finished_url.")
            print("Finished.")
        except KeyboardInterrupt:
            print("Keyboard interrupt detected. Exiting...")
    # No need for driver.quit(), it is handled by the 'with' statement.
if __name__ == "__main__":
    log_path = 'mvp_data/logs/log.txt'
    with open(log_path, 'w') as file:  # Write mode
        file.write('')  # Write IDs, each on a new line
    main()