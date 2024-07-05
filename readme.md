# Workout Instructor-Inator

this tool recives a text file, and creates an audio file with a set of verbal instructions separated by given time gaps.
also the instructor can count down to the next instruction, and background music is mixed in smoothly.

## requirments

- ffmpeg should run from your command line
- scipy, numpy, pyloadnorm and gTTs packages
- works for me on python 3.10.1

## Instructions File

in order for the instructions audio file to be generated, a text file with the requested instructions should be provided. the files name has to be "instructions.txt", and it should simply exists in the present working directory. the format for this file is comprised of lines, (separated by line breaks). the lines alternate between being verbal instructions, and parameters for the waiting period between instructions. the parameters line starts with the duration of the waiting period in MINUETS:SECONDS, then a comma, and then you may add keywords for this waiting period.
the file looks like this:

```text
instructions text to be read
time to wait MINUETS:SECONDS, keywords separated by comma
instructions text to be read
time to wait MINUETS:SECONDS, keywords separated by comma
...
```

for now the only keyword is countdown, which means that the instructor will announce when you are half way to completion, 75% to completion, and ten seconds before completion.

#### example

here is an example for the beginning of some workout

```text
Lets get started with our workout.
0:02
get into a forearm plank for one and a half minuets
1:30, countdown
do 20 pushups and then rest
1:15
do 40 squats
1:00
do a v-sit for two minuets
2:00, countdown
```

## background music

when the program is run, it will ask you whether you want background music. if you answer yes, it will as you to supply some background music file
