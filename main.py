from flask import Flask, make_response, request
from PIL import Image, ImageDraw, ImageFont
import os
from flask_cors import CORS, cross_origin
import requests
import datetime


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
    # convert the time format from 2020-08-21T19:00:00.000Z to 7:00 pm - 10:30 pm
    start_time = start_time.split("T")
    start_time = start_time[1]
    start_time = start_time.split(":")
    # utc to ist

    start_time = start_time[0]+":"+start_time[1]
    end_time = end_time.split("T")
    end_time = end_time[1]
    end_time = end_time.split(":")
    end_time = end_time[0]+":"+end_time[1]
    # pick am or pm
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
#   try:  
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

    # add the calender logo
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
#   except Exception as e:
#     # line number and error message
#     print(e)
#     return "Error"

if __name__ == '__main__':
    app.run(host="0.0.0.0",debug=True)
