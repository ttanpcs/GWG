import os
import argparse
from pathlib import Path
from patterns import STRUMMING_PATTERNS, BASIC_CHORDS, SPECIFIC_VARIATIONS, UNIVERSAL_VARIATIONS, CHROMATIC_SCALE, TAPPING_PATTERNS, ALTERNATE_PICKING_PATTERNS
from random import shuffle, choice, sample
from references import generate_reference_page
from fretboards import chord_2_filepath, chord_2_text
import subprocess

basedir = Path(os.path.abspath(os.path.dirname(__file__)))
file_path = basedir / 'warmup.ily'

def pick_chord(chords):
    chord = choice(chords)
    return chord, choice(UNIVERSAL_VARIATIONS + SPECIFIC_VARIATIONS[chord]) 

def pick_tap(fret, is_major, start_fret, end_fret):
    tones = [fret - 5, fret, fret + 7, fret + 12, fret + 19]
    if is_major:
        tones += [fret - 8, fret + 4, fret + 16]
    else:
        tones += [fret - 9, fret + 3, fret + 15]
    tones = list(sorted(filter(lambda x: x >= start_fret and x <= end_fret, tones)))
    index = choice(range(0, len(tones) - 2))
    return tones[index: index + 3]

def create_line(chords, num=4):
    notes = [(pick_chord(chords)) for i in range(num)]
    note_strings = [ "\\tweak text \\markup { \\with-url " + f'"{chord_2_filepath(notes[i][0], notes[i][1])}" {chord_2_text(notes[i][0], notes[i][1])}'+ "} " + f'{notes[i][0]}1:{notes[i][1]}' for i in range(num)]
    return '\n'.join(note_strings)

def match_note(string, fret):
    base_notes = [24, 19, 15, 10, 5, 0]
    note_index = base_notes[string - 1] + fret
    note_string = f'{CHROMATIC_SCALE[note_index % len(CHROMATIC_SCALE)]}'
    if note_index < 8:
        note_string += ','
    elif (note_index - 8) // len(CHROMATIC_SCALE) >= 1:
        for i in range((note_index - 8) // len(CHROMATIC_SCALE)):
            note_string += '\''
    return note_string

def match_note_string(string, fret, beats = None): 
    if beats is None:
        return f'{match_note(string, fret)}'
    else:
        return f'{match_note(string, fret)}{beats}\\{string}'

def create_alternate_picking_exercise(f):
    f.write("<<\n\t\\new TabStaff {\n\t\t")
    for pattern in ALTERNATE_PICKING_PATTERNS:
        for alteration in [pattern, pattern, list(reversed(pattern)), list(reversed(pattern))]:
            f.write(f'\\tuplet {len(alteration)}/4 ')
            f.write("{ ")
            for note in alteration:
                f.write(" < ")
                for i in range(6): f.write(f'{match_note_string(i, note)} ') 
                f.write(" > ")

            f.write(" } ")

    f.write("\n\t}\n")
    f.write(">>\n")

def create_palm_muting_exercise(f):
    lines = [
        '<<',
        '\\new Voice \\with {\n',
        '\t\\consists Pitch_squash_engraver\n',
        '} \\relative c\'\'{\n',
        '\t\\autoBeamOff\n',
        '\t\\override TextSpanner.bound-details.left.text = "P.M"\n',
        '\tb16 [b16 b16 b16]\n',
        '\tb16 [b16 b16 b16]\n',
        '\tb16 [b16 b16 b16]\n',
        '\tb16 [b16 b16 b16]\n',
        '\n',
        '\tb16\\startTextSpan [b16 b16 b16]\n',
        '\tb16 [b16 b16 b16]\n',
        '\tb16 [b16 b16 b16]\n',
        '\tb16 [b16 b16 b16]\\stopTextSpan\n',
        '\n',
        '\t\\override TextSpanner.bound-details.left.text = "P.M"\n',
        '\tb16\\startTextSpan [b16 b16 b16]\\stopTextSpan\n',
        '\tb16 [b16 b16 b16]\n',
        '\tb16\\startTextSpan [b16 b16 b16]\\stopTextSpan\n',
        '\tb16 [b16 b16 b16]\n',
        '}\n'
        '>>',
    ]
    for line in lines:
        f.write(line)

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

def create_bending_exercises(f, start_fret, end_fret, num=5):
    f.write("<<\n\t\\new TabStaff {\n\t\t")
    for i in range(num):
        string = choice(range(1, 5))
        fret = choice(range(start_fret, end_fret + 1))
        bend_amount = choice([1, 2])
        f.write(f'{match_note_string(string, fret + bend_amount, 2)} ')
        f.write(f'{match_note_string(string, fret, 8)}\\^ ')
        f.write(f'{match_note_string(string, fret + bend_amount, 8)}\\^ ')
        f.write(f'{match_note_string(string, fret, 4)} ')

    f.write("\n\t}\n")
    f.write(">>\n")

def create_two_handed_tapping_exercises(f, strings, start_fret, end_fret):
    ADJUSTMENTS = {1:0, 2:7, 3:3}
    f.write("<<\n\t\\new ChordNames {\n\t\t\\chordmode {\n\t\t\t")
    memory = []
    for i in range(len(TAPPING_PATTERNS)):
        string = choice(strings)
        index = choice(range(len(CHROMATIC_SCALE)))
        note = CHROMATIC_SCALE[(index + ADJUSTMENTS[string]) % len(CHROMATIC_SCALE)]
        is_major = choice([0, 1]) == 1
        tones = pick_tap(index, is_major, start_fret, end_fret)
        if (is_major):
            f.write(f"{note}1 ")
        else:
            f.write(f"{note}1:m ")
        memory.append([string, tones])
    f.write("\n\t\t}\n\t}\n\t\\new TabStaff {\n\t\t")

    for i in range(len(TAPPING_PATTERNS)):
        if len(TAPPING_PATTERNS[i]) == 3:
            f.write("\\tuplet 3/4 { ")
        for j in TAPPING_PATTERNS[i]:
            f.write(f'{match_note_string(memory[i][0], memory[i][1][j], 4)} ')
        if len(TAPPING_PATTERNS[i]) == 3:
            f.write("} ")
    f.write("\n\t}\n")
    f.write(">>\n")

def create_sweep_exercises(f):
    f.write("<<\n\t\\new TabStaff {\n\t\t")
    f.write("\\tuplet 6/4 { ")
    for i in (list(range(3, 0, -1)) + list(range(1, 4))):
        f.write(f'\\once \\override TabNoteHead.style = #\'cross {match_note_string(i, 0, 4)}^\markup { "X" }')
    f.write("} ")
    for i in (list(range(4, 0, -1)) + list(range(1, 5))):
        f.write(f'\\once \\override TabNoteHead.style = #\'cross {match_note_string(i, 0, 8)}^\markup { "X" }')
    f.write("\\tuplet 6/4 { ")
    f.write(f'{match_note_string(3, 12, 4)} ')
    f.write(f'{match_note_string(2, 11, 4)} ')
    f.write(f'{match_note_string(1, 10, 4)} ')
    f.write(f'{match_note_string(1, 13, 4)} ')
    f.write(f'{match_note_string(2, 11, 4)} ')
    f.write(f'{match_note_string(3, 12, 4)} ')
    f.write("} ")
    f.write(f'{match_note_string(3, 10, 8)} (')
    f.write(f'{match_note_string(3, 12, 8)}) ')
    f.write(f'{match_note_string(2, 11, 8)} ')
    f.write(f'{match_note_string(1, 10, 8)} ')
    f.write(f'{match_note_string(1, 13, 8)} (')
    f.write(f'{match_note_string(1, 10, 8)}) ')
    f.write(f'{match_note_string(2, 11, 8)} ')
    f.write(f'{match_note_string(3, 12, 8)} ')
    
    f.write(f'{match_note_string(4, 9, 16)} (')
    f.write(f'{match_note_string(4, 12, 16)}) ')
    f.write(f'{match_note_string(3, 11, 8)} ')
    f.write(f'{match_note_string(2, 10, 8)} ')
    f.write(f'{match_note_string(1, 9, 8)} ')
    f.write(f'{match_note_string(1, 12, 16)} (')
    f.write(f'{match_note_string(1, 9, 16)})')
    f.write(f'{match_note_string(2, 10, 8)} ')
    f.write(f'{match_note_string(3, 11, 8)} ')
    f.write(f'{match_note_string(4, 12, 8)} ')

    f.write("\n\t}\n")
    f.write(">>\n")

def create_picking_exercises(f):
    pass

def create_palm_muting_exercises(f):
    pass

def create_slapping_exercises(f, num=6):
    f.write("<<\n\t\\new ChordNames {\n\t\t\\chordmode {\n") 
    f.write(f"\t\t\t{create_line(BASIC_CHORDS, num)}\n")
    f.write("\t\t}\n\t}\n\t\\new TabStaff {\n\t\t")
    for j in range(num):
        f.write(f'\\once \\override TabNoteHead.style = #\'cross {match_note_string(1, 0, 4)}^\markup { "X" }')
        f.write(f'\\once \\override TabNoteHead.style = #\'cross {match_note_string(2, 0, 4)}^\markup { "X" }')
        f.write(f'\\once \\override TabNoteHead.style = #\'cross {match_note_string(3, 0, 4)}^\markup { "X" }')
        f.write(f'\\once \\override TabNoteHead.style = #\'cross {match_note_string(4, 0, 4)}^\markup { "X" }')
    f.write("\n\t}\n")
    f.write(">>\n")

def create_header(f):
    f.write("\\version \"2.24.3\"\n")
    f.write("\\header {\n\t tagline = #f\n}\n")
    f.write("\\paper {\n")
    f.write("  indent = 0\n")
    f.write("  print-all-headers = ##t\n")
    f.write("}\n")

def generate():
    parser = argparse.ArgumentParser("Guitar Warmup Generator", description="generate randomized set of chord, strumming and pentatonic warmups.")
    parser.add_argument("--file", "-f", type=Path, default=file_path, help="ily generated file path")
    args = parser.parse_args()
    exercises = [
        lambda x: create_pentatonic_exercies(x, choice(range(len(CHROMATIC_SCALE)))),
        lambda x: create_bending_exercises(x, 5, 8),
        create_slapping_exercises,
        lambda x: create_two_handed_tapping_exercises(x, range(1, 4), 4, 19),
        create_sweep_exercises,
        create_alternate_picking_exercise,
        create_palm_muting_exercise
    ]

    with open(args.file, "w") as f:
        create_header(f)
        create_strumming_exercises(f)
        picked_exercises = sample(exercises, 3)
        for exercise in sorted(picked_exercises, key=exercises.index):
            exercise(f)
    result = subprocess.run(f'lilypond "{args.file}" > NUL 2>&1', shell=True)
    generate_reference_page(args.file.with_suffix('.pdf'))

if __name__ == "__main__":
    generate()