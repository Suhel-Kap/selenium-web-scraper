"""
A sample Hello World server.
"""
import os, json, smtplib
from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
import chromedriver_binary
from webdriver_manager.utils import ChromeType
import pandas as pd
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders, message

from flask import Flask, render_template

load_dotenv()

# pylint: disable=C0103
app = Flask(__name__)

YOUTUBE_TRENDING_URL = 'https://www.youtube.com/feed/trending'

def get_driver():
  chrome_options = Options()
  chrome_options.add_argument('--no-sandbox')
  chrome_options.add_argument('--headless')
  chrome_options.add_argument('--disable-dev-shm-usage')
  driver = webdriver.Chrome(ChromeDriverManager().install(),options=chrome_options)
  return driver

def get_videos(driver):
  print("Fetching page...")
  driver.get(YOUTUBE_TRENDING_URL)
  VIDEO_DIV_TAG = "ytd-video-renderer"
  videos = driver.find_elements(By.TAG_NAME, VIDEO_DIV_TAG)
  return videos

def parse_video(video):
  title_tag = video.find_element(By.ID,'video-title')
  title = title_tag.text
  url = title_tag.get_attribute('href')

  channel_tag = video.find_element(By.ID, 'channel-name')
  channel_name = channel_tag.text
  channel_url = channel_tag.find_element(By.TAG_NAME, 'a').get_attribute('href')

  thumbnail_url = video.find_element(By.TAG_NAME, 'img').get_attribute('src')

  metadata_tag = video.find_element(By.ID, 'metadata-line').text
  metadata_tag = metadata_tag.splitlines()
  views = metadata_tag[0]
  uploaded = metadata_tag[1]

  description_txt = video.find_element(By.ID, 'description-text').text

  return {
    'Title': title,
    'URL': url,
    'Channel Name': channel_name,
    'Channel Link': channel_url,
    'Thumbnail URL': thumbnail_url,
    'Views': views,
    'Uploaded': uploaded,
    'Description': description_txt
  }

def send_email(csv_file):
  try:
    server_ssl = smtplib.SMTP_SSL('smtp.gmail.com', 465)
    server_ssl.ehlo()   

    SENDER_EMAIL = 'xyzxyz5580@gmail.com'
    RECEIVER_EMAIL = 'suhelkapadia2@gmail.com'
    SENDER_PASSWORD = os.environ['GMAIL_PASSWORD']
    
    msg = MIMEMultipart()
    msg['From'] = SENDER_EMAIL
    msg['To'] = RECEIVER_EMAIL
    
    msg['Subject'] = 'YouTube Trending Videos'

    body = 'Here attached is a file containing top 10 youtube trending videos.\n'

    msg.attach(MIMEText(body, 'plain'))
    filename = csv_file
    attachment = open(filename, "rb")
    p = MIMEBase('application', 'octet-stream')
    p.set_payload((attachment).read())
    encoders.encode_base64(p)
    p.add_header('Content-Disposition', "attachment; filename= %s" % filename)
    msg.attach(p)
    email_text = msg.as_string()

    server_ssl.login(SENDER_EMAIL, SENDER_PASSWORD)
    server_ssl.sendmail(SENDER_EMAIL, RECEIVER_EMAIL, email_text)
    server_ssl.close()

  except:
      print('Something went wrong...')

@app.route('/')
def hello():
    print("Creating driver...")
    driver = get_driver()

    videos = get_videos(driver)
    print(f"Found {len(videos)} videos")

    print('Parsing the first 10 video')

    video_data = [parse_video(video) for video in videos[:10]]

    print('Saving data to CSV...')
    videos_df = pd.DataFrame(video_data)
    # print(videos_df)
    videos_df.to_csv('./static/trending.csv',index=None)

    print("Sending results over email")
    # send_email('trending.csv')
    message="Top 10 Youtube Trending Videos"

    """Get Cloud Run environment variables."""
    service = os.environ.get('K_SERVICE', 'Unknown service')
    revision = os.environ.get('K_REVISION', 'Unknown revision')

    return render_template('index.html',
        message=message,
        Service=service,
        Revision=revision)

if __name__ == '__main__':
    server_port = os.environ.get('PORT', '8080')
    app.run(debug=False, port=server_port, host='0.0.0.0')
