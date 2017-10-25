import os
import pycurl
import StringIO
from PIL import Image

def run_colourise(in_dir, out_dir, filename):
    in_path = in_dir + '/' + filename
    out_path = out_dir + '/' + filename

    # change to your own gateway if you need to
    url = 'http://localhost:8080'

    c = pycurl.Curl()
    c.setopt(pycurl.URL, url)
    fout = StringIO.StringIO()
    c.setopt(pycurl.WRITEFUNCTION, fout.write)

    c.setopt(pycurl.POST, 1)
    c.setopt(pycurl.HTTPHEADER, ["Content-Type: image/jpeg"])

    filesize = os.path.getsize(in_path)
    c.setopt(pycurl.POSTFIELDSIZE, filesize)
    fin = open(in_path, 'rb')
    c.setopt(pycurl.READFUNCTION, fin.read)

    c.perform()

    response_code = c.getinfo(pycurl.RESPONSE_CODE)
    response_data = fout.getvalue()
    print(response_code)

    with open(out_path, 'wb') as f:
        f.write(response_data)

    im = Image.open(out_path)
    im = im.convert('RGB')
    im.save(out_path, "JPEG")

    c.close()

for filename in os.listdir('frames'):
    print('Colourising ' + filename)
    run_colourise('frames', 'output', filename)
