Important notes that I took while doing this project:

winratesOverGames conclusion: learned how to calculate op.gg like statistics (winrate)
fetch.py: simple API interactions
does15matter.py: first 15 minutes do matter

notes: update challenger db with timelines


winPredictor: comps themselves are not an accurate predictor of win/loss, while gd/15 is more 
              accurate, regardless of comp. when testing the model on other skill brackets, 
              the model proved to be significantly less accurate (around 20%).
              with GD15 as a variable, the prediction accuracy jumped to 70% on a set 
              of 200 challenger games. This will probably increase with data size.

              10/24/22 - hypothesis is that gd@15 would be a good predictor of wins in 
                         challenger, but not in lower elos.
                         data definitely needs pruning, need to not have to comb through
                         data while building the model
                         other possible indicators:
                            kill difference by team @ 15
                            first blood
                            first herald/first dragon
                            first tower
                            first baron
                            cs@10
                            lane gold difference at 15

                          