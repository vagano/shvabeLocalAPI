from subprocess import PIPE, run
import time

import sqlite3

from flask import Flask, jsonify, request, send_from_directory, g
import json
import os
import base64

import uuid

from flask_cors import CORS
from flask_httpauth import HTTPTokenAuth

import math

import logging

from datetime import datetime

app = Flask(__name__, static_url_path='/')
cors = CORS(app, resources={r"/api/*": {"origins": "*"}})
auth = HTTPTokenAuth(scheme='JWT')

path_to_current_file = os.path.dirname(os.path.abspath(__file__)) + "\\"
cfg_file = open(path_to_current_file + "config.json", 'r')
config = json.load(cfg_file)

level = logging.getLevelName(config['app']['service_log_level'])

logging.basicConfig(level=level,
                    format='%(relativeCreated)6d %(threadName)s %(asctime)s %(levelname)s %(message)s',
                    filename=config['app']['log_path'] + 'app.log',
                    filemode='w')

logging.info("Configurated")


def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(config['app']['database_path'] + config['app']['database_name'])
        cursor = db.cursor();
        cursor.execute('''CREATE TABLE IF NOT EXISTS files (id INTEGER PRIMARY KEY AUTOINCREMENT, date DATETIME, 
                               filetype TEXT, filename TEXT, was_shown INTEGER)''')
        db.commit()
        cursor.close()
    return db


def write_file_info(filename, filetype):
    cursor = get_db().cursor()
    cursor.execute('''INSERT INTO files (date, filetype, filename, was_shown) VALUES (?,?,?,?)''',
                   (datetime.now(), filetype, filename, 0))
    get_db().commit()
    cursor.close()


def remove_file(filename):
    try:
        os.remove(filename)
    except Exception as e:
        logging.error("Can't delete file " + filename + ' reason: ' + str(e))


@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()


@auth.verify_token
def verify_token(token):
    if token in config["app"]["access_tokens"]:
        return True
    return False


@app.route('/')
def root():
    test = request.args.get("test")
    if test is not None:
        return app.send_static_file('index_test.html')
    else:
        return app.send_static_file('index.html')


@app.route('/js/<path:path>')
def send_js(path):
    return send_from_directory('js', path)


@app.route('/css/<path:path>')
def send_css(path):
    return send_from_directory('css', path)


@app.route('/photo/<path:path>')
def send_photo(path):
    return send_from_directory('photo', path)


@app.route('/video/<path:path>')
def send_video(path):
    return send_from_directory('video', path)


@app.route('/assets/<path:path>')
def send_assets(path):
    return send_from_directory('assets', path)


@app.route('/api/get_current_temp', methods=['GET'])
# @auth.login_required
def get_temp():
    try:
        with open(config['weather']['file_path'] + config['weather']['file_name'], 'r') as weatherfile:
            return jsonify(json.load(weatherfile))
    except Exception as e:
        return 'Error:' + str(e)


@app.route('/api/save_data', methods=['POST'])
# @auth.login_required
def save_data():
    try:
        base64data = request.json['data'].split(',')[1]
        if request.json['datatype'] == 'photo':
            try:
                tmp_filename = config["app"]["tmp_files_path"] + "tmp_" + str(uuid.uuid4()) + '.png'
                with open(tmp_filename, 'wb') as f_img:
                    f_img.write(base64.b64decode(base64data))

                new_filename = "photo_" + str(uuid.uuid4()) + '.png'
                new_filepath = config["photo_crop"]["path"] + new_filename

                result = run(args=[
                    config["app"]['ffmpeg_executable'],
                    "-i",
                    tmp_filename,
                    "-vf",
                    "scale=-1:{1},crop={0}:{1}:(in_w-{0})/2:0".format(config["photo_crop"]["dimensions"]["width"],
                                                                  config["photo_crop"]["dimensions"]["height"]),
                    new_filepath],
                    stdout=PIPE,
                    stderr=PIPE,
                    universal_newlines=True)
                logging.info("{0} {1} {2}".format(result.returncode, result.stdout, result.stderr))

                try:
                    os.remove(tmp_filename)
                except Exception as e:
                    logging.error('Error in removing tmp img file:' + str(e))

                logging.info('image file ' + new_filename + ' processed successfully')
            except Exception as e:
                logging.error('problem in image processing: ' + str(e))
        else:
            try:
                tmp_filename = config["app"]["tmp_files_path"] + "tmp_"+str(uuid.uuid4()) + '.webm'
                with open(tmp_filename, 'wb') as f_vid:
                    f_vid.write(base64.b64decode(base64data))

                new_filename = "video_"+str(uuid.uuid4()) + '.webm'
                new_filepath = config["video_crop"]["path"] + new_filename

                result = run(args=[
                        config["app"]['ffmpeg_executable'],
                        "-noautorotate",
                        "-i",
                        tmp_filename,
                        "-vf",
                        "scale=-1:{1},crop={0}:{1}:(in_w-{0})/2:0".format(config["video_crop"]["dimensions"]["width"],config["video_crop"]["dimensions"]["height"]),
                        "-strict",
                        "-2",
                        "-preset",
                        "ultrafast",
                        "-metadata:s:v",
                        "rotate=0",
                        "-fflags",
                        "+genpts",
                        new_filepath],
                        stdout=PIPE,
                        stderr=PIPE,
                        universal_newlines=True)
                logging.info("{0} {1} {2}".format(result.returncode,result.stdout, result.stderr))

                try:
                    os.remove(tmp_filename)
                except Exception as e:
                    logging.error('Error in removing tmp video file:' + str(e))
                    logging.info('image file ' + new_filename + ' processed successfully')
            except Exception as e:
                logging.error('problem in video processing: ' + str(e))

        write_file_info(new_filename, request.json['datatype'])
        return json.dumps({'success': True}), 200, {'ContentType': 'application/json'}
    except Exception as e:
        logging.error('Error in saving data:' + str(e))
        return json.dumps({'success': False}), 500, {'ContentType': 'application/json'}


@app.route('/api/get_item_to_show', methods=['GET'])
# @auth.login_required
def get_item_to_show():
    try:
        cursor = get_db().cursor()
        cursor.execute("SELECT filename, filetype FROM files WHERE was_shown = 0 ORDER BY date DESC LIMIT 1")
        filename, filetype = cursor.fetchone()
        cursor.close()
        return jsonify({'filename': filename, 'filetype': filetype})
    except:
        return json.dumps({'success': False}), 404, {'ContentType': 'application/json'}


@app.route('/api/was_shown/<string:filename>', methods=['GET'])
# @auth.login_required
def item_was_shown(filename):
    cursor = get_db().cursor()
    cursor.execute("UPDATE files SET was_shown = 1 WHERE filename = '" + filename + "'")
    get_db().commit()
    cursor.close()
    return json.dumps({'success': True}), 200, {'ContentType': 'application/json'}


if __name__ == '__main__':
    app.run()
