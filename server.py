from flask import Flask, request, jsonify
from flask_cors import CORS
import librosa
import pickle
import numpy as np
from tensorflow.keras.models import Sequential, model_from_json


json_file = open('./emotion_model.json', 'r')
loaded_model_json = json_file.read()
json_file.close()
loaded_model = model_from_json(loaded_model_json)

with open('./scaler2.pickle', 'rb') as f:
    scaler2 = pickle.load(f)

with open('./encoder2.pickle', 'rb') as f:
    encoder2 = pickle.load(f)


def zcr(data, frame_length, hop_length):
    zcr = librosa.feature.zero_crossing_rate(
        data, frame_length=frame_length, hop_length=hop_length)
    return np.squeeze(zcr)


def rmse(data, frame_length=2048, hop_length=512):
    rmse = librosa.feature.rms(
        y=data, frame_length=frame_length, hop_length=hop_length)
    return np.squeeze(rmse)


def mfcc(data, sr, frame_length=2048, hop_length=512, flatten: bool = True):
    mfcc = librosa.feature.mfcc(y=data, sr=sr)
    return np.squeeze(mfcc.T)if not flatten else np.ravel(mfcc.T)


def extract_features(data, sr=22050, frame_length=2048, hop_length=512):
    result = np.array([])

    result = np.hstack((result,
                        zcr(data, frame_length, hop_length),
                        rmse(data, frame_length, hop_length),
                        mfcc(data, sr, frame_length, hop_length)
                        ))
    return result


def get_predict_feat(path):
    d, s_rate = librosa.load(path, duration=2.5, offset=0.6)
    res = extract_features(d)
    result = np.array(res)

    # Pad the feature vector with zeros if its size is smaller than 2376
    if len(result) < 2376:
        result = np.pad(result, (0, 2376 - len(result)))

    result = np.reshape(result, newshape=(1, 2376))
    i_result = scaler2.transform(result)
    final_result = np.expand_dims(i_result, axis=2)

    return final_result


emotions1 = {1: 'Neutral', 2: 'Calm', 3: 'Happy', 4: 'Sad',
             5: 'Angry', 6: 'Fearful', 7: 'Disgust', 8: 'Surprise'}


def prediction(path1):
    res = get_predict_feat(path1)
    predictions = loaded_model.predict(res)
    y_pred = encoder2.inverse_transform(predictions)
    print(y_pred[0][0])
    return y_pred[0][0]




app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})


@app.route('/run', methods=['POST', 'OPTIONS'])
def handle_run():
    if request.method == 'OPTIONS':
        # Respond to preflight request
        response = jsonify({'message': 'Preflight request successful'})
        response.headers.add('Access-Control-Allow-Origin',
                             'http://localhost:5173')
        response.headers.add('Access-Control-Allow-Methods', 'POST')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type')
        return response
    elif request.method == 'POST':
        # Handle actual POST request
        emotion = prediction("static/recorded_audio.wav")
        response_data = {"emotion": emotion}
        return jsonify(response_data)


if __name__ == '__main__':
    app.run(debug=True, port=5000)
