#Package dependencies:
	* brew cask install chromedriver
	* pip install selenium
	* pip install numpy
	* pip install bs4
	* pip install pickle
	* pip install sklearn


## How to run the project

### To run against the online bot:

	1. "python main_piggy.py". This command will prompt a question on whether you want to acquire more data. If you want to acquire more data and watch the bot play against Cleverpiggy, then type in "yes" exactly. If you type anything else, it will use the data that you have in the raw_data/ folder and train the models on them. After training, when you run the same command, and type "yes", it will use the updated models.

### To play against humans
	
	1. "python main_human.py". Everything will be prompted at the menu.



