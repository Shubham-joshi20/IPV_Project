from flask import Flask, render_template, request

app = Flask(__name__)

#@app.route('/')
def index():
    return render_template('index.html')

@app.route('/process_form', methods=['post'])
def process_form():
    if request.method == 'post':
        # Get form data
        name = request.form['name']
        #email = request.form['email']
        
        # Process the data (you can do any processing here)
        # For demonstration, let's just print the received data
        print(f'Name: {name}')
        
        # You can also return a response if needed
        return 'Form submitted successfully'

if __name__ == '__main__':
    app.run(debug=True)
