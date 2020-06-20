#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
import dateutil.parser
import babel
import logging
import config

from flask import Flask, render_template, request, Response, flash, redirect, url_for, jsonify, abort
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import func
from flask_migrate import Migrate
from flask_wtf import Form
from logging import Formatter, FileHandler

from forms import *
from models import setup_db, Artist, Venue, Show
#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db = setup_db(app)

#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
  date = dateutil.parser.parse(value)
  if format == 'full':
      format="EEEE MMMM, d, y 'at' h:mma"
  elif format == 'medium':
      format="EE MM, dd, y h:mma"
  return babel.dates.format_datetime(date, format, locale='en')

app.jinja_env.filters['datetime'] = format_datetime

#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#

@app.route('/')
def index():
  return render_template('pages/home.html')


#  Venues
#  ----------------------------------------------------------------

@app.route('/venues')
def venues():

  data = []
  grouped_data = {}

  current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

  venues = Venue.query.group_by(Venue.id, Venue.state, Venue.city).all()

  for v in venues:
    num_upcoming_shows = v.shows.filter(Show.start_time > current_time).all()

    state_city = v.state + v.city

    if state_city in grouped_data:
      grouped_data[state_city]["venues"] += [{
        "id": v.id,
        "name": v.name,
        "num_upcoming_shows": len(num_upcoming_shows)
      }]

    else:
      grouped_data[state_city] = {
        "city": v.city,
        "state": v.state,
        "venues": [{
          "id": v.id,
          "name": v.name,
          "num_upcoming_shows": len(num_upcoming_shows)
          }
        ]
      }

  for key in grouped_data:
    data.append(grouped_data[key])

  return render_template('pages/venues.html', areas=data)

@app.route('/venues/search', methods=['POST'])
def search_venues():

  response = {}

  current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

  search = "%{}%".format(request.form.get("search_term"))

  search_result = Venue.query.filter(Venue.name.ilike(search)).all()

  response["count"] = len(search_result)
  response["data"] = []

  for v in search_result:
    upcoming_shows = v.shows.filter(Show.start_time > current_time).all()

    response["data"].append({
      "id": v.id,
      "name": v.name,
      "num_upcoming_shows": len(upcoming_shows)
    })

  return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):

  current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

  venue = Venue.query.filter_by(id=venue_id).one_or_none()

  if not venue:
    abort(404)

  formatted_venue = venue.format()

  past_shows = venue.shows.filter(Show.start_time < current_time).all()
  upcoming_shows = venue.shows.filter(Show.start_time > current_time).all()

  formatted_venue["past_shows_count"] = len(past_shows)
  formatted_venue["upcoming_shows_count"] = len(upcoming_shows)

  formatted_venue["past_shows"] = []
  formatted_venue["upcoming_shows"] = []


  for p in past_shows:
    formatted_venue["past_shows"].append(p.format())

  for u in upcoming_shows:
    formatted_venue["upcoming_shows"].append(u.format())

  return render_template('pages/show_venue.html', venue=formatted_venue)

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():

  error = False
  data = {}

  name = request.form.get('name')
  city = request.form.get('city')
  state = request.form.get('state')
  address = request.form.get('address')
  phone = request.form.get('phone')
  image_link = request.form.get('image_link')
  genres = request.form.getlist('genres')
  facebook_link = request.form.get('facebook_link')

  seeking_talent = False
  if 'seeking_talent' in request.form:
    seeking_talent = request.form['seeking_talent'] == 'y'

  seeking_description = request.form.get('seeking_description')

  website = request.form.get('website')

  try:
    v = Venue(name, city, state, address, phone, image_link, facebook_link, website, seeking_talent, seeking_description, genres)
    v.insert()

  except:
    error=True
    db.session.rollback()


  if error:
      flash('An error occurred. Venue ' + request.form['name'] + ' could not be listed.')
  else:
      flash('Venue ' + request.form['name'] + ' was successfully listed!')

  return render_template('pages/home.html')

@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):

  v = Venue.query.get(venue_id)

  if v:
    v.delete()

  return None


#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():

  data = []

  artists = Artist.query.all()

  for a in artists:
    data.append({
      "id": a.id,
      "name": a.name
    })

  return render_template('pages/artists.html', artists=data)

@app.route('/artists/search', methods=['POST'])
def search_artists():

  response = {}

  current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

  search = "%{}%".format(request.form.get("search_term"))

  search_result = Artist.query.filter(Artist.name.ilike(search)).all()

  response["count"] = len(search_result)
  response["data"] = []

  for a in search_result:
    upcoming_shows = a.shows.filter(Show.start_time > current_time).all()

    response["data"].append({
      "id": a.id,
      "name": a.name,
      "num_upcoming_shows": len(upcoming_shows)
    })

  return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):

  current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

  artist = Artist.query.filter_by(id=artist_id).one_or_none()

  if not artist:
    abort(404)

  formatted_artist = artist.format()

  past_shows = artist.shows.filter(Show.start_time < current_time).all()
  upcoming_shows = artist.shows.filter(Show.start_time > current_time).all()

  formatted_artist["past_shows_count"] = len(past_shows)
  formatted_artist["upcoming_shows_count"] = len(upcoming_shows)

  formatted_artist["past_shows"] = []
  formatted_artist["upcoming_shows"] = []


  for p in past_shows:
    formatted_artist["past_shows"].append(p.format())

  for u in upcoming_shows:
    formatted_artist["upcoming_shows"].append(u.format())

  print(formatted_artist)

  return render_template('pages/show_artist.html', artist=formatted_artist)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  form = ArtistForm()
  artist = Artist.query.filter_by(id=artist_id).one_or_none()

  if artist:
    artist = artist.format()
    form.name.data = artist["name"]
    form.city.data = artist["city"]
    form.state.data = artist["state"]
    form.phone.data = artist["phone"]
    form.facebook_link.data = artist["facebook_link"]
    form.image_link.data = artist["image_link"]
    form.seeking_venue.data = artist["seeking_venue"]
    form.seeking_description.data = artist["seeking_description"]
    form.website.data = artist["website"]
    form.genres.data = artist["genres"]

    return render_template('forms/edit_artist.html', form=form, artist=artist)

  return render_template('errors/404.html')


@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):

  error = False

  artist = Artist.query.filter_by(id=artist_id).one_or_none()

  name = request.form.get('name')
  city = request.form.get('city')
  state = request.form.get('state')
  phone = request.form.get('phone')
  image_link = request.form.get('image_link')
  genres = request.form.getlist('genres')
  facebook_link = request.form.get('facebook_link')

  seeking_venue = False
  if 'seeking_venue' in request.form:
    seeking_venue = request.form['seeking_venue'] == 'y'

  seeking_description = request.form.get('seeking_description')

  website = request.form.get('website')

  try:
    artist.name = name
    artist.city = city
    artist.state = state
    artist.phone = phone
    artist.image_link = image_link
    artist.genres = genres
    artist.facebook_link = facebook_link
    artist.seeking_venue = seeking_venue
    artist.seeking_description = seeking_description
    artist.website = website

    artist.update()

  except:
    error=True
    db.session.rollback()

  if error:
      flash('An error occurred. Artist ' + request.form['name'] + ' could not be edited.')
  else:
      flash('Artist ' + request.form['name'] + ' was successfully edited!')

  return redirect(url_for('show_artist', artist_id=artist_id))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  form = VenueForm()

  venue = Venue.query.filter_by(id=venue_id).one_or_none()

  if venue:
    venue = venue.format()
    form.name.data = venue["name"]
    form.address.data = venue["address"]
    form.city.data = venue["city"]
    form.state.data = venue["state"]
    form.phone.data = venue["phone"]
    form.facebook_link.data = venue["facebook_link"]
    form.image_link.data = venue["image_link"]
    form.seeking_talent.data = venue["seeking_talent"]
    form.seeking_description.data = venue["seeking_description"]
    form.website.data = venue["website"]
    form.genres.data = venue["genres"]

    return render_template('forms/edit_venue.html', form=form, venue=venue)

  return render_template('errors/404.html')

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):

  error = False

  venue = Venue.query.filter_by(id=venue_id).one_or_none()

  name = request.form.get('name')
  city = request.form.get('city')
  state = request.form.get('state')
  address = request.form.get('address')
  phone = request.form.get('phone')
  image_link = request.form.get('image_link')
  genres = request.form.getlist('genres')
  facebook_link = request.form.get('facebook_link')

  seeking_talent = False
  if 'seeking_talent' in request.form:
    seeking_talent = request.form['seeking_talent'] == 'y'

  seeking_description = request.form.get('seeking_description')

  website = request.form.get('website')

  try:
    venue.name = name
    venue.city = city
    venue.state = state
    venue.address = address
    venue.phone = phone
    venue.image_link = image_link
    venue.genres = genres
    venue.facebook_link = facebook_link
    venue.seeking_talent = seeking_talent
    venue.seeking_description = seeking_description
    venue.website = website

    venue.update()

  except:
    error=True
    db.session.rollback()

  if error:
      flash('An error occurred. Venue ' + request.form['name'] + ' could not be edited.')
  else:
      flash('Venue ' + request.form['name'] + ' was successfully edited!')

  return redirect(url_for('show_venue', venue_id=venue_id))

#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():

  error = False

  name = request.form.get('name')
  city = request.form.get('city')
  state = request.form.get('state')
  phone = request.form.get('phone')
  image_link = request.form.get('image_link')
  genres = request.form.getlist('genres')
  facebook_link = request.form.get('facebook_link')

  seeking_venue = False
  if 'seeking_venue' in request.form:
    seeking_venue = request.form['seeking_venue'] == 'y'

  seeking_description = request.form.get('seeking_description')

  website = request.form.get('website')

  try:
    a = Artist(name, city, state, phone, image_link, facebook_link, website, seeking_venue, seeking_description, genres)
    a.insert()

  except:
      error=True
      db.session.rollback()


  if error:
      flash('An error occurred. Artist ' + request.form['name'] + ' could not be listed.')
  else:
      flash('Artist ' + request.form['name'] + ' was successfully listed!')

  return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():

  data = []

  shows = Show.query.all()

  if not shows:
    abort(404)

  for s in shows:
    data.append(s.format())


  return render_template('pages/shows.html', shows=data)

@app.route('/shows/create')
def create_shows():
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():

  error = False

  artist_id = request.form.get('artist_id')
  venue_id = request.form.get('venue_id')
  start_time = request.form.get('start_time')

  print(venue_id, artist_id, start_time)

  try:
    s = Show(venue_id, artist_id, start_time)
    s.insert()

  except:
      error=True
      db.session.rollback()

  if error:
      flash('An error occurred. Show could not be listed.')
  else:
      flash('Show was successfully listed!')

  return render_template('pages/home.html')

@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404

@app.errorhandler(500)
def server_error(error):
    return render_template('errors/500.html'), 500


if not app.debug:
    file_handler = FileHandler('error.log')
    file_handler.setFormatter(
        Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
    )
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info('errors')

#----------------------------------------------------------------------------#
# Launch.
#----------------------------------------------------------------------------#

# Default port:
if __name__ == '__main__':
    app.run()

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''
