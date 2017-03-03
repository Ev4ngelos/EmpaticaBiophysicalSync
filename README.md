# EmpaticaBiophysicalSync
A simple Python script that syncs and merges all Empatica E4 biophysical outputs into a common file.

<a href="https://store.empatica.com/products/e4-wristband?variant=945527715">Empatica E4</a> is a wrist-worn biophysical that measures continuously
one's biophsyical reponses such as, Heart Rate (HR), IBI, (Inter-Beat Interval), Electrodermal Activity (EDA), Blood Volume Pulse (BVP), skin temperature and 3-axis acceleration.
Biophysical responses are measured in different frequencies and stored in separate files (e.g., HR in 1 Hz whereas BVP in 64 Hz). This Python script syncs and merges all 
responses into a signle file by downsampling them to 1 Hz (matching the HR frequency rate).


Downsampling is performed for all biophysical responses (except for HR) by summing up or values in a period of one second and then dividing the totals by their corresponding frequencies.
For acceleration values, a low pass filter is applied for removing the effect of gravity and an overall (i.e., total acceleration) value is calculated.
Since IBI is a series of timestamps indicating when a heartbeat occurred, it has first to be encoded into a different variable before we can 
match it with variables acquired in regular intervals (e.g., HR). Thus, IBI produced from this script is the total IBI observed into timeslots of 
one second.


For running the script, simply place it in the same directory where the Empatica data are stored and then execute it.
It will combine all inputs into a single output CSV file.
