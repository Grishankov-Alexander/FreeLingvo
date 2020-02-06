# FreeLingvo

FreeLingvo is an open source translation search GUI application that works offline and supports over 140 dictionaries.

![Example](https://i.imgur.com/Vmpz9Sp.png)

### For Users

##### Installers
The installer is currently available for Windows. You can go to [release v1.0](https://github.com/ache2014/FreeLingvo/releases/tag/v1.0) and download the "FreeLingvoSetup.exe".  
**Note**: *The installer is not signed yet, so Windows will probably warn you about an unrecognized application.*

##### To run or freeze the application manually:
1. Clone this repo to your current directory:  
`git clone https://github.com/ache2014/FreeLingvo.git`

2. Change to the projects directory:  
`cd FreeLingvo`

3. Create the virtual environment  
**Note**: *Use Python version 3.6.x. There are no guarantees that other versions will work.*  
`python3.6 -m venv venv`

4. Activate the virtual environment
```
# On Mac/Linux:
venv/bin/activate
# On Windows:
venv\scripts\activate.bat
```

5. Install the required libraries  
`pip install -r requirements/base.txt`

You are able to run the application with  
`fbs run`

You can also freeze it to the executable  
`fbs freeze`

For more information see the [fbs tutorial](https://github.com/mherrmann/fbs-tutorial).

### For developers

Feel free to make your contributions. Send your pull requests in the "develop" branch.  
Consider something from this list:
* Increase TEI XML Dictionaries parsing speed.
* Improve formatting quality for TEI XML dictionaries.

### Acknowledgements

Dictionaries were taken from the [FreeDict](https://freedict.org/) project. The FreeDict project strives to be the most comprehensive source of truly free bilingual dictionaries.

[fman build system](https://build-system.fman.io/) (fbs) is the fastest way to create a Python GUI. It solves common pain points such as packaging and deployment.

[Qt](https://www.qt.io/) is an excellent framework for building cross-platform GUI applications.