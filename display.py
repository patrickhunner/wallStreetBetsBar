from rgbmatrix import RGBMatrix, RGBMatrixOptions, graphics
import time
import sys
import os.path
import requests
from threading import Thread
import queue

from PIL import Image

def get_stock_logo(sym):
    if os.path.isfile("logos/{}.png".format(sym)):
        print(sym + " logo is already downloaded...")
        return
    req = "https://cloud.iexapis.com/stable/stock/{}/logo?token=pk_63537822109845ffa70a33cef99e35c1".format(sym)
    resp = requests.get(req)
    resp = resp.json()
    url = resp["url"]
    print("URL for {} obtained".format(sym))

    myfile = requests.get(url)
    open("logos/{}.png".format(sym), 'wb').write(myfile.content)


def make_persistant_request(req):
    success = False
    while not success:
        try:
            resp = requests.get(req)
            resp = resp.json()
            success = True
        except:
            success = False
    return resp


def get_stock_data(sym):
    print("req formation")
    req = "https://sandbox.iexapis.com/stable/stock/{}/quote?token=Tpk_d10896a8a4fb425c96d0748e8c077dbd".format(sym)
    resp = make_persistant_request(req)

    change = resp["change"]
    arrow = '\u2193'
    color = graphics.Color(255, 0, 0)
    if change > 0:
        arrow = '\u2191'
        color = graphics.Color(0, 255, 0)
    str1 = u'{0} {1:.2f} {2}'.format(sym, resp["latestPrice"], arrow)
    str2 = '{0:.2f} ({1:.2f}%)'.format(change, round(resp["changePercent"]*100, 2))
    print(str1)
    print(str2)
    return (color, str1, str2, sym)


def get_data_loop(out_q, interval):
    symbols = get_display_parameters()
    while True:
        resps = []
        for sym in symbols:
            get_stock_logo(sym)
            resps.append(get_stock_data(sym))
        new_symbols = get_display_parameters()
        if symbols != new_symbols:
            print("Symbols Changed while getting data")
            symbols = new_symbols
            continue
        out_q.put(resps)

        print("Entering Sleep Cycle...")
        sleeps = 0
        while sleeps < interval:
            new_symbols = get_display_parameters()
            if new_symbols != symbols:
                print("Symbols Changed")
                break
            time.sleep(1)
            sleeps += 1


def get_display_parameters():
    req = "http://10.0.0.245:3001/api"
    resp = make_persistant_request(req)
    return resp["data"]["stocks"]


def display(matrix, font, textColor, str1, str2, sym):
    offscreen_canvas = matrix.CreateFrameCanvas()
    pos = offscreen_canvas.width

    is_image = True
    try:
        image = Image.open("logos/{}.png".format(sym)).convert("RGB")
        image.thumbnail((matrix.width, matrix.height), Image.ANTIALIAS)
        img_width, img_height = image.size
    except:
        is_image = False
        img_width = -5

    while True:
        offscreen_canvas.Clear()

        #matrix.SetImage(image.convert('RGB'))
        if is_image:
            offscreen_canvas.SetImage(image, pos)

        len1 = graphics.DrawText(offscreen_canvas, font, img_width + pos + 5, 14, textColor, str1)
        len2 = graphics.DrawText(offscreen_canvas, font, img_width + pos + 5, 28, textColor, str2)
        if len1 < len2:
            len1 = len2
        pos -= 1
        if (pos + len1 + img_width + 5 < 0):
            #pos = offscreen_canvas.width
            break

        time.sleep(0.05)
        offscreen_canvas = matrix.SwapOnVSync(offscreen_canvas)

    
# Main function
if __name__ == "__main__":
    try:
        # Start loop
        print("Press CTRL-C to stop sample")
        
        options = RGBMatrixOptions()
        options.rows = 32
        options.cols = 64
        options.hardware_mapping = "adafruit-hat"
        
        matrix = RGBMatrix(options = options)
        font = graphics.Font()
        #font.LoadFont("../../../fonts/7x13.bdf")
        font.LoadFont("7x13.bdf")

        #symbols = get_display_parameters() 

        #stock_input = queue.Queue()
        #stock_input.put(symbols)
        stock_data = queue.Queue()
        #should_break = queue.Queue()
        #should_break.put(False)
        thread = Thread(target=get_data_loop, args=(stock_data, 300))
        thread.start()

        while stock_data.empty():
            time.sleep(1)
            #print("sleeping")

        idx = -1
        while True:
            if not stock_data.empty():
                resps = stock_data.get()
                print("new resps")
            prev_idx = idx
            for idx, val in enumerate(resps):
                idx_to_use = prev_idx + 1 + idx
                if idx_to_use > len(resps) - 1:
                    idx_to_use = idx_to_use - len(resps)
                print("Using index {} to display".format(idx_to_use))
                try:
                    r = resps[idx_to_use]
                except:
                    r = resps[len(resps) - 1]
                display(matrix, font, r[0], r[1], r[2], r[3])
                if not stock_data.empty():
                    print("Data not empty anymore")
                    #idx = len(resps)
                    break

            #symbols = get_display_parameters()
            #has_changed = symbols != stock_input.get()
            #stock_input.put(symbols)
            #if has_changed:
            #    print("Symbols Changed")
            #    while not should_break.empty:
            #        should_break.get()
            #    should_break.put(True)

    except KeyboardInterrupt:
        print("Exiting\n")
        thread.kill()
        sys.exit(0)
