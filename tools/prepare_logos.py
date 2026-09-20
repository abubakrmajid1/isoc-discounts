"""Retrieve genuine retailer logos from published brand/offer-provider assets."""
import io, json, pathlib, urllib.request
from PIL import Image
import cairosvg
root = pathlib.Path('logos')
sources = json.loads((root / 'sources.json').read_text())
urls = {
 'superdrug': 'https://d34e3vwr98gw1q.cloudfront.net/7167749b1a933ad0c8fd08bb91ab48b2e1087f6ddfbcd85703e9dd0dd130247d/original/b2117af8-4acf-4e77-8a0e-3263e7c4fd97.svg',
 'schuh': 'https://d34e3vwr98gw1q.cloudfront.net/82a29abf5823c18c56d2fb35741fe20cde3203966e9da1f1cbcb78e58fc3127e/original/2b484ef0-9b53-4f6e-85c1-84c091dfac65.svg',
 'specsavers': 'https://upload.wikimedia.org/wikipedia/commons/7/78/Specsavers_logo.svg'
}
for brand, url in urls.items():
    request = urllib.request.Request(url, headers={'User-Agent': 'SwanseaISOC-Directory/1.0 (https://github.com/abubakrmajid1/isoc-discounts)'})
    with urllib.request.urlopen(request, timeout=35) as response:
        data = response.read()
    if b'<svg' not in data[:2000]:
        raise ValueError('Not a valid logo SVG: '+brand)
    png = cairosvg.svg2png(bytestring=data, output_width=400)
    image = Image.open(io.BytesIO(png)).convert('RGBA')
    image.thumbnail((400, 400))
    image.save(root / (brand+'.png'), optimize=True)
    sources[brand+'.png'] = url
    print('Saved', brand, image.size)
(root / 'sources.json').write_text(json.dumps(sources, indent=2))
