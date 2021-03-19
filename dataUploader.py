import os

import google_auth_oauthlib.flow
import googleapiclient.discovery
import googleapiclient.errors

import pandas as pd
import csv

def getAnalytics(ChannelID, savePath = None, language = 'Russian'):

    if(language.lower() == 'russian'):
        encoding = 'windows-1251'
    else:
        encoding = 'UTF-8'
    if(savePath is None):
        savePath = 'analytics.csv'
    
    scopes = ["https://www.googleapis.com/auth/youtube.readonly"]

    # Disable OAuthlib's HTTPS verification when running locally.
        # *DO NOT* leave this option enabled in production.
    os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"

    api_service_name = "youtube"
    api_version = "v3"
    client_secrets_file = "client_secret_570633768588-l7plk9ljl5s7hob8lts3roetiouv4qob.apps.googleusercontent.com.json"

        # Get credentials and create an API client
    flow = google_auth_oauthlib.flow.InstalledAppFlow.from_client_secrets_file(
        client_secrets_file, scopes)
    credentials = flow.run_console()
    youtube = googleapiclient.discovery.build(
        api_service_name, api_version, credentials=credentials)


    def getUploadsID(ChannelID):
        request = youtube.channels().list(
            part="contentDetails,snippet,topicDetails,contentOwnerDetails",
            id=ChannelID
        )
        response = request.execute()

        UploadsID = response['items'][0]['contentDetails']['relatedPlaylists']['uploads']
        return UploadsID

    def getPlaylists(UploadsID):
        playlists = []
        nextPageToken = None
        notAll = True
        while(notAll):
            if(nextPageToken is None):
                request = youtube.playlists().list(
                    part="snippet",
                    channelId=UploadsID,
                    maxResults=50
                )
            else:
                request = youtube.playlists().list(
                    part="id",
                    channelId=UploadsID,
                    maxResults=50,
                    pageToken=nextPageToken
                )   
            response = request.execute()
            items = response['items']
            for item in items:
                playlists.append({'id':item['id'], 'title':item['snippet']['title']})
            try:
                nextPageToken = request['nextPage']
            except:
                notAll = False
                continue
        return playlists

    def getVideosByPlaylist(ID):
        videos = []
        nextPageToken = None
        notAll = True
        while(notAll):
            if(nextPageToken is None):
                request = youtube.playlistItems().list(
                    part="snippet",
                    playlistId=ID,
                    maxResults=50
                )
            else:
                request = youtube.playlistItems().list(
                    part="snippet",
                    playlistId=ID,
                    maxResults=50,
                    pageToken=nextPageToken
                )  
            response = request.execute()
            items = response['items']
            for item in items:
                videos.append({'id':item["snippet"]["resourceId"]["videoId"], 'title':item['snippet']['title'], 'date':item['snippet']['publishedAt']})
            try:
                nextPageToken = response['nextPageToken']
            except:
                notAll = False
                continue
        return videos 

    #UploadsID = getUploadsID('UCRS-7r-HT7VXZF2ZDVogueg')
    #UploadsID = getUploadsID('UCLfISex2d92tzfLKAOFPxeA')

    def getStatistics(videoID):
        pass
        

    playlists = getPlaylists(ChannelID)

    dataOld = []
    #data = []
    #data.append([])
    #data.append([])
    #data.append([])
    #data.append([])
    #data.append([])
    #data.append([])
    #data.append([])
    #data.append([])
    #data.append([])
    #data.append([])
    vds = []
    it = 0
    for playlist in playlists:
        it+=1
        print('Processing', it,'playlist of', len(playlists))
        videos = getVideosByPlaylist(playlist['id'])
        print('Count of videos:', len(videos))
        
        for i in videos:
            vds.append(i['id'])
            request = youtube.videos().list(
                    part="statistics",
                    id=i['id']
                )
            response = request.execute()
            try:
                statistics = response['items'][0]['statistics']
                dataOld.append(
                    [i['id'],
                    i['title'],
                    i['date'],
                    playlist['id'],
                    playlist['title'],
                    statistics['viewCount'],
                    statistics['likeCount'],
                    statistics['dislikeCount'],
                    statistics['commentCount'],
                    statistics['favoriteCount']]
                )
            except:
                pass
            
    dataReady = pd.DataFrame(data=dataOld, columns=['VideoID', 'VideoTitle', 'DateOfPublic', 'PlaylistID', 'PlaylistTitle', 'views', 'likes', 'dislikes', 'comments', 'Favorites'])

    dataReady.to_csv(savePath, index=False, encoding=encoding)
