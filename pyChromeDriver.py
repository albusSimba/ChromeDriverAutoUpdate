import requests
import os
import zipfile
from lxml import html

BETA = 0
STABLE = 1

# Config 
txt = r"ChromeDriverVersion.txt"
version_url = r"https://chromedriver.chromium.org/"
index_url = r'https://chromedriver.storage.googleapis.com/index.html?path='

file_name = 'chromedriver_win32.zip'
dir_7zip = r"7z\7za.exe"
exe_name = "chromedriver.exe"

BUILD = STABLE

class ChromeDriver:
    def __init__(self):

        self.last_updated = " does not exist "
        if os.path.exists(txt):
            read = open(txt, "r")
            self.last_updated = read.readline()
            read.close()

        main_site = requests.get(version_url)
        
        urls = extract_urls(main_site, index_url)
        self.download_links = extract_versions(urls, index_url)
        self.latest_version = self.download_links[BUILD].version

        write = open(txt, "w")
        write.write(self.latest_version)
        write.close()

    def update(self):
        if self.latest_version == self.last_updated:
            print("Current Version is Latest: ChromeDriver", self.last_updated)
        else:
            print("Current Version: ChromeDriver", self.last_updated)
            print("Latest stable release: ChromeDriver", self.latest_version)

            version_response = requests.get(index_url + self.latest_version)

            if version_response.text:
                
                try:
                    download_url = self.download_links[BUILD].download_link
                    print("Requesting url :", download_url)
                    print("Downloading :", file_name)
                    
                    download_file(download_url)

                    while not os.path.exists(file_name):
                        time.sleep(1)

                    print("unziping ... ")

                    cwd = os.getcwd()
                    inDir = os.path.join(cwd, file_name)
                    outDir = cwd

                    zip_decompress(inDir, outDir)

                    while not os.path.exists(exe_name):
                        time.sleep(1)
                except:
                    print("Something went wrong")
                    
                os.remove(file_name)

        
class ChromeDriverUrl():
    def __init__(self, download_link, version):
        self.version = version
        self.download_link = download_link.replace("index.html?path=", "") + file_name

def zip_decompress(inDir, outDir):
    with zipfile.ZipFile(inDir, 'r') as zip_ref:
        zip_ref.extractall(outDir)

def extract_urls(page, url_substring):
    webpage = html.fromstring(page.content)
    return [ url for url in webpage.xpath('//a/@href') if url_substring in url]

def extract_versions(urls, url_substring):

    return [ChromeDriverUrl(download_link=u, 
                            version=u.replace(url_substring, "").replace(r'/', "")) for u in urls]

def download_file(url):
    local_filename = url.split('/')[-1]
    # NOTE the stream=True parameter below
    with requests.get(url, stream=True) as r:
        r.raise_for_status()
        with open(local_filename, 'wb') as f:
            for chunk in r.iter_content(chunk_size=8192): 
                # If you have chunk encoded response uncomment if
                # and set chunk_size parameter to None.
                #if chunk: 
                f.write(chunk)
    return local_filename

if __name__ == '__main__':

    if os.path.exists(txt):
        os.remove(txt)
    ChromeDriver().update()

