CROSS = "\once \override NoteHead.style = #'cross"

STRUMMING_PATTERNS = [
    "b4 b8 [b8~] b8 [b8] b4",
    "b8 [b8] b8 [b8] r8 b8 r4",
    "b8 [b8] b8 [b8~] b8 [b8] b4",
    "b8 [b8~] b8 [b8] r2",
    "b4 b8 [b8~] b8 [b8] b8 [b8]",
    "b4 b8 [b8] b4 b8 [b8]",
    "b4 b8 [b8~] b2",
    "b8 [b8~] b8 [b8~] b8 [b8] b4",
    "b8 [b8] b4 r8 b8 b4",
    "b4 b8. [b16~] b16 [b16 b8] b8 [b16 b16]",
    "b8. [b16] r8 b8~ b2",
    "b8. [b16] r8 b8~ b8 [b8] b8 [b16 b16]",
    f'b8 [{CROSS} b8] b8 [{CROSS} b8] {CROSS} b8 [b8] b8 [{CROSS} b8]',
    f'b4 {CROSS} b8 [b8] b4 {CROSS} b8 [b8]',
    f'b4 {CROSS} b8 [b8] b8 [b8] {CROSS} b8 [b8]',
    f'b4 {CROSS} b8 [{CROSS} b8] {CROSS} b8 [{CROSS} b8] {CROSS} b8 [{CROSS} b8]',
]

TAPPING_PATTERNS = [
    # Ascending 3s
    [2, 0, 1],
    # Descending 3s
    [2, 1, 0],
    # 4s pattern 1
    [2, 0, 1, 0],
    # 4s pattern 2
    [2, 1, 0, 1]
]

CHROMATIC_SCALE = ["e", "f", "fis", "g", "aes", "a", "bes", "b", "c", "cis", "d", "ees"]

BASIC_CHORDS = ["c", "d", "e", "f", "fis", "g", "a", "bes", "b"]

UNIVERSAL_VARIATIONS = ["", "7", "m", "m7", "sus", "5"]

SPECIFIC_VARIATIONS = {
    "c" : ["2", "maj7", "/g", "/e", "/b"],
    "d" : ["2", "maj7", "/fis", "/a"],
    "e" : ["2", "maj7"],
    "f" : ["2", "maj7", "/a"],
    "fis" : [],
    "g" : ["2", "maj7", "/b", "/fis"],
    "a" : ["2", "maj7"],
    "bes" : ["2", "maj7"],
    "b" : ["2", "maj7"],
}

ALTERNATE_PICKING_PATTERNS = [
    [1, 2, 3, 4],
    [1, 2, 3],
    [1, 2, 4],
    [1, 3, 4]
]