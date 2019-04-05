from sanic.response import json
from sanic import Blueprint

import requests

from html.parser import HTMLParser
from bs4 import BeautifulSoup

from io import BytesIO

from PIL import Image

from base64 import b64encode, standard_b64encode

v1 = Blueprint('v1')

@v1.route('/v1')
async def get_article(request):
    article_url = request.args.get('a',None)
    if not article_url:
        return json({'status':'error', 'message':'missing article'})
    else:
        req = requests.get(article_url)

        soup = BeautifulSoup(req.text, 'html.parser')

        info = {
            'url':article_url,
            'extra':{}
        }

        for meta in soup.find_all('meta'):
            type = meta.get('name', None)
            if type == None:
                type = meta.get('property')

            # HTML standards
            if type=="title":info['title']=meta.get('content','_')
            if type=="og:title":info['title']=meta.get('content','_')
            if type=="twitter:title":info['title']=meta.get('content','_')

            if type=="description":info['description']=meta.get('content','_')
            if type=="og:description":info['description']=meta.get('content','_')
            if type=="twitter:description":info['description']=meta.get('content','_')

            if type=="image":info['image_url']=meta.get('content','_')
            if type=="og:image":info['image_url']=meta.get('content','_')
            if type=="twitter:image":info['image_url']=meta.get('content','_')

            # Article specific
            if type=="author":info['author']=meta.get('content','_')

            if type=="article:kicker":info['extra']['kicker']=meta.get('content','_')
            if type=="topo:kicker":info['extra']['kicker']=meta.get('content','_')

        # image as data
        if info.get('image_url') :
            print('o')
            im_url = info.get('image_url')
            im_req = requests.get(im_url)
            print(im_req.content)

            info['image_data'] = ''
            img = Image.open(BytesIO(im_req.content))
            output = BytesIO()
            img.save(output, format='JPEG')
            hex_data = output.getvalue()
            info['image_data'] = "data:image/jpg;base64,"+str(standard_b64encode(hex_data), 'utf-8')

        return json({
            'status':'ok',
            'data': info
        })
