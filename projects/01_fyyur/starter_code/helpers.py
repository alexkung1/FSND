from datetime import datetime
# from app import Genre, Artist, Venue, Show

def retrieve_upcoming_shows(shows):
    return [show for show in shows if show.start_time >= datetime.today()]

def retrieve_past_shows(shows):
    return [show for show in shows if show.start_time <= datetime.today()]

def transform_show(show, output_format="artist"):
    if output_format=="artist":
        return {
            "artist_id": show.artist_id,
            "artist_name": show.artist.name,
            "artist_image_link": show.artist.image_link,
            "start_time": show.start_time
        }
    elif output_format=="show":
        return {
            "venue_id": show.venue_id,
            "venue_name": show.venue.name,
            "artist_id": show.artist_id,
            "artist_name": show.artist.name,
            "artist_image_link": show.artist.image_link,
            "start_time": show.start_time
        }
    else:
        return {
            "venue_id":show.venue_id,
            "venue_name": show.venue.name,
            "venue_image_link": show.venue.image_link,
            "start_time": show.start_time
        }

def transform_genres(genres):
    if genres:
        if type(genres) == list:
            return ' '.join(genres)
        else:
            return genres.split()
    else:
        return genres

# def replace_genres(model, genre_list):
#     model.genres.clear()
#     model.genres.extend(genre_list)

# def parse_genres(genre_list):
#     genres = [Genre.query.filter(Genre.name.ilike(genre)).first() for genre in genre_list]
#     return [genre for genre in genres if genre]

def transform_artist_detail(artist):
    past_shows = retrieve_past_shows(artist.shows)
    upcoming_shows = retrieve_upcoming_shows(artist.shows)
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

def safe_commit_session(model, db):
    error = False
    try:
        db.session.add(model)
        db.session.commit()
    except Exception as e:
        error = True
        db.session.rollback()
    finally:
        db.session.close()
        return error