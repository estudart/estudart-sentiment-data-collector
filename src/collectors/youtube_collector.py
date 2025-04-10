import time
import json
from datetime import datetime, timezone
from concurrent.futures import ThreadPoolExecutor, as_completed

from googleapiclient.discovery import build
from youtube_transcript_api import YouTubeTranscriptApi

from src.collectors.news_collector import NewsDataCollector



class YoutubeDataCollector(NewsDataCollector):
    def __init__(self):
        super().__init__()

        self.platform = "youtube"

        self.loop_delay_time = self.secrets.get("YOUTUBE_LOOP_DELAY_TIME")
        self.video_limit = self.secrets.get("YOUTUBE_VIDEO_LIMIT")
        self.comment_limit = self.secrets.get("YOUTUBE_COMMENT_LIMIT")
        self.api_key = self.secrets.get("YOUTUBE_API_KEY")
        self.executor = ThreadPoolExecutor(max_workers=5)

        self.youtube = None

        self._initialize_credentials()

    
    def _initialize_credentials(self) -> None:
        self.youtube = build("youtube", "v3", developerKey=self.api_key)


    def fetch_data(self, query: str, limit: int = 5) -> list:
        videos_data = self.youtube.search().list(
            channelId=query,
            part="id,snippet",
            type="video",
            maxResults=limit,
            order="date",
            fields=(
                "items(id(videoId),snippet(publishedAt,channelId,channelTitle,title,description))"
            )
        ).execute()

        return videos_data
    

    def fetch_video_transcript(self, video_id: str) -> dict:
        try:
            # Get the transcript (auto-generated or manually created)
            transcripts = YouTubeTranscriptApi.get_transcript(video_id, languages=['pt', 'en'])

            return " ".join([transcript["text"] for transcript in transcripts])

        except Exception as err:
            raise
    

    def process_comment(self, comment, keyword, video_id):
        snippet = comment["snippet"]["topLevelComment"]["snippet"]
        comment_id = comment["id"]

        processed_comment = {
            "id": comment_id,
            "video_id": video_id,
            "author": snippet["authorDisplayName"],
            "body": snippet["textDisplay"],
            "likes": snippet["likeCount"],
            "created_utc": snippet["publishedAt"]
        }
        self.logger.info(f"Processed new comment: {processed_comment}")
        if not self.queue_manager.is_set_member("youtube-comments", comment_id):
            self.send_to_queue(f"youtube-{keyword}-comments", 
                                processed_comment)
    

    def process_data(self, 
                     video_data: dict, 
                     keyword: str) -> list:
        is_video_new = False

        try:
            video_id = video_data["id"]["videoId"]
            video_stats = self.youtube.videos().list(
                    part="statistics",
                    id=video_id,
                    fields="items(statistics)"
                ).execute()["items"][0]["statistics"]

            processed_video = {
                # Textual Content
                "title": video_data["snippet"]["title"],
                "description": video_data["snippet"]["description"],
                "body": self.fetch_video_transcript(video_id),

                # Metadata
                "id": video_id,
                "created_utc": video_data["snippet"]["publishedAt"],
                "channel_id": video_data["snippet"]["channelId"],
                "channel_title": video_data["snippet"]["channelTitle"],

                # Engagement Metrics
                "view_count": int(video_stats.get("viewCount", 0)),
                "likes": int(video_stats.get("likeCount", 0)),
                "num_comments": int(video_stats.get("commentCount", 0)),
                "num_favorite": int(video_stats.get("favoriteCount", 0)),

                # URL
                "url": f"https://www.youtube.com/watch?v={video_id}"
            }
            if not self.queue_manager.is_set_member(f"{self.platform}-videos", video_id):
                self.send_to_queue(f"{self.platform}-{keyword}-videos", 
                                    processed_video)
                is_video_new = True
            else:
                self.logger.debug(f"video {video_id} already seen, skipping.")
                return is_video_new
            
        except Exception as err:
            self.logger.error(
                f"Could not process video with id {video_id}, "
                f"reason: {err}")
            return is_video_new

        self.logger.debug(f"Processed new video: {processed_video}")

        try:
            comments = self.youtube.commentThreads().list(
                part="id,snippet",
                videoId=video_id,
                maxResults=self.comment_limit,
                textFormat="plainText"
            ).execute()
            # Run a loop on comments list and send it to queue
            futures = [
                self.executor.submit(self.process_comment, 
                                     comment, keyword, video_id)
                for comment in comments["items"]
            ]
            for future in as_completed(futures):
                future.result()

        except Exception as err:
            self.logger.error(
                f"Could not process comments for video with id {video_id}, "
                f"reason: {err}")

        return is_video_new
    

    def send_to_queue(self, queue, data: json):
        return self.queue_manager.send_to_queue(queue, data)
    

    def run_loop(self, query):
        loop_start_time = datetime.now(timezone.utc)
        try:
            videos = self.fetch_data(query, limit=self.video_limit)
        except Exception as err:
            self.logger.info(
                f"Could not fetch data for {query}, "
                f"reason: {err}")
            raise

        number_of_videos = 0
        for video in videos["items"]:
            if self.process_data(video, query):
                number_of_videos+=1

        loop_finished_time = datetime.now(timezone.utc)

        time_difference = (
            (loop_finished_time - loop_start_time)
            .total_seconds())

        self.logger.info(
            f"Loop for {query} took {round(time_difference, 2)} seconds "
            f"and processed {number_of_videos} videos.")
        

    def run(self, querys):
        while True:
            for query in querys:
                try:
                    self.run_loop(query)
                except Exception as err:
                    self.logger.error(
                        f"Could not run loop for {query}, resson: {err}"
                    )
            
            time.sleep(self.loop_delay_time)         
