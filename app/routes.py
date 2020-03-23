from flask import render_template, request
from app import app
from app.bin import find_fish
from app.bin import find_bugs
from app.bin.get_tz import get_timezones

from datetime import datetime

northern_fishes = find_fish.load_northern()
southern_fishes = find_fish.load_southern()
northern_bugs = find_bugs.load_northern()
southern_bugs = find_bugs.load_southern()
print('Fish and bugs loaded.')

@app.route('/')
@app.route('/index')
def index():
    return render_template('index.html')

@app.route('/fish', methods=['GET', 'POST'])
def fish():
    if request.method == 'POST':
        hemisphere = request.form.get('hemisphere', None)
        timezone = request.form.get('timezone', None)
        if hemisphere != None and timezone != None:
            if hemisphere == 'Northern':
                fish_list = find_fish.main(timezone, northern_fishes)
            else:
                fish_list = find_fish.main(timezone, southern_fishes)
            return render_template('fish-table.html', hemisphere=hemisphere, timezones=get_timezones(), timezone=timezone, fish_list=fish_list)
        return render_template('fish.html', timezones=get_timezones())
    else:
        return render_template('fish.html', timezones=get_timezones())

@app.route('/bugs', methods=['GET', 'POST'])
def bugs():
    if request.method == 'POST':
        hemisphere = request.form.get('hemisphere', None)
        timezone = request.form.get('timezone', None)
        if hemisphere != None and timezone != None:
            if hemisphere == 'Northern':
                bugs_list = find_bugs.main(timezone, northern_bugs)
            else:
                bugs_list = find_bugs.main(timezone, southern_bugs)
            return render_template('bugs-table.html', hemisphere=hemisphere, timezones=get_timezones(), timezone=timezone, bugs_list=bugs_list)
        return render_template('bugs.html', timezones=get_timezones())
    else:
        return render_template('bugs.html', timezones=get_timezones())