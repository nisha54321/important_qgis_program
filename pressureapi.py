import os, cv2, math, numpy as np
#http://192.168.15.148:2001/?filename=/home/rdp/Music/pressure/img/gauge-4.jpeg&maxval=80
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

####
def avg_circles(circles, b):
    avg_x, avg_y, avg_r = 0, 0, 0
    for i in range(b):
        avg_x = avg_x + circles[0][i][0]
        avg_y = avg_y + circles[0][i][1]
        avg_r = avg_r + circles[0][i][2]
    avg_x = int(avg_x / (b))
    avg_y = int(avg_y / (b))
    avg_r = int(avg_r / (b))
    return avg_x, avg_y, avg_r

def showImg(img):
    cv2.imshow("output", img)
    cv2.waitKey(0)
    cv2.destroyAllWindows()


def dist_2_pts(x1, y1, x2, y2):
    return np.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)

# folder = os.getcwd() + "/img/test1.jpeg"
# maxval = 100

@app.route('/',methods=['GET'])
def findVal():
    folder = request.args.get('filename')
    maxval = float(request.args.get('maxval'))
    print(folder,maxval)
    
    img = cv2.imread(folder)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    blur = cv2.blur(gray, (12, 12))
    height, width = img.shape[:2]
    circle_img = cv2.HoughCircles(
        blur,
        cv2.HOUGH_GRADIENT,
        1,
        1,
        np.array([]),
        100,
        45,
        int(height * 0.2),
        int(height * 0.7),
    )
    a, b, c = circle_img.shape
    x, y, r = avg_circles(circle_img, b)
    output1 = img.copy()
    cv2.circle(output1, (x, y), r, (0, 255, 0), 2)
    cv2.circle(output1, (x, y), 2, (0, 0, 255), 5)
    mask = np.zeros(output1.shape[:2], dtype="uint8")
    cv2.circle(mask, (x, y), r, 255, -1)
    img_c = cv2.bitwise_and(img, img, mask=mask)
    captured_frame_bgr = cv2.cvtColor(img_c, cv2.COLOR_BGRA2BGR)
    captured_frame_bgr = cv2.medianBlur(captured_frame_bgr, 3)
    captured_frame_lab = cv2.cvtColor(captured_frame_bgr, cv2.COLOR_BGR2Lab)
    captured_frame_lab_red = cv2.inRange(
        captured_frame_lab, np.array([20, 150, 150]), np.array([190, 255, 255])
    )
    captured_frame_lab_red = cv2.GaussianBlur(captured_frame_lab_red, (5, 5), 2, 2)
    circles = cv2.HoughCircles(
        captured_frame_lab_red,
        cv2.HOUGH_GRADIENT,
        1,
        captured_frame_lab_red.shape[0] / 8,
        param1=100,
        param2=11,
        minRadius=0,
        maxRadius=60,
    )
    if circles is not None:
        circles = np.round(circles[0, :]).astype("int")
        for circle in circles:
            cv2.circle(
                output1,
                center=(circle[0], circle[1]),
                radius=circle[2],
                color=(0, 255, 0),
                thickness=2,
            )
    th, dst2 = cv2.threshold(gray, 130, 255, cv2.THRESH_BINARY_INV)
    masked = cv2.bitwise_and(dst2, dst2, mask=mask)
    lines = cv2.HoughLinesP(
        image=masked,
        rho=3,
        theta=np.pi / 180,
        threshold=100,
        minLineLength=100,
        maxLineGap=0,
    )
    final_line_list = []
    diff1LowerBound = 0
    diff1UpperBound = 0.5
    diff2LowerBound = 0.65
    diff2UpperBound = 1.0
    for i in range(0, len(lines)):
        for x1, y1, x2, y2 in lines[i]:
            diff1 = dist_2_pts(x, y, x1, y1)
            diff2 = dist_2_pts(x, y, x2, y2)
            if diff1 > diff2:
                temp = diff1
                diff1 = diff2
                diff2 = temp
            if (
                (diff1 < diff1UpperBound * r)
                and (diff1 > diff1LowerBound * r)
                and (diff2 < diff2UpperBound * r)
            ) and (diff2 > diff2LowerBound * r):
                final_line_list.append([x1, y1, x2, y2])
    x1 = final_line_list[0][0]
    y1 = final_line_list[0][1]
    x2 = final_line_list[0][2]
    y2 = final_line_list[0][3]
    cv2.line(output1, (x1, y1), (x2, y2), (0, 0, 255), 2)
    red1 = math.atan2(circles[0][0] - x, circles[0][1] - y) * 180 / math.pi
    red2 = math.atan2(circles[1][0] - x, circles[1][1] - y) * 180 / math.pi
    val = abs(180 - math.atan2(x - x1, y - y1) * 180 / math.pi)
    if red1 > 0:
        start = 90 - red1
        end = 270 - red2
    else:
        start = 90 - red2
        end = 270 - red1
    val1 = val - start
    
    temp = maxval / (end - start)
    new_value = val1 * temp
    cv2.rectangle(
        output1,
        (x - (r + 10), y - (r + 10)),
        (x + (r + 10), y + (r + 10)),
        (0, 255, 0),
        3,
    )
    cv2.putText(
        output1,
        ("Gauge Reading: {}".format(math.ceil(new_value))),
        (int(x - (r + 14)), int(y - (r + 14))),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.8,
        (0, 0, 255),
        2,
        cv2.LINE_AA,
    )
    
    val = "Gauge Reading: {}".format(math.ceil(new_value))
    
    return jsonify(val)

if __name__ == '__main__':
    app.run(host='0.0.0.0',debug=True,port=2001)

