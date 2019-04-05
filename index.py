import os
from sanic import Sanic
from sanic.response import json

from version1 import v1


app = Sanic(__name__)
app.blueprint(v1)


@app.route('/')
async def welcome(request):
    return json({
        'status':'ok',
        'routes':{
            'v1':{
                'article':'/v1/<url>'
            }
        }
    })


if __name__ == '__main__':
    port = os.environ.get('PORT', 3000)
    app.run(host='0.0.0.0', port=port, debug=True)
