from flask import Flask, render_template, url_for, request, redirect, make_response, session
import random
import json
import time
import os 
from datetime import datetime
from telespy import data_for_build_graph

app_flask = Flask(__name__)
app_flask.secret_key = '73870e7f-634d-433b-946a-8d20132bafac'

@app_flask.route('/', methods=['GET', 'POST'])
def index():
    if request.method=='POST':
        directory = request.form['directory']
        path = os.getcwd() + '\\' + directory
        not_exist_directory = False
        if not os.path.isdir(path):
            not_exist_directory = True
            return render_template('index.html', not_exist_directory=not_exist_directory)
        else:
            not_exist_directory = False
            user1 = directory.split('_+_')[0]
            user2 = directory.split('_+_')[1]
            session['data'] = dict(username1=user1, username2=user2, username_concat=directory)
            return redirect(url_for('graphs'))
    return render_template('index.html')

@app_flask.route('/graphs', methods=['GET', 'POST'])
def graphs():
    username1 = session.get('data')['username1']
    username2 = session.get('data')['username2']
    username_concat = session.get('data')['username_concat']
    summary = data_chance(username_concat, username_concat)[0]
    str_chance = data_chance(username_concat, username_concat)[1]
    if summary and str_chance:
        return render_template('graphs.html', username1=username1, username2=username2, username_concat=username_concat, summary=summary, str_chance=str_chance)
    else:
        return render_template('graphs.html', username1=username1, username2=username2, username_concat=username_concat)


@app_flask.route('/data_chance/<username>:<username_concat>', methods=["GET", "POST"])
def data_chance(username, username_concat):
    file_csv_name = os.getcwd() + '\\' + '{}'.format(username_concat) + '\\' + 'intersect_{}.csv'.format(username_concat)
    data = data_for_build_graph(file_csv_name)
    return data[1], data[2]

@app_flask.route('/data/<username>:<username_concat>', methods=["GET", "POST"])
def data(username, username_concat):
    if '+' in username:
        file_csv_name = os.getcwd() + '\\' + '{}'.format(username_concat) + '\\' + 'intersect_{}.csv'.format(username_concat)
        data = data_for_build_graph(file_csv_name)
    else:
        file_csv_name = os.getcwd() + '\\' + '{}'.format(username_concat) + '\\' + '{}_online.csv'.format(username)
        data = data_for_build_graph(file_csv_name)
    response = make_response(json.dumps(data[0]))
    response.content_type = 'application/json'
    return response


if __name__ == '__main__':
    app_flask.run(debug=True)