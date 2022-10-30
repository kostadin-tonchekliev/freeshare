# FreeShare
## An open source file sharing service

---

Have you ever wanted to share a file but were afraid of the security risks of someone else hosting your file or perhaps wanted some features they didn't offer? Well this is the project for you. I started FreeShare as a way of learning Python servers and API's however it turned into something which I thought other people can enjoy. Build entirely with Python and based on Flask. It might not be the prettiest because front-end isn't my strong side but is usable for now. <br>

---
### Features:
+ Web page for uploading/downloading files
+ Ability to upload/download files directly over a POST request
+ Set a time after which the file will be automatically deleted
+ Customisability

### Requirements:
Nothing much, just a place to run the Flask server and it is up to if you want to have it publicly accessible or totally local. <br>
*Note: depending on your setup you might need to install a separate server like apache/nginx which will be responsible for the actual serving of the uploaded files. An easy way of seeing if you need such is by trying to open an uploaded file from the web, if you see a 404 an extra server is required*

### Setup:
Install the required packages:
```
    pip3 install -r requirements.txt
```
Update the app.py file with your own settings.
```
    app.config['SECRET_KEY'] = '************************' #Change this to something unique
    domain = 'domain.com' #Change this to the domain you want to serve the files from
    protocol = 'http' #Change this to the protocol you want to use
```
Optional Settings:
```
    On line 21: log_file = logging.FileHandler('info.log') -> Change info.log to the file name you want to use for storing the logs
    On line 64: @app.route('/api', methods=['POST']) -> Change /api to the endpoint you want to use for the POST requests
```

### Usage:
Run the server:
```commandline
    flask run
```
^^^ Needs to be done in the place you have uploaded the files to. By default it will run the Flask server on port 5000, you can change this by running `flask run --port 80` <br>
*Note: If you are going to deploy on an actual server I would advise running it with `flask run --host 0.0.0.0 --port 80` so that it can show on the server IP*

After running the server you can upload files to the server by going to the domain you set in the config file or making a POST request. The file is the file you want to upload and the TTL is how long you want the file to be live, leaving TTL empty will keep it forever. <br>
When making the POST request you need to add the file and the TTL is optional, not adding TTL will keep the file permanent. Here is an example:
```bash
    curl -X POST -F 'file=@example.txt' -F 'ttl=10' http://127.0.0.1/api
```
*Note: before the file name you need to add @ so that it can work.*

---
### Structure:
```
├── app.py -> Flask app
├── info.log -> Log file for main activity
├── guardian.log -> Access log
├── /files -> Folder to save files to
└── /static -> Static files for the web page
    ├── script.js
    └── style.css
└── /templates  -> Templates for the web page
    ├── 404.html
    ├── base.html
    ├── download.html
    ├── index.html
    └── uploaded.html
```

### To do:
+ Create a docker image where everything is already setup
