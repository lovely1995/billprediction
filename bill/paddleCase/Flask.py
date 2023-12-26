
from flask import Flask,request
from flask import render_template
from flask.views import MethodView
from flask_restx import Api, Resource,Namespace, fields

import json
import ocrFuc as ocr
app = Flask(__name__)
#swagger
api = Api(app)
# 创建第一个命名空间
namespace1 = Namespace('OCR', description='ocr-YulonBill-V2023.12.12')
api.add_namespace(namespace1)


path = api.model('para', {
    'PATH': fields.String(description='path'),
    'TOKEN': fields.String(description='token'),
})

@namespace1.route('/preWater')
class preWater(Resource):
    @api.expect(path)  # 指定期望的输入参数模型
    def post(self):
        """
        This is the documentation for preWaterBill.
        """
        data = json.loads(request.data.decode('utf-8'))
        result = ocr.water(data)
        return result

@namespace1.route('/preEle')
class preEle(Resource):
    @api.expect(path)  # 指定期望的输入参数模型
    def post(self):
        """
        This is the documentation for preEleBill.
        """
        data = json.loads(request.data.decode('utf-8'))
        result = ocr.ele(data)
        return result



if __name__ == '__main__':
    app.debug = True
    app.run()
    

                
                
