import cv2 as cv
import numpy as np
import os
from flask import Flask, render_template, request, send_file
from time import time

def convolve(I: np.ndarray, width: int, height: int, H: int):
    new = np.zeros(I.shape)
    H_half = H//2
    for w in range(width):
        for h in range(height):
            if w-H_half < 0 or w-H_half+H > width-1 or h-H_half < 0 or h-H_half+H > height-1:
                sum = [0,0,0]
                for Hw in range(H):
                    for Hh in range(H):
                        try:
                            sum += I[w+Hw-H_half, h+Hh-H_half]
                        except IndexError:
                            pass
                new[w, h] = sum
            else:
                new[w, h] = I[w-H_half:w-H_half+H, h-H_half:h-H_half+H].sum(axis=(0,1))
    return new

def cache(file: str, H: int):
    input = cv.imread("./input/"+file)
    name = file[:file.rfind('.')]
    if not os.path.isfile(f"./output/{name} on acid{H}.png"):
        return
    output = cv.imread(f"./output/{name} on acid{H}.png")
    if output.shape == input.shape:
        print(f"Returning cache of {name} on acid{H}.png")
        return f"./output/{name} on acid{H}.png"

def webmain(file: str, H: int):
    start = time()
    c = cache(file, H)
    if c is not None:
        return send_file(c)

    I = cv.imread("./input/"+file)
    if I is None:
        return 'Failure. (Did you put the image into the input folder?)'
    
    width, height = len(I), len(I[0])
    new = convolve(I, width, height, H)

    outname = f"./output/{file[:file.rfind('.')]} on acid{H}.png"
    cv.imwrite(outname,np.array(new,dtype=np.uint8))
    total = time()-start
    print(f"Size of {height}x{width} with H of size {H} took {round(total,1)} seconds ({round(total/60,1)} minutes).")
    return send_file(outname)

app = Flask(__name__,static_folder='static')
@app.route('/')
def website():
    return render_template('start.html')

@app.route('/trip', methods=['GET','POST'])
def generateImage():
    if request.method == 'GET':
        return "No input."
    
    elif request.method == 'POST':
        form = request.form
        img = multi1 = multi2 = single = 0
        try:
            img = form['img']
            single = int(form['prescisionS'])
            multi1 = int(form['prescisionM1'])
            multi2 = int(form['prescisionM2'])
        except KeyError:
            pass
        except ValueError:
            pass
        if multi1 and multi2:
            r = range(multi1, multi2)

            if single and single not in r:
                webmain(img, single)

            for i in r:
                webmain(img, i)
            return webmain(img, multi2)
        
        elif single:
            return webmain(img, single)
        
        return 'Failure. (Did you input numbers into the form.)'
        
if __name__ == '__main__':
    app.run(host='localhost')
