# Sample Python code for youtube.playlists.insert
# See instructions for running these code samples locally:
# https://developers.google.com/explorer-help/guides/code_samples#python

import os

import google_auth_oauthlib.flow
import googleapiclient.discovery
import googleapiclient.errors
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

scopes = ["https://www.googleapis.com/auth/youtube.force-ssl"]

# Disable OAuthlib's HTTPS verification when running locally.
# *DO NOT* leave this option enabled in production.
os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"
api_service_name = "youtube"
api_version = "v3"
# Add your own client_secrets_file.json file here
client_secrets_file = r"client_secret_1065829972808-ng9dd6jpjavuf0ogqvhjtcagevf2s5kq.apps.googleusercontent.com.json"

# Get credentials and create an API client
flow = google_auth_oauthlib.flow.InstalledAppFlow.from_client_secrets_file(client_secrets_file, scopes)
credentials = flow.run_console()
youtube = googleapiclient.discovery.build(api_service_name, api_version, credentials=credentials)


def get_stored_data():
    '''
    Get the stored playlist ID and last added video index from the file
    :return: playlist_id, last_added
    '''
    try:
        with open('playlist_info.txt', 'r') as file:
            playlist_id = file.readline().strip()
            last_added = int(file.readline().strip())
        return playlist_id, last_added
    except FileNotFoundError:
        return None, 0


def store_data(playlist_id, last_added):
    '''
    Store the playlist ID and last added video index to the file
    :param playlist_id: str
    :param last_added: int
    :return: None
    '''
    with open('playlist_info.txt', 'w') as file:
        file.write(f'{playlist_id}\n{last_added}')


def create_playlist(youtube, title, description='Playlist created via API'):
    '''
    Create a new playlist
    :param youtube: youtube API object
    :param title: str
    :param description: str
    :return: str
    '''
    playlist_body = {
        'snippet': {
            'title': title,
            'description': description
        },
        'status': {
            'privacyStatus': 'public'
        }
    }
    playlist_response = youtube.playlists().insert(
        part='snippet,status',
        body=playlist_body
    ).execute()
    return playlist_response['id']


def add_video_to_playlist(youtube, playlist_id, video_id):
    '''
    Add a video to a playlist
    :param youtube: youtube API object
    :param playlist_id: str
    :param video_id: str
    :return: None
    '''
    playlist_item_body = {
        'snippet': {
            'playlistId': playlist_id,
            'resourceId': {
                'kind': 'youtube#video',
                'videoId': video_id
            }
        }
    }
    youtube.playlistItems().insert(
        part='snippet',
        body=playlist_item_body
    ).execute()


def main():
    try:
        playlist_id, last_added = get_stored_data()

        if not playlist_id:
            # Create a new playlist if none exists
            playlist_id = create_playlist(youtube, r'صحيح البخاري - الشيخ ياسين رشدي', r'شرح صحيح البخاري للشيخ ياسين رشدي بمسجد المواساة بالإسكندرية')
            last_added = 0  # Start from the beginning

        # Start adding videos from where we left off, up to 1615
        for i in range(last_added + 1, 1616):
            query = f'bokhv{str(i).zfill(5)}'
            search_response = youtube.search().list(q=query, part='id,snippet', maxResults=1, type='video').execute()

            if search_response['items']:
                video_id = search_response['items'][0]['id']['videoId']
                add_video_to_playlist(youtube, playlist_id, video_id)
                print(f'Added video {video_id} ({query}) to playlist {playlist_id}')
                store_data(playlist_id, i)  # Update stored data with the latest added video number
            else:
                print(f'No video found for {query}')
                break  # Stop the loop if no video is found for the current number

    except HttpError as e:
        print(f'An HTTP error occurred: {e.resp.status} {e.content}')


if __name__ == "__main__":
    main()

