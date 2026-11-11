# New Horizons Critter Catcher

Small web app that takes user's current time and calculates what bugs and fish are available in Animal Crossing New Horizon.\
Built using Flask.

It is currently hosted on:
- [Vercel](https://critter-catcher.vercel.app/)
- [Heroku](https://critter-catcher-3aba88585161.herokuapp.com) on a Hobby dyno!

## Features

- Live availability for all 200 Critterpedia entries, with your time zone detected automatically and the hemisphere guessed from it
- Plan ahead by picking any month and hour
- Every card shows the season, active hours, shadow size, price (plus what C.J. or Flick pay), weather, and how many catches unlock it
- "New this month" and "Last chance" lists
- A Critterpedia tracker: mark critters as caught (saved in your browser) and hide the ones you have
- Search, filters, sorting, dark mode, and a mobile layout

## Installation

Requires Python 3.10 or newer (the deployed app runs Python 3.12, pinned in `.python-version`).

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```
On Windows, activate with `.venv\Scripts\activate` instead.

Then, to start local server, it is:
```bash
flask run
```

Then go to [localhost:5000](http://localhost:5000) to visit the web app!

To run the tests:
```bash
python -m unittest
```

## Data

Critter data lives in `app/data/` with one row per Critterpedia entry and Northern Hemisphere months (the format is described at the top of `app/critters.py`). It was checked against [Nookipedia](https://nookipedia.com/) in November 2026.

## Contributing
Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

## License
[MIT](https://choosealicense.com/licenses/mit/)
