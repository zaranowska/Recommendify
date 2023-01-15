import pandas as pd
import yaml
from sklearn.model_selection import train_test_split, StratifiedKFold, GridSearchCV
from sklearn.metrics import classification_report
from sklearn.ensemble import RandomForestClassifier
import pickle
import spotipy 
from spotipy.oauth2 import SpotifyOAuth


top_artist_df = pd.read_pickle("top_artists.pkl")
followed_artists_df = pd.read_pickle("followed_artists.pkl")
top_tracks_df = pd.read_pickle("top_tracks.pkl")
saved_tracks_df = pd.read_pickle("saved_tracks.pkl")
playlist_tracks_df = pd.read_pickle("playlist_tracks.pkl")
recommendation_tracks_df = pd.read_pickle("recommendation_tracks.pkl")



def recommendation_tracks_uni(playlist_tracks_df, recommendation_tracks_df):
    playlist_tracks_df = playlist_tracks_df.drop_duplicates(subset='id', keep="first").reset_index()
    recommendation_tracks_df = recommendation_tracks_df.drop_duplicates(subset='id', keep="first").reset_index()

    recommendation_tracks_df = recommendation_tracks_df[~recommendation_tracks_df['id'].isin(playlist_tracks_df['id'].tolist())]
    return recommendation_tracks_df



def get_X_y(recommendation_tracks_uni):
    with open("playlists.yml", 'r') as stream:
        playlists = yaml.safe_load(stream)
    playlist_tracks_df = pd.read_excel('pt_df.xlsx')
    
    playlist_tracks_df['ratings'] = playlist_tracks_df['playlist_id'].apply(lambda x: 1 if x in playlists.values() else 0)
    playlist_tracks_df['ratings']
    

    X = playlist_tracks_df[['popularity',  'duration_ms', 'danceability', 'energy',
                            'key', 'loudness', 'mode', 'speechiness', 'acousticness', 'instrumentalness',
                            'liveness', 'valence', 'tempo', 'time_signature', 'genres']]  # order here is important for xgboost later
    y = playlist_tracks_df['ratings']
    

    X = X.dropna()
    return X, y
def random_forest_model(X, y, recommendation_tracks_uni):
    X, y = get_X_y(recommendation_tracks_uni)
    recommendation_tracks_uni = recommendation_tracks_uni.dropna()
    

    X = X.drop('genres', 1).join(X['genres'].str.join('|').str.get_dummies())
    X_recommend = recommendation_tracks_uni.copy()
    X_recommend = X_recommend.drop('genres', 1).join(X_recommend['genres'].str.join('|').str.get_dummies())
    
 
    X = X[X.columns.intersection(X_recommend.columns)]
    X_recommend = X_recommend[X_recommend.columns.intersection(X.columns)]
    

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    X_train.head()
    
 
    rfc = RandomForestClassifier(n_estimators = 1000, random_state=42)
    rfc_gcv_parameters = {'min_samples_leaf': [1, 3, 5, 8], 
                          'max_depth': [3, 4, 5, 8, 12, 14], 
                         }
    rfe_gcv = GridSearchCV(rfc, rfc_gcv_parameters, n_jobs=-1, cv=StratifiedKFold(2), verbose=1, scoring='roc_auc')
    rfe_gcv.fit(X_train, y_train)
    rfe_gcv.best_estimator_, rfe_gcv.best_score_
    
    
    print(classification_report(y_test, rfe_gcv.predict(X_test)))
    



    pickle.dump(rfe_gcv ,open('music_classifier.pkl','wb'))

 
    recommendation_tracks_df['ratings'] = rfe_gcv.predict(X_recommend)
    recommendation_tracks_df['prob_ratings'] = rfe_gcv.predict_proba(X_recommend)[:,1]  # slice for probability of 1
    recommendation_tracks_df[recommendation_tracks_df['ratings'] == 1].head()
    
    tracks_to_add = recommendation_tracks_df[recommendation_tracks_df['prob_ratings'] >= 0.9]['id']

    return tracks_to_add



def create_playlist(tracks_to_add):
    scope = "playlist-modify-private"
    
    sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
        client_id = "a811ca65f86749e385a0426469546013",
        client_secret = "499683208dac4b1487cfbc47bf90cbc3",
        redirect_uri = "https://localhost:8008/callback",
        scope=scope,
    ))
    user='bt23protein'
  
    new_playlist = sp.user_playlist_create(user, 
                                           name="Polec sobie piosenki",
                                           public=False, 
                                           collaborative=False)

    for id in tracks_to_add:
        sp.user_playlist_add_tracks(user, 
                                    playlist_id=new_playlist['id'], 
                                    tracks=[id])