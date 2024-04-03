from flask import Flask, render_template, request, send_file
import os
import cv2
import numpy as np
from io import BytesIO
import base64

app = Flask(__name__)

UPLOAD_FOLDER = 'uploads'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def adjust_contrast(image_path):
    # Load the image
    image = cv2.imread(image_path)

    # Check if the image is color (3 channels)
    if len(image.shape) == 3:
        # Convert the image to LAB color space
        lab = cv2.cvtColor(image, cv2.COLOR_BGR2LAB)

        # Split the LAB image into channels
        l, a, b = cv2.split(lab)

        # Apply histogram equalization to the L channel
        l_equalized = cv2.equalizeHist(l)

        # Merge the equalized L channel with the original A and B channels
        adjusted_lab = cv2.merge((l_equalized, a, b))

        # Convert LAB image back to BGR
        adjusted_image = cv2.cvtColor(adjusted_lab, cv2.COLOR_LAB2BGR)

    else:
        # Convert the image to grayscale
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

        # Apply histogram equalization
        equalized = cv2.equalizeHist(gray)

        # Convert back to BGR (if needed)
        adjusted_image = cv2.cvtColor(equalized, cv2.COLOR_GRAY2BGR)

    return adjusted_image

def sharpen_image(image_path, sharpen=True):
    # Load the image
    image = cv2.imread(image_path)

    # Check if the image is color (3 channels)
    if len(image.shape) == 3:
        # Create a sharpening kernel
        kernel = np.array([[-1, -1, -1],
                           [-1,  9, -1],
                           [-1, -1, -1]])
        # Apply the sharpening kernel
        sharpened_image = cv2.filter2D(image, -1, kernel)
    else:
        # Apply sharpening directly to grayscale image
        sharpened_image = cv2.filter2D(image, -1, np.array([[0, -1, 0],
                                                             [-1, 5, -1],
                                                             [0, -1, 0]]))

    return sharpened_image


@app.route('/')
def index():
    return render_template('Front_page.html')

@app.route('/input.html')
def input_page():
    return render_template('input.html')

@app.route('/Sharping.html')
def Sharp_page():
    return render_template('Sharping.html')

@app.route('/process_image', methods=['POST'])
def process_image():
    if 'image' in request.files:
        image = request.files['image']
        if image.filename != '':
            image_path = os.path.join(app.config['UPLOAD_FOLDER'], image.filename)
            image.save(image_path)

            # Adjust contrast
            contrast_adjusted = adjust_contrast(image_path)

            # Save the adjusted image using cv2.imwrite
            adjusted_image_path = os.path.join(app.config['UPLOAD_FOLDER'], 'adjusted_' + image.filename)
            cv2.imwrite(adjusted_image_path, contrast_adjusted)

            # Prepare the image for download
            with open(adjusted_image_path, 'rb') as image_file:
                img_data = base64.b64encode(image_file.read()).decode()

            return render_template('download.html', image_data=img_data)

    return 'No image selected'


@app.route('/sharp_image', methods=['POST'])
def sharp_image():
    if 'image' in request.files:
        image = request.files['image']
        if image.filename != '':
            image_path = os.path.join(app.config['UPLOAD_FOLDER'], image.filename)
            image.save(image_path)
        
        sharp_img = sharpen_image(image_path,sharpen=True)

        sharp_image_path = os.path.join(app.config['UPLOAD_FOLDER'], 'adjusted_' + image.filename)
        cv2.imwrite(sharp_image_path, sharp_img)

        # Prepare the image for download
        with open(sharp_image_path, 'rb') as image_file:
            img_data = base64.b64encode(image_file.read()).decode()

        return render_template('download.html', image_data=img_data)

@app.route('/download_image', methods=['POST'])
def download_image():
    image_data = request.form['image_data']
    img_data = base64.b64decode(image_data)
    return send_file(BytesIO(img_data), mimetype='image/jpeg', as_attachment=True, download_name='adjusted_image.jpeg')


if __name__ == '__main__':
    app.run(debug=True)


