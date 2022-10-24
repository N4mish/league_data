Important notes that I took while doing this project:

winratesOverGames conclusion: learned how to calculate op.gg like statistics (winrate)
winPredictor: comps themselves are not an accurate predictor of win/loss, while gd/15 is more 
              accurate, regardless of comp. when testing the model on other skill brackets, 
              the model proved to be significantly less accurate (around 20%).
              with GD15 as a variable, the prediction accuracy jumped to 70% on a set 
              of 200 challenger games. This will probably increase with data size.
fetch.py: simple API interactions
does15matter.py: first 15 minutes do matter

notes: update challenger db with timelines