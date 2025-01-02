import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin

def find_links(domain):
    base_url = f"https://{domain}"
    visited_links = set()
    html_files = []
    def crawl(url):
        if url in visited_links or not url.startswith(base_url):
            return
        visited_links.add(url)
        try:
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                for link in soup.find_all("a", href=True):
                    href = link['href'].strip()
                    full_url = urljoin(base_url, href)  # Handle relative URLs
                    if f"//{domain}" in full_url:
                        if full_url not in html_files:
                            html_files.append(full_url)
                    elif not full_url.endswith(('.jpg', '.png', '.css', '.js', '.json', '.xml')):  # Skip non-relevant files
                        crawl(full_url)  # Recursively crawl other links
            else:
                print(f"Failed to access {url}. Status code: {response.status_code}")
        except requests.exceptions.RequestException as e:
            print(f"Error accessing {url}: {e}")
    crawl(base_url)
    if html_files:
        return html_files
    else:
        print("No HTML files found.")
        return None

def get_subdomains_from_crtsh(domain):
        url = f"https://crt.sh/?q=%25.{domain}&output=json"
        try:
            response = requests.get(url)
            if response.status_code == 200:
                cert_data = response.json()
                subdomains = {entry['name_value'] for entry in cert_data}
                return list(subdomains)
        except Exception as e:
            print(f"Error fetching data: {e}")
        return []

def searcher(domain):
    subdomains = get_subdomains_from_crtsh(domain)
    if subdomains:
        print("\n\nFound subdomains..!")
        for sub in subdomains:
            print(sub)
    else:
        print("\n\nNo subdomains found..!")
    urls = find_links(domain)
    if urls:
        print("\n\nFound Sitemap..!")
        for links in urls:
            print(links)
    else:
        print("\n\nNo sitemap found..!")

print("Domain and Sitemap searcher")
domain = input("Enter the domain: ")
searcher(domain)
