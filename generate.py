import os
import argparse
from pathlib import Path
from patterns import STRUMMING_PATTERNS, BASIC_CHORDS, VARIATIONS, CHROMATIC_SCALE
from random import shuffle, choice

basedir = Path(os.path.abspath(os.path.dirname(__file__)))
file_path = basedir / 'warmup.ily'

def pick_chord(chords):
    return choice(chords), choice(VARIATIONS) 

def create_line(chords):
    notes = [(pick_chord(chords)) for i in range(4)]
    return f'{notes[0][0]}1:{notes[0][1]} {notes[1][0]}:{notes[1][1]} {notes[2][0]}:{notes[2][1]} {notes[3][0]}:{notes[3][1]}'

def create_pentatonic_exercies(f, index):
    major = CHROMATIC_SCALE[index]
    minor = CHROMATIC_SCALE[(index - 3) % len(CHROMATIC_SCALE)]
    tones = [index - 8, index - 5, index - 3, index, index + 2, index + 4, index + 7, index + 9, index + 12, index + 14]
    tones = list(filter(lambda x: x > 1, tones))[:6]
    f.write("<<\n\t\\new ChordNames {\n\t\t\\chordmode {\n") 
    f.write(f"\t\t\t{minor}1:m {major}\n")
    f.write("\t\t}\n\t}\n\t\\new TabStaff {\n\t\t")
    for i in range(6):
        f.write(f'{CHROMATIC_SCALE[tones[i] % len(CHROMATIC_SCALE)]}')
        if tones[i] < 8:
            f.write(',')
        f.write('2\\6 ')
    f.write("\n\t}\n")
    f.write(">>\n")

def create_strumming_exercises(f):
    shuffle(STRUMMING_PATTERNS)
    f.write("<<")
    for pattern in STRUMMING_PATTERNS:
        f.write("\n\t\\new ChordNames {\n\t\t\\chordmode {\n")
        f.write(f"\t\t\t{create_line(BASIC_CHORDS)}\n")
        f.write("\t\t}\n\t}\n\t\\new Voice \\with {\n\t\t\\consists Pitch_squash_engraver\n\t} \\relative c\'\'{\n\t\t\\autoBeamOff\n")
        for i in range(4):
            f.write(f"\t\t{pattern}\n")
        f.write("\t}\n")
    f.write(">>\n")

def generate():
    parser = argparse.ArgumentParser("Guitar Warmup Generator", description="generate randomized set of chord, strumming and pentatonic warmups.")
    parser.add_argument("--file", "-f", type=Path, default=file_path, help="ily generated file path")
    args = parser.parse_args()
    with open(args.file, "w") as f:
        f.write("\\version \"2.24.1\"\n")
        create_strumming_exercises(f)
        create_pentatonic_exercies(f, choice(range(len(CHROMATIC_SCALE))))

if __name__ == "__main__":
    generate()