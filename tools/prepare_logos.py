"""Fetch published retailer logo assets; never generate substitute brand artwork."""
import io, json, pathlib, re, urllib.request
from urllib.parse import urljoin
from bs4 import BeautifulSoup
from PIL import Image
import cairosvg

root = pathlib.Path('logos')
sources = json.loads((root / 'sources.json').read_text())
headers = {'User-Agent': 'Mozilla/5.0 (compatible; SwanseaISOC-Directory/1.0)'}
def fetch(url):
    with urllib.request.urlopen(urllib.request.Request(url, headers=headers), timeout=35) as response:
        return response.read()

def save_png(name, data):
    if b'<svg' in data[:1500]:
        data = cairosvg.svg2png(bytestring=data, output_width=400)
    image = Image.open(io.BytesIO(data)).convert('RGBA')
    if image.width < 32 or image.height < 16:
        raise ValueError('Image too small')
    image.thumbnail((400, 400))
    image.save(root / (name + '.png'), optimize=True)
    print(name, image.size)

for brand in ['superdrug', 'schuh', 'specsavers']:
    pages = ([f'https://www.studentbeans.com/student-discount/uk/{brand}'] if brand != 'specsavers' else []) + [f'https://www.{brand}.co.uk/' if brand != 'superdrug' else 'https://www.superdrug.com/']
    success = False
    for page in pages:
        try:
            markup = fetch(page).decode('utf-8', 'replace')
            soup = BeautifulSoup(markup, 'html.parser')
            candidates = []
            for img in soup.find_all('img'):
                alt = img.get('alt', '').lower()
                src = img.get('src') or img.get('data-src', '')
                if src and (alt == brand or ('logo' in alt and brand in alt) or (brand in src.lower() and 'logo' in src.lower())):
                    candidates.append(urljoin(page, src))
            if brand == 'specsavers':
                for link in soup.find_all('link'):
                    if 'apple-touch-icon' in link.get('rel', []) or 'icon' in link.get('rel', []):
                        candidates.append(urljoin(page, link.get('href', '')))
                for svg in soup.find_all('svg'):
                    label = (str(svg.get('class', '')) + svg.get('aria-label','') + svg.get('id', '')).lower()
                    if 'logo' in label:
                        try:
                            svg['xmlns'] = 'http://www.w3.org/2000/svg'
                            save_png(brand, str(svg).encode())
                            sources[brand+'.png'] = page + '#header-logo'
                            success = True
                            break
                        except Exception as error:
                            print('inline logo:', error)
            if success:
                break
            print(brand, 'candidates:', candidates[:8])
            for candidate in dict.fromkeys(candidates):
                try:
                    save_png(brand, fetch(candidate))
                    sources[brand+'.png'] = candidate
                    success = True
                    break
                except Exception as error:
                    print('Candidate failed:', error)
            if success:
                break
        except Exception as error:
            print(page, error)
    if not success:
        raise RuntimeError('Could not retrieve a genuine logo for ' + brand)
(root / 'sources.json').write_text(json.dumps(sources, indent=2))
