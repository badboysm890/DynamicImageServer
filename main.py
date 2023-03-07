from flask import Flask, make_response, request
from PIL import Image, ImageDraw, ImageFont
import os
from flask_cors import CORS, cross_origin
import requests
import datetime
import json


app = Flask(__name__)
CORS(app)


def getGame(id):

    url = "http://devstage.turftown.in/api/v2/game/share/"+id
    
    payload={}
    headers = {}
    
    response = requests.request("GET", url, headers=headers, data=payload)
    data = response.json()
    print(data["data"]["type"])
    vs_Data = data["data"]["type"]
    date = data["data"]["start_time"]
    start_time = data["data"]["start_time"]
    end_time = data["data"]["end_time"]
    gameKind = data["data"]["sport_name"]
    courtImage = data["data"]["image"]
    # convert the date format from 2020-08-21T19:00:00.000Z to Wed . Aug 21st
    date = date.split("T")
    date = date[0]
    date = date.split("-")
    date = date[2]+" . "+date[1]+" "+date[0]
    start_time = start_time.split("T")
    start_time = start_time[1]
    start_time = start_time.split(":")
    start_time = start_time[0]+":"+start_time[1]
    end_time = end_time.split("T")
    end_time = end_time[1]
    end_time = end_time.split(":")
    end_time = end_time[0]+":"+end_time[1]
    if int(start_time.split(":")[0]) < 12:
        start_time = start_time+" am"
    else:
        start_time = start_time+" pm"
    if int(end_time.split(":")[0]) < 12:
        end_time = end_time+" am"
    else:
        end_time = end_time+" pm"
    time = start_time+" - "+end_time
    
    # start_time should be in 12 hour format example 17:30 pm to 5:30 pm

    start_time = datetime.datetime.strptime(start_time, '%H:%M %p')

    # end_time should be in 12 hour format example 17:30 pm to 5:30 pm
    end_time = datetime.datetime.strptime(end_time, '%H:%M %p')

    # convert from utc to ist
    start_time = start_time + datetime.timedelta(hours=5, minutes=30)
    end_time = end_time + datetime.timedelta(hours=5, minutes=30)

    time  = start_time.strftime('%I:%M %p') + " - " + end_time.strftime('%I:%M %p')


    # 09 . 02 2023 to Day Month Date
    
    date_str = date
    date_object = datetime.datetime.strptime(date_str, "%d . %m %Y")
    
    day_suffix = "th" if 4 <= date_object.day <= 20 or 24 <= date_object.day <= 30 else ["st", "nd", "rd"][date_object.day % 10 - 1]
    
    date = date_object.strftime("%a %b %-d" + day_suffix)

    data = {
        "date": date,
        "time": time,
        "vs": vs_Data,
        "courtImage": courtImage,
        "gameKind": gameKind
    }

    return data

@app.route('/image')
def image_endpoint():
    id = request.args.get('id')
    game = getGame(id)
    date = game['date']
    time = game['time']
    vs = game['vs']
    courtImage = game['courtImage']
    gameKind = game['gameKind']
    img = Image.new('RGB', (1200, 630), color='white')
    draw = ImageDraw.Draw(img)
    bg = Image.open('BG.png')
    img.paste(bg, (0, 0))
    text = "Join my Game on"
    try:
     font = ImageFont.truetype('Nexa-Trial-Heavy.ttf', 80)
    except:
        permission = oct(os.stat('Nexa/Commercial/Nexa_V2_2020/TTF/NexaDemo-Bold.ttf').st_mode)[-3:]
        font = ImageFont.load_default()
    
    
    draw.text((70, 50), text, fill='white', font=font)
    calender = Image.open('Date.png')
    img.paste(calender, (70, 430), calender)
    timer = Image.open('Time.png')
    img.paste(timer, (70, 530), timer)
    location = Image.open('Court.png')
    court = Image.open(requests.get(courtImage, stream=True).raw)
    court = court.resize((274, 273))
    img.paste(court, (800, 120), location)
    game = Image.open('TurfTownLogo.png')
    img.paste(game, (70, 180), game)
    micro = Image.open('MicroBanner.png')
    img.paste(micro, (850, 350), micro)
    font = ImageFont.truetype('NexaText-Trial-Bold.ttf', 37)
    text = vs if vs is not None else "6 v 6"
    text_width, text_height = draw.textsize(text, font)
    text_x = (micro.width - text_width) / 2 + 850
    text_y = (micro.height - text_height) / 2 + 340
    # Nexa-Text Regular
    
    draw.text((text_x, text_y), text, fill='white', font=font)
    font = ImageFont.truetype('NexaText-Trial-Regular.ttf', 47)
    if date is None:
        date = "Wed . Aug 21st"
    draw.text((150, 428), date, fill='white', font=font)
    font = ImageFont.truetype('NexaText-Trial-Regular.ttf', 47)

    if time is None:
        time = "7:00 pm - 10:30 pm"
    draw.text((150, 528), time, fill='white', font=font)

    if gameKind is None:
        gameKind = "Football"
    burn = Image.open(gameKind+".png")
    img.paste(burn, (1040, 470), burn)
    img = img.resize((int(img.width/2), int(img.height/2)), Image.ANTIALIAS)
    img.save('image.jpeg')
    response = make_response(open('image.jpeg', 'rb').read())
    response.headers.set('Content-Type', 'image/jpeg')
    return response

def add_corners(im, rad):
    circle = Image.new('L', (rad * 2, rad * 2), 0)
    draw = ImageDraw.Draw(circle)
    draw.ellipse((0, 0, rad * 2 - 1, rad * 2 - 1), fill=255)
    alpha = Image.new('L', im.size, 255)
    w, h = im.size
    alpha.paste(circle.crop((0, 0, rad, rad)), (0, 0))
    alpha.paste(circle.crop((0, rad, rad, rad * 2)), (0, h - rad))
    alpha.paste(circle.crop((rad, 0, rad * 2, rad)), (w - rad, 0))
    alpha.paste(circle.crop((rad, rad, rad * 2, rad * 2)), (w - rad, h - rad))
    im.putalpha(alpha)
    return im

def getVenue(id):
    url = "https://devstage.turftown.in/api/v3/venue/get_venue_info/"+id
    payload={}
    headers = {
      'x-access-token': 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6IjVlMDIwNjk4MTdmNTE3NmRmZmZhNmNmNSIsInBob25lIjoiOTM0NzYwMzAxMyIsInJvbGUiOiJ1c2VyIiwiaWF0IjoxNjc3NzI2NjUyfQ.mOa7eq4jKRvOripCXh74kJFjCo8KVOngdGHPb2bDb9E'
    }
    response = requests.request("POST", url, headers=headers, data=payload)
    # print(response.text)
    # json parse and return
    return json.loads(response.text)

@app.route('/venue')
def venue_endpoint():
    id = request.args.get('id')
    venue = getVenue(id)
    spotlight_picture = venue['data']['venue']['spotlight_picture']
    rating = venue['data']['ratings_and_reviews']['rating']
    area = venue['data']['venue']['area']
    address = venue['data']['venue']['address']
    name = venue['data']['venue']['name']
    print(spotlight_picture, rating, area, address, name)
    img = Image.new('RGB', (1200, 630), color='white')
    draw = ImageDraw.Draw(img)
    bg = Image.open('venue/venueBG.png')
    img.paste(bg, (0, 0))
    text_line1 = "Check this"
    text_line2 = "venue out on"
    try:
        font = ImageFont.truetype('Nexa-Trial-Heavy.ttf', 100)
    except:
        permission = oct(os.stat('Nexa/Commercial/Nexa_V2_2020/TTF/NexaDemo-Bold.ttf').st_mode)[-3:]
        font = ImageFont.load_default()
    draw.text((70, 90), text_line1, fill='white', font=font)
    draw.text((70, 220), text_line2, fill='white', font=font)

    # logo below the text turfLogo
    turfLogo = Image.open('venue/turfLogo.png')
    img.paste(turfLogo, (73, 390), turfLogo)

    venueImage = Image.open(requests.get(spotlight_picture, stream=True).raw).convert("RGBA")
    venueImage = venueImage.resize((320, 320))
    venueImage = add_corners(venueImage, 50)
    img.paste(venueImage, (800, 120), venueImage)

    # add emptyRatingsBanner under the venueImage
    emptyRatingsBanner = Image.open('venue/emptyRatingsBanner.png')
    img.paste(emptyRatingsBanner, (820, 360), emptyRatingsBanner)

    # add rating on the emptyRatingsBanner where ratings is two decimal points
    rating  = float(rating)
    rating = str(rating)
    font = ImageFont.truetype('Nexa-Trial-Heavy.ttf', 60)
    draw.text((890, 390), rating, fill='white', font=font)

    # add StarVenue.png after the rating
    starVenue = Image.open('venue/StarVenue.png')
    img.paste(starVenue, (1000, 400), starVenue)

    font = ImageFont.truetype('NexaText-Trial-Bold.ttf', 37)
    text = name
    img.save('venue/venue.jpeg')
    response = make_response(open('venue/venue.jpeg', 'rb').read())
    response.headers.set('Content-Type', 'image/jpeg')


    return response
    

if __name__ == '__main__':
    app.run(host="0.0.0.0",debug=True)
