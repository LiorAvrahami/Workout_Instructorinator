# Workout Instructor-Inator

this tool recives a text file, and creates an audio file with a set of verbal instructions separated by given time gaps.
also the instructor can count down to the next instruction, and background music is mixed in smoothly.

## requirments

- ffmpeg should run from your command line
- scipy, numpy, pyloadnorm and gTTs packages
- works for me on python 3.10.1

## Instructions File

in order for the instructions audio file to be generated, a text file with the requested instructions should be provided. the files name has to be "instructions.txt", and it should simply exists in the present working directory. the format for this file is comprised of lines, (separated by line breaks). the lines alternate between being verbal instructions, and parameters for the waiting period between instructions. the parameters line starts with the duration of the waiting period in MINUTES:SECONDS, then a comma, and then you may add keywords for this waiting period.
lines that start with "#" are skipped.
the file looks like this:

```text
instructions text to be read
time to wait MINUTES:SECONDS, keywords separated by comma
instructions text to be read
time to wait MINUTES:SECONDS, keywords separated by comma
# this line is a comment, and will be skipped by the parser.
instructions text to be read
time to wait MINUTES:SECONDS, keywords separated by comma
...
```

an example keyword is countdown, which means that the instructor will count down to completion of this line.

#### example

here is an example for the beginning of some workout

```text
Lets get started with our workout.
0:02
get into a forearm plank for one and a half minutes
1:30, countdown
do 20 pushups and then rest
1:15
do 30 squats
# the next line will wait 7 seconds, then beep, then the one minute will start, and beep every 2 seconds
1:00, beepreps, delaybeep, 7
do a v-sit for two minutes
2:00, countdown
```

## keywords

- announce_time: the instructor announces the length of the current wait-line before starting
- countdown: the instructor start's by announcing the total time, like with "announce_time". then every whole minute before the end, the instructor announces how much time is left. also it announces it 30 minuets and 10 minuets before the end. also the code checks and makes sure that no too announcements are too close together. (if they are then they are not done. for example if total time is 20 seconds, then the 10 second mark will not be announced)
- beepreps: search the last line for a number, denote it N. then divide the given time into N repetitions and beep at the end of each repetition.
- delaybeep: after this keyword, a number argument must follow denote the number T. the waitline will wait T seconds, beep, and then will wait the amount of time that was given as the first argument.

## background music

when the program is run, it will ask you whether you want background music. if you answer yes, it will as you to supply some background music file
