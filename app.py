from flask import Flask, request, render_template, url_for, redirect, session
import string
import secrets
import os
import logging
import threading
import time

app = Flask(__name__)

app.config['SECRET_KEY'] = '**********' #Change this to something unique
domain = 'domain.com' #Change this to the domain you want to serve the files from
protocol = 'http' #Change this to the protocol you want to use

path = os.getcwd()
current_folders = []
savefolder = 'static'


logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
log_file = logging.FileHandler('info.log')
formatter = logging.Formatter('[%(thread)d](%(asctime)s): %(message)s')
log_file.setFormatter(formatter)
logger.addHandler(log_file)

guardian = logging.getLogger('guardian')
guardian.setLevel(logging.DEBUG)
logfile = logging.FileHandler('guardian.log')
format = logging.Formatter('[%(thread)d](%(asctime)s): %(message)s')
logfile.setFormatter(format)
guardian.addHandler(logfile)

try:
    current_folders = os.listdir(f'{path}/{savefolder}')
except FileNotFoundError:
    current_folders = []
    logger.warning(f'[!]{savefolder} folder not found, creating it for you')
    os.mkdir(f'{path}/{savefolder}')

def generate_name(number):
    name = ''.join(secrets.choice(string.ascii_uppercase + string.ascii_lowercase) for i in range(number))
    return name

def create_folder():
    fname = generate_name(20)
    try:
        os.makedirs(f"{path}/{savefolder}/{fname}")
    except:
        logging.error(f"[!]{fname} already exists, generating new name")
        fname = generate_name(20)
        os.makedirs(f"{path}/{savefolder}/{fname}")
    return fname

def file_deletion(file, folder, ttlm):
    logger.info(f"[=]Thread for: {file.filename} with ttl: {ttlm} started. ({folder})")
    if ttlm is None or ttlm == '' or ttlm == 0:
        logger.error(f"[!]Empty TTL provided")
    else:
        time.sleep(int(ttlm))
        os.remove(f"{path}/{savefolder}/{folder}/{file.filename}")
        os.rmdir(f"{path}/{savefolder}/{folder}")
        current_folders.remove(folder)
        logger.info(f"[-]{file.filename} deleted. ")
    logger.info(f"[=]Thread for: {file.filename} finished. ")

def session_kill():
    session.pop('file_name', default=None)
    session.pop('ttl_value', default=None)
    logger.info("[-]Session variables killed")

def guardian_log():
    guardian.info(f'{request.environ["REMOTE_ADDR"]} requested {request.path}')

@app.route('/api', methods=['POST'])
def api():
    guardian_log()
    file_value = request.files['file']
    file_name = file_value.filename
    ttl = request.form.get('ttl')
    folder_name = create_folder()
    current_folders.append(folder_name)
    file_value.save(f'{path}/{savefolder}/{folder_name}/{file_name}')
    logger.info(f"[+]{file_name} succesfully created. ")
    x = threading.Thread(target=file_deletion, args=(file_value, folder_name, ttl, ))
    x.start()
    return f"Web download link: {protocol}://{domain}/{folder_name}\nCurl download link: {protocol}://{domain}/{savefolder}/{folder_name}/{file_name}\n"

@app.route('/', methods=('GET', 'POST'))
def main():
    guardian_log()
    if request.method == "POST":
        logger.info("[+]Session started")
        file_value = request.files['file_input']
        session['ttl_value'] = request.form['ttl_input']
        folder_name = create_folder()
        current_folders.append(folder_name)
        session['file_name'] = file_value.filename
        file_value.save(f"{path}/{savefolder}/{folder_name}/{session['file_name']}")
        x = threading.Thread(target=file_deletion, args=(file_value, folder_name,  session['ttl_value'],))
        x.start()
        return redirect(url_for('upload', folder_out=folder_name))
    session_kill()
    return render_template('index.html')

@app.route('/<folder_out>/')
def upload(folder_out):
    guardian_log()
    if folder_out in current_folders:
        if not 'file_name' in session:
            infile_name = os.listdir(f'{savefolder}/{folder_out}')
            return render_template('download.html', protocol=protocol, domain=domain, path_message=f'{savefolder}/{folder_out}', file_message=infile_name[0] )
        return render_template('uploaded.html', protocol=protocol, domain=domain, file_message=session['file_name'], ttl_message=session['ttl_value'], path_message=f'{savefolder}/{folder_out}')
    else:
        logger.warning(f'[!]{request.environ["REMOTE_ADDR"]} tried to access non existant folder /{folder_out}')
        return redirect(url_for('err'))

@app.route('/404')
def err():
    guardian_log()
    return render_template('404.html')

app.jinja_env.globals.update(session_kill=session_kill)

if __name__ == '__main__':
    app.run()
