#http://192.168.13.232:5004/?cordinate=71.51459076930828,%2020.9079174228675&radius=500&radius1=800&radius2=1000
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

####
@app.route('/',methods=['GET'])
def index():
    clipshp = 'hellow'
    
    return jsonify(clipshp)


if __name__ == '__main__':
    app.run(host='0.0.0.0',debug=True,port=5004)
