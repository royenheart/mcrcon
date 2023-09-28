from flask import Flask, render_template, request, abort
import logging
from logging.handlers import RotatingFileHandler
from threading import Timer
import gzip
import re
import shlex
import subprocess
import traceback
import os
import yaml

# log settings

mclog = logging.getLogger("mcverify_logger")
mclog.setLevel(logging.INFO)

formatter = logging.Formatter('[%(asctime)s] - %(levelname)s - %(message)s')
console_handler = logging.StreamHandler()
console_handler.setFormatter(formatter)
mclog.addHandler(console_handler)

# Decorator

is_abort = False
def abort_decorator(func):
    def inner(*args, **kwargs):
        if is_abort:
            mclog.error('Internal Server Error, it may result from errors of your server settings, please check logs')
            abort(500) # Internal Server Error
        else:
            ret = func(*args, **kwargs)
            return ret
    return inner

# Read configs, only read once

import os

tmp = os.getenv('MCVERIFY_BIN')
if tmp != None:
    mcverify_bin = tmp
else:
    mclog.warning("MCVERIFY BIN folder not defined! Will set MCVERIFY_BIN to './'")
    mcverify_bin = "./"

tmp = os.getenv('MCVERIFY_ETC')
if tmp != None:
    mcverify_etc = tmp
else:
    mclog.warning("MCVERIFY ETC folder not defined! Will set MCVERIFY_ETC to './'")
    mcverify_etc = "./"
    
tmp = os.getenv('MCVERIFY_VAR')
if tmp != None:
    mcverify_var = tmp
else:
    mclog.warning("MCVERIFY VAR folder not defined! Will set MCVERIFY_VAR to './'")
    mcverify_var = "./"

mclog.info("MCVERIFY_BIN SET TO {}".format(mcverify_bin))
mclog.info("MCVERIFY_ETC SET TO {}".format(mcverify_etc))
mclog.info("MCVERIFY_VAR SET TO {}".format(mcverify_var))

with open(mcverify_etc + '/mcverify.yaml', 'r') as stream:
    cfg = stream.read()
    mcverify_data = yaml.safe_load(cfg)

with open(mcverify_etc + '/mcrcon.yaml', 'r') as stream:
    cfg = stream.read()
    mcrcon_data = yaml.safe_load(cfg)

# Set file log 

try:
    mcverify_var_run = mcverify_var + "/mcverify-run" 
    os.makedirs(mcverify_var_run, exist_ok = True)
    file_handler = RotatingFileHandler(mcverify_var_run + "/logfile.log", maxBytes=1048576, backupCount=7, encoding='utf-8')
    file_handler.setFormatter(formatter)
    mclog.addHandler(file_handler)
except Exception:
    mclog.error(traceback.format_exc())
    mclog.error("Logger saved to file failed, check configs or file permission")

# APP setting

app = Flask(__name__, static_url_path = "/", template_folder = mcverify_etc + "/mcverifytemplates", static_folder = mcverify_etc + "/mcverifystatic")
app.config.from_file(mcverify_etc + '/server.yaml', load=yaml.safe_load)
app.logger.handlers = mclog.handlers
app.logger.setLevel(logging.INFO)

# Set mcrcon command prefix and check mcrcon configs, need combined with server command
# Check once

try:
    if mcrcon_data['passwd'] != None:
        mcrcon_passwd = '-p ' + mcrcon_data['passwd']
    else:
        mclog.warning('rcon passwd sets to none, it is not recommended')
        mcrcon_passwd = ''
    if mcrcon_data['location'] != None:
        mcrcon_location = mcrcon_data['location']
    else:
        mclog.warning('rcon location sets to none, will use default ./')
        mcrcon_location = './'
    if mcrcon_data['host'] != None:
        mcrcon_host = mcrcon_data['host']
    else:
        mclog.warning('rcon host sets to none, will use default localhost')
        mcrcon_host = 'localhost'
    if mcrcon_data['port'] != None:
        mcrcon_port = mcrcon_data['port']
    else:
        mclog.warning('rcon port sets to none, will use default 25575')
        mcrcon_port = 25575
    if mcrcon_data['wait'] != None:
        mcrcon_wait = mcrcon_data['wait']
    else:
        mclog.warning('rcon wait sets to none, will use default 1')
        mcrcon_wait = 1
    mcrcon_command_prefix = "{}/mcrcon -H {} -P {} {} -w {} ".format(
        mcrcon_location,
        mcrcon_host,
        mcrcon_port,
        mcrcon_passwd,
        mcrcon_wait
    )
    is_abort = False
except KeyError as e:
    mclog.error(str(e) + ' not defined in mcrcon_data! Check your mcrcon.yaml')
    is_abort = True
except Exception:
    mclog.error(traceback.format_exc())
    is_abort = True

# Check mcverify configs
# Check once

try:
    if mcverify_data['questions'] != None and len(mcverify_data['questions']) > 0:
        mcverify_questions = mcverify_data['questions']
        for d in mcverify_questions:
            for k, v in d.items():
                if k == 'q' and v == 'MCID':
                    mclog.error("Your questions should not contain question named 'MCID', it is engaged by mcverify")
                    raise Exception("MCID question multiple engaged")
                elif v == None:
                    mclog.error("Your questions should not contain a null value key: {} in quesiton {}".format(k, d))
                    raise Exception("Null value key contained")
        mcverify_questions_front = [{k: v for k, v in d.items() if k != 'a'} for d in mcverify_questions]
    else:
        mclog.warning("no questions, questions set to None")
        mcverify_questions = None
        mcverify_questions_front = None
    is_abort = False
except KeyError as e:
    mclog.error(str(e) + ' not defined in mcverify_data! Check your mcverify.yaml')
    is_abort = True
except Exception:
    mclog.error(traceback.format_exc())
    is_abort = True

try:
    if mcverify_data['MCID_pattern'] != None and mcverify_data['MCID_pattern'] != '':
        mcverify_mcid = mcverify_data['MCID_pattern']
    else:
        mclog.warning("no pattern for MCID, set to None")
        mcverify_mcid = None
except KeyError as e:
    mclog.warning('MCID_pattern not defined in mcverify_data!')
    mclog.warning("It's recommended to set a pattern for MCID")
    mcverify_mcid = None
except Exception:
    mclog.error(traceback.format_exc())
    is_abort = True

# Route

mclog.info("Ensure that an SSL certificate and HTTPS access are already enabled")

@app.route('/', methods=['POST', 'GET'])
@abort_decorator
def index():
    if request.method == 'POST':
        try:
            MCID = request.form['MCID']
            for d in mcverify_questions:
                answer = request.form[d['q']]
                expected = d['a']
                must = d['must']
                if must or answer != '':
                    match_result = re.match(expected, answer)
                    if not match_result:
                        # Not as expected
                        mclog.info("Got post: {} from client ip {}, not as expected".format(request.form, request.remote_addr))
                        return render_template('index.html', ret = {'r': 'no', 'resp': "Your answer for question '{}' is incorrect".format(d['q'])})
            if mcverify_mcid != None:
                match_result = re.match(mcverify_mcid, MCID)
                if not match_result:
                    # Not as expected
                    mclog.info("MCID: '{}' from client ip {}, not as expected".format(MCID, request.remote_addr))
                    return render_template('index.html', ret = {'r': 'no', 'resp': "MCID '{}' should be in format {}".format(MCID, mcverify_mcid)})
            # As expected
            mclog.info("Got post: {} from client ip {}, as expected, will exectue mcrcon".format(request.form, request.remote_addr))
            # Set command
            command = mcrcon_command_prefix + " \"/whitelist add {}\"".format(MCID)
            command_list = shlex.split(command)
            # call
            mclog.info("call mcrcon command: {}".format(command_list))
            process = subprocess.Popen(command_list, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            # define kill process
            def kill_process():
                process.terminate()
            # set mcrcon call most wait time
            time_sec = 4
            mclog.info("Wait for at most {} secs".format(time_sec))
            timer = Timer(time_sec, kill_process)
            try:
                timer.start()
                stdout_d, stderr_d = process.communicate()
                stdout_d = str(stdout_d)
                stderr_d = str(stderr_d)
                return_code = process.returncode
                # command_result has called in mc successfully need to be updated
                if return_code == 0 and not "Unknown command" in stdout_d:
                    mclog.info("mcrcon run successfully. output: {}".format(stdout_d))
                    return render_template('index.html', ret = {'r': 'yes', 'resp': "{} successfully added to whitelist".format(MCID)})
                else:
                    mclog.error("mcrcon stdout output: {}".format(stdout_d))
                    mclog.error("mcrcon stderr output: {}".format(stderr_d))
                    raise Exception("mcrcon exec failed")
            except Exception:
                mclog.error(traceback.format_exc())
                return render_template('index.html', ret = {'r': 'no', 'resp': "Whiltelist added failed, please report to sysadmin"})
            finally:
                timer.cancel()
        except Exception:
            mclog.error(traceback.format_exc())
            mclog.error("POST {} from client ip {}, but server not correctly response".format(request.form, request.remote_addr))
            abort(500)
    else:
        return render_template('index.html', questions = mcverify_questions_front)