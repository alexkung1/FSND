#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for, abort
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from flask_migrate import Migrate
from datetime import datetime
from forms import *
from helpers import *
#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:password@localhost:5432/fyyur'
db = SQLAlchemy(app)
# TODO: connect to a local postgresql database

migrate = Migrate(app, db)

#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#


artist_genres = db.Table('artist_genres',
    db.Column('artist_id', db.Integer, db.ForeignKey('artists.id'), primary_key=True),
    db.Column('genre_id', db.Integer, db.ForeignKey('genres.id'), primary_key=True)
    )

venue_genres = db.Table('venue_genres',
    db.Column('venue_id', db.Integer, db.ForeignKey('venues.id'), primary_key=True),
    db.Column('genre_id', db.Integer, db.ForeignKey('genres.id'), primary_key=True)
    )

class Venue(db.Model):
    __tablename__ = 'venues'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    address = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))

    website = db.Column(db.String(120))
    seeking_talent = db.Column(db.Boolean)
    seeking_description = db.Column(db.String())
    genres = db.relationship('Genre', secondary=venue_genres, backref=db.backref('venues', lazy=True))

    shows = db.relationship("Show", back_populates="venue")
    
    def __repr__(self):
      return self.name

    # TODO: implement any missing fields, as a database migration using Flask-Migrate

class Artist(db.Model):
    __tablename__ = 'artists'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    seeking_venue = db.Column(db.Boolean, default=False)
    shows = db.relationship("Show", back_populates="artist")
    genres = db.relationship('Genre', secondary=artist_genres, backref=db.backref('artists', lazy=True))

    # TODO: implement any missing fields, as a database migration using Flask-Migrate

class Genre(db.Model):
  __tablename__ = 'genres'
  id = db.Column(db.Integer, primary_key=True)
  name = db.Column(db.String, nullable=False)

  def __repr__(self):
    return self.name

class Show(db.Model):
  __tablename__ = 'shows'
  venue_id = db.Column(db.Integer, db.ForeignKey('venues.id'), primary_key=True)
  artist_id = db.Column(db.Integer, db.ForeignKey('artists.id'), primary_key=True)
  venue = db.relationship("Venue", back_populates="shows")
  artist = db.relationship("Artist", back_populates="shows")
  start_time = db.Column(db.DateTime, nullable=False, default=datetime.utcnow(), primary_key=True)

  def __repr__(self):
    try:
      return "<({}){} - ({}){}>".format(self.venue.id,self.venue.name[:10], self.artist.id,self.artist.name[:10])
    except:
      return super.__repr__(self)

# TODO Implement Show and Artist models, and complete all model relationships and properties, as a database migration.


  


#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
  if type(value) != datetime:
    date = dateutil.parser.parse(value)
  else:
    date = value
  if format == 'full':
      format="EEEE MMMM, d, y 'at' h:mma"
  elif format == 'medium':
      format="EE MM, dd, y h:mma"
  return babel.dates.format_datetime(date, format)

app.jinja_env.filters['datetime'] = format_datetime

#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#

@app.route('/')
def index():
  return render_template('pages/home.html')

#----------------------------------------------------------------------------#
# Helper Functions.
#----------------------------------------------------------------------------#

# given a model with a genres association and a list of string genres,
# set the genres associated with the model to the corresponding instrumented
# list of Genre objects
def set_genre_list(model, genre_list):
  # gets a genre by name, if no corresponding genre is found, the genre is
  # created
  def get_or_create_genre(genre_name):
    genre = Genre.query.filter(Genre.name.ilike('%{}%'.format(genre_name))).first()
    if genre:
      return genre
    else:
      return Genre(name=genre_name)

  model.genres.clear()
  genre_list = [get_or_create_genre(genre) for genre in genre_list]
  model.genres.extend(genre_list)

def retrieve_upcoming_shows(filter_kwargs):
  return Show.query.filter_by(**filter_kwargs).filter(Show.start_time >= datetime.now()).all()

def retrieve_past_shows(filter_kwargs):
  return Show.query.filter_by(**filter_kwargs).filter(Show.start_time < datetime.now()).all()

def transform_artist_detail(artist):
    past_shows = retrieve_past_shows({"artist": artist})
    upcoming_shows = retrieve_upcoming_shows({"artist": artist})
    return {
        "id": artist.id,
        "name": artist.name,
        "genres": artist.genres,
        "city": artist.city,
        "state": artist.state,
        "phone": artist.phone,
        "seeking_venue": artist.seeking_venue,
        "image_link": artist.image_link,
        "facebook_link": artist.facebook_link,
        "past_shows": [transform_show(show, "venue") for show in past_shows],
        "upcoming_shows": [transform_show(show, "venue") for show in upcoming_shows],
        "past_shows_count": len(past_shows),
        "upcoming_shows_count": len(upcoming_shows),
    }

#  Venues
#  ----------------------------------------------------------------

@app.route('/venues')
def venues():

  all_venues = Venue.query.all()

  data = []

  for venue in all_venues:
    was_added = False
    # Add num_upcoming_shows
    parsed_venue = {
      "id": venue.id,
      "name": venue.name,
      "num_upcoming_shows": len(retrieve_upcoming_shows({"venue": venue}))
    }
    for i in range(len(data)):
      location = data[i]
      if location["city"] == venue.city and location["state"] == venue.state:        
        data[i]["venues"].append(parsed_venue)
        was_added = True

    if not was_added:    
      data.append({
        "city": venue.city,
        "state": venue.state,
        "venues": [
          parsed_venue
        ]
      })
         
  return render_template('pages/venues.html', areas=data);

@app.route('/venues/search', methods=['POST'])
def search_venues():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for Hop should return "The Musical Hop".
  # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"

  search_term=request.form.get('search_term', '')

  matching_venues= Venue.query.filter(Venue.name.ilike('%{}%'.format(search_term))).all()

  response={
    "count": len(matching_venues),
    "data": [{"id": venue.id, "name": venue.name, "num_upcoming_shows": len(retrieve_upcoming_shows({ "venue":venue }))} for venue in matching_venues]
  }
  return render_template('pages/search_venues.html', results=response, search_term=search_term)

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  # shows the venue page with the given venue_id
  # TODO: replace with real venue data from the venues table, using venue_id

  venue = Venue.query.get(venue_id)
  if not venue:
    return abort(404)
  past_shows = retrieve_past_shows({"venue": venue })
  upcoming_shows = retrieve_upcoming_shows({ "venue": venue })
  data = {
    "id": venue.id,
    "name": venue.name,
    "genres": venue.genres,
    "address": venue.address,
    "city": venue.city,
    "state": venue.state,
    "phone": venue.phone,
    "website": venue.website,
    "facebook_link": venue.facebook_link,
    "seeking_talent": venue.seeking_talent,
    "image_link": venue.image_link,
    "past_shows": [transform_show(show) for show in past_shows],
    "upcoming_shows": [transform_show(show) for show in upcoming_shows],
    "past_shows_count": len(past_shows),
    "upcoming_shows_count": len(upcoming_shows),
  }
  return render_template('pages/show_venue.html', venue=data)

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
  # TODO: insert form data as a new Venue record in the db, instead
  # TODO: modify data to be the data object returned from db insertion
  
  data = {
   key: request.form.get(key) for key in request.form if key != 'genres'
  }
  venue = Venue(**data)
  set_genre_list(venue, request.form.getlist('genres'))

  error=False
  safe_commit_session(venue, db)

  # on successful db insert, flash success
  if not error:
    flash('Venue ' + request.form['name'] + ' was successfully listed!')
  else:
    flash('An error occurred. Venue ' + data.name + ' could not be listed.')
  # TODO: on unsuccessful db insert, flash an error instead.
  
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
  return render_template('pages/home.html')

@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):

  venue = Venue.query.get(venue_id)
  error = False
  try:
    db.session.delete(venue)
    db.session.commit()
  except:
    error = True
    db.session.rollback()
  finally:
    db.session.close()

  if error:
    flash('An error occurred. Venue ' + venue.name + ' could not be deleted.')
  else:
    flash('Venue ' + venue.name + ' deleted successfully.')
  # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage
  return render_template('pages/home.html')

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  data=[{
    "id": artist.id,
    "name": artist.name,
  } for artist in Artist.query.all()]
  return render_template('pages/artists.html', artists=data)

@app.route('/artists/search', methods=['POST'])
def search_artists():

  search_term=request.form.get('search_term', '')

  matching_artists= Artist.query.filter(Artist.name.ilike('%{}%'.format(search_term))).all()

  response={
    "count": len(matching_artists),
    "data": [{
      "id": artist.id,
      "name": artist.name,
      "num_upcoming_shows": len(retrieve_upcoming_shows({ "artist": artist })),
    } for artist in matching_artists]
  }
  return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):

  artist = Artist.query.get(artist_id)
  if not artist:
    return abort(404)
  data = transform_artist_detail(artist)
  return render_template('pages/show_artist.html', artist=data)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  form = ArtistForm()
  artist = Artist.query.get(artist_id)
  artist_data=transform_artist_detail(artist)
  # TODO: populate form with fields from artist with ID <artist_id>
  return render_template('forms/edit_artist.html', form=form, artist=artist_data)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  # TODO: take values from the form submitted, and update existing
  # artist record with ID <artist_id> using the new attributes
  form = request.form
  artist = Artist.query.get(artist_id)
  artist.name = form.get('name', artist.name)
  artist.city = form.get('city', artist.city)
  artist.state = form.get('state', artist.state)
  artist.phone = form.get('phone', artist.phone)
  artist.facebook_link = form.get('facebook_link', artist.facebook_link)
  set_genre_list(artist, form.getlist('genres'))
  error = safe_commit_session(artist, db)
  if not error:
    artist = Artist.query.get(artist_id)
    flash('Artist ' + artist.name + ' edited successfully.')
  else:
    flash('Unable to edit artist ' + artist.name)

  return redirect(url_for('show_artist', artist_id=artist_id))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  form = VenueForm()
  
  venue = Venue.query.get(venue_id)

  # TODO: populate form with values from venue with ID <venue_id>
  return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  # TODO: take values from the form submitted, and update existing
  # venue record with ID <venue_id> using the new attributes
  venue = Venue.query.get(venue_id)
  if not venue:
    return abort(404)
  form = request.form
  venue.name = form.get('name', venue.name)
  venue.phone = form.get('phone', venue.phone)
  venue.address = form.get('address', venue.address)
  venue.city = form.get('city', venue.city)
  venue.state = form.get('state', venue.state)
  venue.facebook_link = form.get('facebook_link', venue.facebook_link)
  set_genre_list(venue, form.getlist('genres'))

  error=False
  safe_commit_session(venue, db)

  # on successful db insert, flash success
  if not error:
    flash('Venue ' + form.get('name') + ' was successfully listed!')
  else:
    flash('An error occurred. Venue ' + form.get('name') + ' could not be listed.')
  return redirect(url_for('show_venue', venue_id=venue_id))

#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
  # called upon submitting the new artist listing form
  form = request.form
  artist_data = {
    key: form.get(key) for key in form if key != 'genres'
  }
  artist = Artist(**artist_data)
  import pdb; pdb.set_trace()
  set_genre_list(artist, form.getlist('genres'))

  error = safe_commit_session(artist, db)
  if error:
    flash('Unable to add artist ' + artist_data.get("name"))
  else:
    flash('Artist ' + request.form['name'] + ' was successfully listed!')
  return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  # displays list of shows at /shows
  # TODO: replace with real venues data.
  #       num_shows should be aggregated based on number of upcoming shows per venue.
  data=[transform_show(show, "show") for show in Show.query.all()]
  return render_template('pages/shows.html', shows=data)

@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  # called to create new shows in the db, upon submitting new show listing form
  # TODO: insert form data as a new Show record in the db, instead
  form = request.form
  show = Show(artist_id=form.get('artist_id'), venue_id=form.get('venue_id'), start_time=form.get('start_time'))

  error = safe_commit_session(show,db)
  if error:
    flash('Unable to add show')
  else:
    # on successful db insert, flash success
    flash('Show was successfully listed!')
  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Show could not be listed.')
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
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
