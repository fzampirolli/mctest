# Integration: MCTest + Moodle + VPLAY
## Author of the VPL modifications: Heitor Savegnago
## Orientation: Paulo Pisani

###Implementations to allow the integration of MCTest and VPL + Moodle.

MCTest creates activities to be answered by the 
student during an exercise, sends a set of test 
cases in JSON format to the teacher's email, in 
addition to the activity variation (parametric 
questions) designed for each student in CSV format. 
To fix it automatically, create a VPL activity in 
Moodle, upload these JSON and CSV files, as well as 
other files in this folder (use the latest version). 
The student receives automatic feedback on his code, 
such as an activity grade.