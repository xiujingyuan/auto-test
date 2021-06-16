from app.api.nacos import api_nacos


@api_nacos.route('/')
def hello_world():
    return 'hello nacos api'
