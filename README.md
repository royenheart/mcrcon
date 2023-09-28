# mcverify

mcverify use [flask](https://github.com/pallets/flask) and [mcrcon](https://github.com/Tiiffi/mcrcon) which is console based Minecraft [rcon](https://developer.valvesoftware.com/wiki/Source_RCON_Protocol) client for remote administration and server maintenance scripts. It provides a lightweight web where users only need to answer a few questions to automatically add their own whitelist permissions to the MC server with whitelist enabled.

This project is modified from the origin software: [mcrcon](https://github.com/Tiiffi/mcrcon). The original author is [Tiiffi](https://github.com/Tiiffi/). The C source code isn't modified, but the python and bash scripts are newly appended.

---

### Installation

##### building from source

```bash
git clone https://github.com/royenheart/mcverify.git mcverify
cd mcverify
make
make PREFIX=/path/to/your-installation-path install
```

Check [INSTALL.md](INSTALL.md) for futher details about what have been done.

The usage of mcrcon is described in [original README.md](https://github.com/Tiiffi/mcrcon/#readme)

---

### Usage

##### Function of files

- `mcverify` is a bash script that encapsulates the command to start `mcverify.py` which is the main flask program. You should always use it to start the mcverify web.
- `mcverify.py` is the main flask program. It is the core of the whole project.
- `mcverify.yaml` is a configuration file about mcverify runtime parameters, including questions and answers.
- `mcrcon.yaml` sets the parameters of mcrcon, set up this file correctly so that mcverify can call mcrcon correctly.
- `server.yaml` sets the flask configuration, go to [flask official documentation](https://flask.palletsprojects.com/en/latest/config/) for more information.
- `mcverifystatic/` folder includes static files of mcverify web, including css, images. You can modify them after your install the mcverify. Do not edit them in the project folder.
- `mcverifytemplates/` folder includes html files of mcverify web. The same as mcverifystatic, edit them in your installation path after you have installed mcverify.
- `mcrcon.c` and compiled `mcrcon` are the original source code and executable file of mcrcon. They are to connect to mc server with Rcon protocol.

###### How to start

Before your start, remember to enable rcon and rcon passwd(optional, but recommended) in your [**server.properties**](https://minecraft.gamepedia.com/Server.properties) file:

```config
enable-rcon=true
rcon.port=25575
rcon.password=your_rcon_pasword
```

After you install the mcverify. You should first edit the `mcverify.yaml` and `mcrcon.yaml` file. They are included in the `etc` folder of your installation path. What you need to edit is the questions you want your server users to answer. In mcverify.yaml, `q` key defines the question name, it can't be `MCID`. `a` key can be regex that matches the answer, it should use `^` as first char when `$` as the last, or the regex matching will cause error. `MCID_pattern` is the regex that matches the MCID.

Example is as follows:

```yaml
questions:
  - 
    q: "What is MC"
    a: "minecraft"
    must: true
  - 
    q: "What is Minecraft"
    a: "MC"
    must: false
  - 
    q: "What's your real name"
    a: "^[a-zA-Z]+$"
    must: true
MCID_pattern: "^[a-zA-Z0-9\\-_]+$"
```

In mcrcon.yaml, configure your mc server's rcon port and so on. Make sure mcrcon can connect to your mc server with configurations in this file. You can use `mcrcon` compiled executable file to test it.

An example is shown below:

```yaml
## Default is localhost
host: localhost
## Default is 25575
port: 25575
## Default is 1
wait: 1
passwd: your_server_rcon_passwd(optional)
## Default is ./
location: /path/to/mcverify/
```

When things done, export the `bin` folder of your installation path to ENV `PATH`, then you can start with `mcverify`. The origin file I use `gunicorn` to deploy the server, you can replace it with your favorite deploy methods. You can also open it with DEBUG mode, just start with `DEBUG=on mcverify`.

The log file will locate in `var/mcverify-run` folder of your installation path. You can check python source code for how logs are written.

The `etc` folder of installation path also includes `mcverifystatic` and `mcverifytemplates`, which includes html, css and images used by front page, it's ok to edit them as you like.

---

### Contact

Issues are welcomed. If you have any questions, contact me with my [email](mailto:royenheart@outlook.com).

---

### License

This project is licensed under the zlib License - see the [LICENSE](LICENSE) file for details.