# statvu-plus-plus
---
- **How to add Games to this Database**:
	1. Clone this repo and install all dependencies by running `install_dependencies.py`
	2. Add a `.mp4` file to the folder labeled `unprocessed-videos`
	3. Title the video using the following formatting: `MM.DD.YYYY.HOM.at.AWY.NET` where:
		 - MM.DD.YYYY is the month/day/year a game was played on
		- HOM is the home teams 3-letter acronym and AWY is AWY. All acronyms can be found [here](https://en.wikipedia.org/wiki/Wikipedia:WikiProject_National_Basketball_Association/National_Basketball_Association_team_abbreviations).
		- NET is the 3-letter acronym for the network the game was broadcast on. We will be using these abbreviations:
			- ESPN: **ESP**
			- TNT: **TNT**
			- FOX: **FOX**
			- ...
		- Example: the Los Angeles Lakers played the Golden State Warriors on 01/14/16 on TNT:
			- **01.14.2016.LAL.at.GSW.TNT**
	4. Once all videos you wish to add are formatted and placed in `unprocessed-videos` run the `main.py` script
