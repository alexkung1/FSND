#----------------------------------------------------------------------------#
# Model-independent helper functions.
#----------------------------------------------------------------------------#

# Transform show model into appropriate output format
#   params: show, output_format
#   where output_format is one of 'artist', 'show' or any
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


# given a transient model and the corresponding db instance
# commit the model to the db and return the success of the transaction
def safe_commit_session(model, db):
    error = False
    try:
        db.session.add(model)
        db.session.commit()
    except:
        error = True
        db.session.rollback()
    finally:
        db.session.close()
        return error