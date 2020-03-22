from flask import render_template, request
from app import app
from app.bin.find_fish import main as fishes
from app.bin.get_tz import get_timezones
import pytz

from datetime import datetime

tz = ''

@app.route('/')
@app.route('/index')
def index():
    return render_template('index.html')

@app.route('/fish')
def fish():
    return render_template('fish.html', timezones = get_timezones())

@app.route('/fish/', methods=['GET', 'POST'])
def selected_fish():
    if request.method == 'POST':
        hemisphere = request.form.get('hemisphere', None)
        timezone = request.form.get('timezone', None)
        if hemisphere != None and timezone != None:
            fish_list = fishes(hemisphere, timezone)
            return render_template('fish-n.html', hemisphere=hemisphere, timezones = get_timezones(), timezone=timezone, fish_list = fish_list)
        return render_template('fish.html', timezones = get_timezones(), hemisphere=hemisphere, timezone=timezone)