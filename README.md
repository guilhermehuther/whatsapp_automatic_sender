[![Downloads](https://static.pepy.tech/badge/whatsappas)](https://pepy.tech/project/whatsappas) [![PyPI badge](https://badge.fury.io/py/whatsappas.svg)](https://badge.fury.io/py/whatsappas) [![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

# Overview

**whatsappas** is a library for sending automatic messages/photos on whatsapp.

# Installation
Install the latest stable version from PyPI:

```shell
pip install whatsappas
```

# Included function

* send_messages

# Quick start
``` python
>>> from whatsappas import send_messages
>>> send_messages()
```

# Usage and cautions

* Support sending automatic messages and/or photos to numbers and groups.

* Waiting times while sending messages is normal and needed for the well function of the library and security of your account on whatsapp.

* The library is built using essencialy [Selenium](https://www.selenium.dev/selenium/docs/api/py/api.html) and with all it's caveats.

* *.ipynb* files can face problems while running the function try to use *.py* scripts.

* A temporary file is created to keep count of the current position in the csv file. Set the parameter to *False* if you dont want to start from the previous position.

* The whatsapp doesn't support this type of activity and the risc of having your account banned is significantly even with all the counter measurements made in this library.

# Supported file

* The library only supports ***.csv files*** that follows the specific structure [Example .csv](https://github.com/guilhermehuther/whatsapp_automatic_sender/blob/main/example.csv).

* The header must be *Message;NumberOrGroup;photo_path*

* The *separator* in the csv must be '*;*' (semicolon).

* Paths for the photos must be full *C:\Users\CURRENT_USER\Desktop* or *blank* if you just want the message to be sent.

* Cellphone numbers can vary from country to country so be aware of how the Whatsapp API uses your cellphone number pattern in your country [Explication example for Brazilian numbering](https://faq.whatsapp.com/5913398998672934/). In the .csv example file has the USA and Brazil patterns of cellphone number usage respectively.
