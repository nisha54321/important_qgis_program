from ai4bharat.transliteration import XlitEngine
#http://192.168.13.6:4000/?name1=NISHA%20PATEl
from flask import Flask, request, jsonify
from flask_cors import CORS
import time

app = Flask(__name__)
CORS(app)

#@app.route('/',methods=['GET','POST'])
def main():
    
    t1 = time.time()
    # name1 = request.args.get('name1')
    # print(name1)
    b1 = 100000*('rakesh gupta',)

    # b1 = 'mahesh','lina','ramesh'*300
    
    # l1 = [b1]
    res= []
    e = XlitEngine("hi", beam_width=1) ###sentence
    for i in b1:
        result = e.translit_sentence(i)
        result = result['hi']
        # e = XlitEngine("hi", beam_width=10) ###sentence
        # result = e.translit_sentence(name1)
        # result = result['hi']
        res.append(result)
    print(res)
    print(f'{time.time() -t1} seconds')
    #return jsonify(str(result))
 
if __name__ == "__main__":
    main()

    #app.run(host='0.0.0.0',port=4000)
