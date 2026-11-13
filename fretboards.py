import argparse
import subprocess
import os
from patterns import BASIC_CHORDS, UNIVERSAL_VARIATIONS, SPECIFIC_VARIATIONS 
from fretmap import FRET_MAP
from pathlib import Path

CHORD_DIR = "generated_chords"

def chord_2_filepath(chord, var):
  standardized_var = var.replace('/','-')
  return Path(os.path.abspath(os.path.join(CHORD_DIR, f"chord_{chord}{standardized_var}")) + ".cropped.pdf").as_uri()

def translate_note(chord):
   if chord == "bes":
      return "B \\flat"
   elif chord == "fis":
      return "F \\sharp"
   else:
      return chord.upper()

def chord_2_text(chord, var):
   chord_text = "{" + translate_note(chord)
   if var != "":
      if var[0] != '/':
          chord_text += " \\super " + var
      else:
          chord_text += "/" + translate_note(var[1:])   
   chord_text += "}"
   return chord_text

def create_override_line(name, tab):
   return f"""
  \\storePredefinedDiagram #default-fret-table \\chordmode {{ {name} }} #guitar-tuning \"{tab}\"
  """

def create_ly_output(name_list, override_block):
    score_string = "\n".join([f"""
        \\new ChordNames \\chordmode {{ {" ".join(name)} }}
        \\new FretBoards \\chordmode {{ {" ".join(name)} }}""" for name in name_list])
    return f"""
  \\version "2.24.0"
  \\include "predefined-guitar-fretboards.ly"
  #(ly:set-option 'crop #t)
  \\header {{
    tagline = ##f
  }}

  {override_block}

  \\score {{
    <<
        {score_string}
    >>
    \\layout {{
      indent = 0\\pt
      ragged-right = ##t
    }}
  }}
  """

def finalize_files(file_id, ly_content):
    ly_filename = os.path.join(CHORD_DIR, file_id + ".ly")
    base_output_path = os.path.join(CHORD_DIR, file_id)
    if not os.path.isfile(ly_filename):
        with open(ly_filename, "w", encoding="utf-8") as f:
            f.write(ly_content)
            
        cmd = f'lilypond -dno-point-and-click -dbackend=eps --pdf -o "{base_output_path}" "{ly_filename}"'
        result = subprocess.run(cmd, shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        
        if result.returncode == 0:
            print(f"Successfully generated diagram for: {file_id}")
        else:
            print(f"Skipped unsupported syntax for: {file_id}")
    else:
        print(f"Skipped generation for: {file_id} since it already exists")

def generate_fretboards(all = False):
    os.makedirs(CHORD_DIR, exist_ok=True)
    
    name_list = [[]]
    override_list = []
    for chord in BASIC_CHORDS:
        for var in UNIVERSAL_VARIATIONS+SPECIFIC_VARIATIONS[chord]:
            name = f'{chord}1:{var}'
            file_id = f"chord_{chord}{var.replace('/','-')}"
            tab = FRET_MAP[chord][var]
            override_block = create_override_line(name, tab)
            if all:
                override_list.append(override_block)
                name_list[-1].append(name)
            else:
                ly_content = create_ly_output([[name]], override_block)
                finalize_files(file_id, ly_content)
        name_list.append([])
    if all:
        ly_content = create_ly_output(name_list[:-1], '\n'.join(override_list))
        finalize_files("all_chords", ly_content)
    print(f"\nAll generated chord diagrams saved in '{CHORD_DIR}'!")

if __name__ == "__main__":
  parser = argparse.ArgumentParser("Guitar Chord Tab Generator", description="TSIA")
  parser.add_argument("--all", "-a", action="store_true", help="Generate all on a single pdf")
  args = parser.parse_args()
  generate_fretboards(args.all)