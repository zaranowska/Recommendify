import spotipy
import yaml
from spotipy.oauth2 import SpotifyOAuth
from data_functions import offset_api_limit, get_artists_df, get_tracks_df, get_track_audio_df,\
    get_all_playlist_tracks_df, get_recommendations



client_id = "a811ca65f86749e385a0426469546013"
client_secret = "499683208dac4b1487cfbc47bf90cbc3"
redirect_uri = "http://localhost:8888/callback"


scope = "user-library-read user-follow-read user-top-read playlist-read-private"

def authenticate_spotify(client_id, client_secret, redirect_uri, scope):
    sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
        client_id=client_id,
        client_secret=client_secret,
        redirect_uri=redirect_uri,
        scope=scope))
    return sp


def top_artists(sp):
    top_artists = offset_api_limit(sp, sp.current_user_top_artists())
    top_artists_df = get_artists_df(top_artists)
    top_artists_df.to_pickle("top_artists.pkl")
    return top_artists_df

def followed_artists(sp):
    followed_artists = offset_api_limit(sp, sp.current_user_followed_artists())
    followed_artists_df = get_artists_df(followed_artists)
    followed_artists_df.to_pickle("followed_artists.pkl")
    return followed_artists_df

def top_tracks(sp):
    top_tracks = offset_api_limit(sp, sp.current_user_top_tracks())
    top_tracks_df = get_tracks_df(top_tracks)
    top_tracks_df = get_track_audio_df(sp, top_tracks_df)
    top_tracks_df.to_pickle("top_tracks.pkl")
    return top_tracks_df

def saved_tracks(sp):
    saved_tracks = offset_api_limit(sp, sp.current_user_saved_tracks())
    saved_tracks_df = get_tracks_df(saved_tracks)
    saved_tracks_df = get_track_audio_df(sp, saved_tracks_df)
    saved_tracks_df.to_pickle("saved_tracks.pkl")
    return saved_tracks_df

def playlist_tracks(sp):
    playlist_tracks_df = get_all_playlist_tracks_df(sp, sp.current_user_playlists())  # limit of 50 playlists by default
    playlist_tracks_df = get_track_audio_df(sp, playlist_tracks_df)
    playlist_tracks_df.to_pickle("playlist_tracks.pkl")
    return playlist_tracks_df


def playlist_yaml_dump(playlist_tracks_df):
    playlist_dict = dict(zip(playlist_tracks_df['playlist_name'], playlist_tracks_df['playlist_id']))
    with open('playlists.yml', 'w') as outfile:
        yaml.dump(playlist_dict, outfile, default_flow_style=False)

def recommendation_tracks(sp, playlist_tracks_df):
 
    recommendation_tracks = get_recommendations(sp, playlist_tracks_df[playlist_tracks_df['playlist_name'].isin(
     ["Your Top Songs 2022", 'Chill', 'Top Metal', 'Top Pop', 'Dark&Gothic']
                 )].drop_duplicates(subset='id', keep="first")['id'].tolist())
    recommendation_tracks_df = get_tracks_df(recommendation_tracks)
    recommendation_tracks_df = get_track_audio_df(sp, recommendation_tracks_df)
    recommendation_tracks_df.to_pickle("recommendation_tracks.pkl")
    return recommendation_tracks_df
