from flask import Flask, flash, redirect, render_template, request, session, abort 

import pickle
import sys
import spotipy
import spotipy.util as util
import random
from music_data import authenticate_spotify, top_artists, top_tracks, followed_artists, saved_tracks, playlist_tracks, playlist_yaml_dump,recommendation_tracks
from modele import recommendation_tracks_uni, create_playlist, get_X_y, random_forest_model, create_playlist



client_id = "a811ca65f86749e385a0426469546013"
client_secret = "499683208dac4b1487cfbc47bf90cbc3"
redirect_uri = "http://localhost:8888/callback"

scope = 'user-library-read user-top-read playlist-modify-public user-follow-read playlist-modify-private'




app = Flask(__name__)

@app.route('/')
def my_form():
    return render_template('input.html')


@app.route("/", methods=['POST'])
def recomendify():
    from music_data import authenticate_spotify, top_artists, top_tracks, followed_artists, saved_tracks, playlist_tracks, playlist_yaml_dump,recommendation_tracks
    from modele import recommendation_tracks_uni, create_playlist, get_X_y, random_forest_model, create_playlist
 
    spotify_auth = authenticate_spotify(client_id, client_secret, redirect_uri, scope)
    top_tracks = top_tracks(spotify_auth)
    followed_artists = followed_artists(spotify_auth)
    saved_tracks = saved_tracks(spotify_auth)
    playlist_tracks = playlist_tracks(spotify_auth)
    playlist_yaml_dump = playlist_yaml_dump(playlist_tracks)
    recommendation_tracks =  recommendation_tracks(playlist_tracks)
    recommendation_tracks_uni = recommendation_tracks_uni(playlist_tracks, recommendation_tracks)
    get_X_y = get_X_y(recommendation_tracks_uni)
    random_forest_model = random_forest_model(get_X_y, recommendation_tracks_uni)
    playlist = create_playlist(random_forest_model)
    return render_template('playlist.html', playlist=playlist )


if __name__ == "__main__":

	app.run(host='0.0.0.0')
