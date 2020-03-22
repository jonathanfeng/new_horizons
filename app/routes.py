from flask import render_template
from app import app
from app.bin.find_fish import main as fishes

from datetime import datetime


@app.route('/')
@app.route('/index')
def index():
    return render_template('index.html')

@app.route('/fish')
def fish():
    return render_template('fish.html')

@app.route('/fish/n')
def fish_n():
    fish_list = fishes('n')
    current_time = datetime.now()
    return render_template('fish-n.html', fish_list=fish_list, current_time=current_time)

@app.route('/fish/s')
def fish_s():
    fish_list = fishes('s')
    return render_template('fish-n.html', fish_list = fish_list)