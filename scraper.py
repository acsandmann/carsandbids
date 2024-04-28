from bs4 import BeautifulSoup
import time
import re
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from concurrent.futures import ThreadPoolExecutor
import urllib.request
import ssl
import json

ssl._create_default_https_context = ssl._create_stdlib_context


class Scraper:
    def __init__(self):
        self.data = []
        options = Options()
        options.add_argument("--window-size=1920,1200")
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_argument("--headless")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-gpu")
        self.driver = webdriver.Chrome(options=options)

        opener = urllib.request.build_opener()
        opener.addheaders = [
            (
                "User-Agent",
                "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/36.0.1941.0 Safari/537.36",
            )
        ]
        urllib.request.install_opener(opener)

    def scrape_page(self, page=None):
        soup = self.make_request(
            f'https://carsandbids.com/past-auctions/{f"?page={page}" if page is not None else ""}'
        )
        ul_tag = soup.find("ul", class_="auctions-list past-auctions")
        li_tags = ul_tag.find_all("li", class_="auction-item")

        for li in li_tags:
            data = {
                "url": li.find("a", class_="hero")["href"],
                "title": li.find("a", class_="hero")["title"],
                "image_url": li.find("img")["src"],
                #'sold_price': li.find('span', class_='bid-value').text
            }
            bid_value = li.find("span", class_="bid-value")
            if bid_value:
                data["sold_price"] = bid_value.text.strip()

            auction_subtitle = li.find("p", class_="auction-subtitle")
            if auction_subtitle:
                details = auction_subtitle.text.strip()
                parsed_entry = {
                    "engine": re.search(
                        r"\b(\d{3}-hp|\d+.\d+-Liter|\d+.\d+-Liter Flat-\d+)\b", details
                    ),
                    "transmission": re.search(
                        r"\b(\d+-Speed Manual|Automatic|PDK)\b", details
                    ),
                    #'packages': re.search(r'\b(Sport Chrono Package|AMG Performance Package|Sport Package)\b', details),
                    "ownership": re.search(
                        r"\b(\d+ Owner|California-Owned|Southern-Owned)\b", details
                    ),
                    "modifications": re.search(
                        r"\b(Mostly Unmodified|Some Modifications|Highly Modified)\b",
                        details,
                    ),
                    "mileage": re.search(r"~?(\d{1,3}(,\d{3})* Miles)\b", details),
                    #'Misc': re.findall(r'[^,]+', details)  # Catch all other details
                }

                # Normalize extracted data
                for key in parsed_entry:
                    match = parsed_entry[key]
                    data[key] = match.group(0) if match else None

            self.data.append(data)

    def make_request(self, url):
        driver = self.driver
        try:
            driver.get(url)
            time.sleep(5)
            driver.execute_script("window.scrollTo(0, 2000)")
            time.sleep(2)
            driver.execute_script("window.scrollTo(0, 2000)")
            time.sleep(2)
            driver.execute_script("window.scrollTo(0, 2000)")
            time.sleep(2)
            driver.execute_script("window.scrollTo(0, 2000)")
            time.sleep(2)
            driver.execute_script("window.scrollTo(0, 2000)")
            time.sleep(2)
            soup = BeautifulSoup(driver.page_source, "html.parser")
            return soup
        except Exception as e:
            print(e)

    def scrape(self):
        pages = range(1, 396)
        with ThreadPoolExecutor(max_workers=15) as executor:
            executor.map(self.scrape_page, pages)
        self.scrape_page()


def main():
    s = Scraper()
    s.scrape()
    with open("scraped_data.json", "w") as outfile:
        json.dump(s.data, outfile, indent=4)


if __name__ == "__main__":
    main()
