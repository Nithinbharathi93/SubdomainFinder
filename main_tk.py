from tkinter import *
from tkinter import scrolledtext
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

def searcher(e, op, site, flag, site_flag):
    domain = e.get()
    e.delete(0, END)
    subdomains = get_subdomains_from_crtsh(domain)
    if subdomains:
        op.delete("0.0", END)
        flag.configure(text = "Found subdomains..!", fg = "green")
        for sub in subdomains:
            op.insert(END, f'{sub}\n')
    else:
        flag.configure(text = "No subdomains found..!", fg = "red")
    urls = find_links(domain)
    if urls:
        site.delete("0.0", END)
        site_flag.configure(text = "Found Sitemap..!", fg = "green")
        for links in urls:
            site.insert(END, f'{links}\n')
    else:
        site_flag.configure(text = "No sitemap found..!", fg = "red")

root = Tk()
root.geometry("600x400")

l_tit = Label(root, text="Domain Searcher")

frm_dom = Frame(root)

l_dom = Label(frm_dom, text = "Domain Name")
e_dom = Entry(frm_dom, width=30)

l_dom.grid(row=0, column=0)
e_dom.grid(row=0, column=1)

scrl_op = scrolledtext.ScrolledText(root, width=80, height=7)

scrl_site = scrolledtext.ScrolledText(root, width=80, height=7)

op_flag = Label(root, text = "", font=("helvetica", 18, "bold"), fg="red")
site_flag = Label(root, text = "", font=("helvetica", 18, "bold"), fg="red")

btn_sub = Button(root, text="Search", command=lambda: searcher(e_dom, scrl_op, scrl_site, op_flag, site_flag))


l_tit.pack()
frm_dom.pack()
scrl_op.pack()
op_flag.pack()
scrl_site.pack()
site_flag.pack()
btn_sub.pack()

root.mainloop()