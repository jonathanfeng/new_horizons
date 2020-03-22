from flask import render_template
from app import app
from app.bin import find_fish


@app.route('/')
@app.route('/index')
def index():
    return render_template('index.html')

@app.route('/fish')
def fish():
    return render_template('fish.html')

@app.route('/fish/n')
def fish_n():
    fish_list = find_fish.main('n')
    return render_template('fish-n.html', fish_list=fish_list)

@app.route('/fish/s')
def fish_s():
    return 'south'