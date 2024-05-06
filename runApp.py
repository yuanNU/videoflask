from flask import Flask, render_template, Response, request
import cv2

app = Flask(__name__)

cap = None
video_writer = None
is_recording = False

@app.route('/')
def index():
    return render_template('index.html')

def gen_frames(video_source):
    global video_writer, is_recording, cap
    if not cap:
        cap = cv2.VideoCapture(video_source)
        if not cap.isOpened():
            raise ValueError("Error opening video stream or file")

    while True:
        success, frame = cap.read()
        if not success:
            break
        else:
            ret, buffer = cv2.imencode('.jpg', frame)
            frame = buffer.tobytes()

            if is_recording:
                if not video_writer:
                    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH) + 0.5)
                    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT) + 0.5)
                    size = (width, height)
                    fourcc = cv2.VideoWriter_fourcc(*'XVID')
                    video_writer = cv2.VideoWriter('2Recorded.avi', fourcc, 20.0, size)
                video_writer.write(cv2.imdecode(buffer, cv2.IMREAD_COLOR))

            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

@app.route('/video_feed')
def video_feed():
    video_source = request.args.get('video_source')
    return Response(gen_frames(video_source), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/start_recording', methods=['POST'])
def start_recording():
    global is_recording
    is_recording = True
    return "Recording started", 200

@app.route('/stop_recording', methods=['POST'])
def stop_recording():
    global is_recording, video_writer, cap
    is_recording = False
    if video_writer:
        video_writer.release()
        video_writer = None
    if cap:
        cap.release()
        cap = None
    return "Recording stopped", 200

if __name__ == '__main__':
    app.run(debug=True, threaded=True, use_reloader=False)