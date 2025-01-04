# Workout Instructor-Inator

this tool recives a text file, and creates an audio file with a set of verbal instructions separated by given time gaps.
also the instructor can count down to the next instruction, and background music is mixed in smoothly.

# Short Explanation

in order to make a simple instructor audio file, all you need is to create a .txt file, write the instruction you want the instructor to say, then go down a line and write the time in minuets for the instructor to wait, like in the following example:

```text
Lets get started with our workout.
0:02
get into a forearm plank for one and a half minutes
1:30
do 20 pushups and then rest
1:15
do 30 squats
1:00
```

then you run the program either by dragging this file onto the workout_instructorinator.py or workout_instructorinator.exe files or by running the workout_instructorinator file and then you will be asked to supply the path to the instructions .txt file that you made. pressing tab will trigger autocompletion.
then you will asked to supply the path to some folder that contains the songs you want to play in the background.
and then you will be asked to choose a speaker. see [speaker preferences](#speaker-preferences)

# Detailed Documentation

## requirments

- works for me on `python 3.10.1`
- packages required: `scipy`, `numpy`, `pyloadnorm` and `gTTs`. all can be downloaded via pip.  
(also `efipy` and `tqdm` are optional packages for making the program easier to use)
- ffmpeg should run from your command line.  
    you can check if you have ffmpeg on your command line by opening the command terminal (cmd on windows) and entering `ffmpeg -h`.  
    it works for me with ffmpeg-full-2023-01-12. but if you don't have ffmpeg then it's probably best you download the newest version buy following [these instructions](https://www.wikihow.com/Install-FFmpeg-on-Windows).
    this program should be 100% safe but I would still personally advise scanning with [virustotal](https://www.virustotal.com/gui/home/upload) as I personally do with any program I download.


## Instructions File

in order for the instructions audio file to be generated, a text file with the requested instructions should be provided. the file or set of files can be provided by dragging them onto `generate_audio_file.py`, by inputing them as command line argument, or by simply launching `generate_audio_file.py` and then providing the file path when inquired.  
the format for this instruction file is comprised of lines, (separated by line breaks). the lines alternate between being verbal instructions, and parameters for the waiting period between instructions. the parameters line starts with the duration of the waiting period in MINUTES:SECONDS, then a comma, and then you may add keywords for this waiting period.  
lines that start with "#" are comments and are skipped.  
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

### example

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

## Sets

also it is possible to incorporate Sets into the instruction file. this means that you can define an instruction file called a Set, that can be incorperated as a part of other instruction files. these Sets need to be located in the Sets folder . for example you can have an instruction file called Core_10_min_Workout inside the Sets folder and then in any other instruction file you can incorperate Core_10_min_Workout using the `@` charicter like so:

```text
Lets get started with our workout.
0:02
we are going to start with some core exercises
0:00
@Core_10_min_Workout
great job on completing that 10 minuets of core exercises. now let's go into a cooldown
0:00
@Full_Body_Cooldown
```

*note that filenames shouldn't have spaces in them*

## keywords

- ```announce_time```: the instructor announces the length of the current wait-line before starting
- ```countdown```: the instructor start's by announcing the total time, like with "announce_time". then every whole minute before the end, the instructor announces how much time is left. also it announces it 30 seconds and 10 seconds before the end. also the code checks and makes sure that no too announcements are too close together. (if they are then they are not done. for example if total time is 20 seconds, then the 10 second mark will not be announced)
- ```beepreps```: search the last line for a number, denote it N. then divide the given time into N repetitions and beep at the end of each repetition.
- ```delaybeep```: after this keyword, a number argument must follow denote the number T. the waitline will wait T seconds, beep, and then will wait the amount of time that was given as the first argument.

## background music

when the program is run, it will ask you to supply some background music folder

## preferences

the \$ symbol can be used for two things:

- define set choice preferences
- define speaker preferences

#### set choice preferences

it's possible to write a line that selects between several sets based on the context and the current "set choice preference"
an example for a line like this: ```@ ScapularPushUps | DiamondPushUps``` where the set that will be expressed in practice is either ScapularPushUps or DiamondPushUps depending on the choice preference that was given by the user. if no choice preference is given, then the user is prompted to indicate which one to choose, and then this choice will be used in similar inquiries.
in order to define a choice preference automatically without being prompted, one can write a line like this: ```$ ScapularPushUps | DiamondPushUps -> ScapularPushUps``` which will indicate that wherever a choice needs to be made between ScapularPushUps and DiamondPushUps, ScapularPushUps should be chosen. also the word "None" can be used on the right side of this arrow, to indicate to skip such sets altogether. making it easier then ever to skip leg day! for example with the following line:
```$ Squats -> None```
after this line, lines that call the Squats set like this one ```@ Squats``` will be effectively skipped.

#### speaker preferences

the speaker preferences allow you to change the accent and speed of the speaker. an example usage is the line
```$ Speaker:com.ng:x1.2```
which sets the speaker to have a nigerian accent and to talk at x1.2 speed
the possible accents are:

| Language/Region            | Domain   |
|----------------------------|----------|
| English (Australia)        | com.au   |
| English (United Kingdom)   | co.uk    |
| English (United States)    | us       |
| English (Canada)           | ca       |
| English (India)            | co.in    |
| English (Ireland)          | ie       |
| English (South Africa)     | co.za    |
| English (Nigeria)          | com.ng   |
| French (Canada)            | ca       |
| French (France)            | fr       |
| Portuguese (Brazil)        | com.br   |
| Portuguese (Portugal)      | pt       |
| Spanish (Mexico)           | com.mx   |
| Spanish (Spain)            | es       |
