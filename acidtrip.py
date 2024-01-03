import cv2 as cv
import numpy as np
from flask import Flask, render_template, request, send_file
from time import time

def webmain(file: str, H: int):
    start = time()
    I = cv.imread("./input/"+file)

    try:
        new = np.zeros(I.shape)
    except:
        return 'Failure. (Did you put the image into the input folder?)'
    width, height = len(I), len(I[0])
    Hsize = abs(H)
    for row in range(width):
        for col in range(height):
            sum = 0
            for Hrow in range(Hsize):
                for Hcol in range(Hsize):
                    try:
                        sum += I[row+Hrow-(H//2), col+Hcol-(H//2)]
                    except:
                        pass
            new[row, col] = sum

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
        if form['prescisionM1'] and form['prescisionM2']:
            r = range(int(form['prescisionM1']),int(form['prescisionM2']))
            if form['prescisionS'] and int(form['prescisionS']) not in r:
                webmain(form['img'],int(form['prescisionS']))
            for i in r:
                webmain(form['img'],i)
            return webmain(form['img'],int(form['prescisionM2']))
        elif form['prescisionS']:
            return webmain(form['img'],int(form['prescisionS']))
        return 'Failure. (Did you input numbers into the form.)'
        
if __name__ == '__main__':
    app.run(host='localhost')