# Scope-Analyser

For Analysing .csv files of Oscilloscope(Tested for Hantek DSO5202P)

The '.csv' files must have a start like this..

#timebase=4000000000(ps)

,#voltbase=1000000(uV)

where the 1st row "#timebase=4000000000(ps)" indicates the timescale to which the scope plot can be rescaled initialy

and the 2nd row "#voltbase=1000000(uV)" indicates the voltage division to which the plot may be initialy scaled to..

The initial configuration can be set up by the "self.config" file and the position of windows is saved in "self.pos" file
