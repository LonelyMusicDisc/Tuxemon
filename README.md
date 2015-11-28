![build-status](https://travis-ci.org/Tuxemon/Tuxemon.svg?branch=master)

Tuxemon
=========

Tuxemon is a free, open source monster-fighting RPG.

![screenshot](http://www.tuxemon.org/images/featurette-01.png)


Version
----

0.3.1


Requirements
-----------

Tuxemon uses a number of open source projects to work properly:

* *python* - version 2.7+
* *python-pygame* - python game library
* *python-pytmx* - python library to read Tiled Map Editor's TMX maps.
* *python-netifaces* - Cross platform network interface information.
* *neteria* - Game networking framework for Python.

*Optional*

* *libShake* - rumble library for Linux.


Installation
--------------

**Ubuntu**

```sh

sudo apt-get install python python-pygame python-pip python-imaging git python-netifaces
sudo pip install pytmx
git clone https://github.com/ShadowBlip/Neteria.git
cd Neteria
sudo python setup.py install
cd ..
git clone https://github.com/Tuxemon/Tuxemon.git
cd Tuxemon/tuxemon
./tuxemon.py

```

*Optional rumble support*

```sh

sudo apt-get install build-essential
git clone https://github.com/zear/libShake.git
cd libShake/
make; make install

```

**Mac OS X (Yosemite)**

```sh
ruby -e "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/master/install)"
brew tap Homebrew/python
brew update
brew install python
brew install sdl sdl_image sdl_mixer sdl_ttf portmidi hg git
pip install pytmx
pip install pillow
pip install hg+http://bitbucket.org/pygame/pygame
cd ~/git (or to your prefered development directory)
curl -O https://pypi.python.org/packages/source/n/netifaces/netifaces-0.10.4.tar.gz#md5=36da76e2cfadd24cc7510c2c0012eb1e
tar xvzf netifaces-0.10.4.tar.gz
cd netifaces-0.10.4
python setup.py install
git clone https://github.com/ShadowBlip/Neteria.git
cd Neteria
python setup.py install
git clone https://github.com/Tuxemon/Tuxemon.git
cd Tuxemon/tuxemon
ulimit -n 10000; python tuxemon.py

```


Controls
--------------

##### Tuxemon
* *Arrow Keys* - Movement
* *Enter* - Select/activate
* *ESC* - Menu/Cancel


##### Map Editor

Use *Tiled* map editor: http://www.mapeditor.org/


License
----

GNU v3

Copyright (C) 2015 William Edwards <shadowapex@gmail.com>,  
Benjamin Bean <superman2k5@gmail.com>

This software is distributed under the GNU General Public Licence as published
by the Free Software Foundation.  See the file LICENCE for the conditions
under which this software is made available.  Tuxemon also contains code from
other sources.

