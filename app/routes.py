from flask import render_template, request, send_from_directory
import os
from app import app
from app.bin import find_fish
from app.bin import find_bugs
from app.bin import find_sea_creatures
from app.bin.get_tz import get_timezones

from datetime import datetime

northern_fishes = find_fish.load_northern()
southern_fishes = find_fish.load_southern()
northern_bugs = find_bugs.load_northern()
southern_bugs = find_bugs.load_southern()
northern_sea_creatures = find_sea_creatures.load_northern()
southern_sea_creatures = find_sea_creatures.load_southern()
print('Fish, bugs, and sea creatures loaded.')

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
            return render_template('critter-table.html', hemisphere=hemisphere, timezones=get_timezones(), timezone=timezone, critter_list=fish_list, title='Fish Fetcher', critterType='fish')
        return render_template('critter.html', timezones=get_timezones(), title='Fish Fetcher', critterType='fish')
    else:
        return render_template('critter.html', timezones=get_timezones(), title='Fish Fetcher', critterType='fish')

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
            return render_template('critter-table.html', hemisphere=hemisphere, timezones=get_timezones(), timezone=timezone, critter_list=bugs_list, title='Bug Bounties', critterType='bugs')
        return render_template('critter.html', timezones=get_timezones(), title='Bug Bounties', critterType='bugs')
    else:
        return render_template('critter.html', timezones=get_timezones(), title='Bug Bounties', critterType='bugs')

@app.route('/sea_creatures', methods=['GET', 'POST'])
def sea_creatures():
    if request.method == 'POST':
        hemisphere = request.form.get('hemisphere', None)
        timezone = request.form.get('timezone', None)
        if hemisphere != None and timezone != None:
            if hemisphere == 'Northern':
                sea_creatures_list = find_sea_creatures.main(timezone, northern_sea_creatures)
            else:
                sea_creatures_list = find_sea_creatures.main(timezone, southern_sea_creatures)
            return render_template('critter-table.html', hemisphere=hemisphere, timezones=get_timezones(), timezone=timezone, critter_list=sea_creatures_list, title='Sea Creature Search', critterType='sea_creatures')
        return render_template('critter.html', timezones=get_timezones(), title='Sea Creature Search', critterType='sea_creatures')
    else:
        return render_template('critter.html', timezones=get_timezones(), title='Sea Creature Search', critterType='sea_creatures')

@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path,'static'), 'favicon.ico', mimetype='image/vnd.microsoft.icon')

@app.route('/apple-touch-icon.png')
def apple_touch_icon():
    return send_from_directory(os.path.join(app.root_path,'static'), 'apple-touch-icon.png')

@app.route('/android-icon-192x192.png')
def android_icon():
    return send_from_directory(os.path.join(app.root_path,'static'), 'android-icon-192x192.png')