from collections import Counter
import requests 
from itertools import groupby
import os
import json
from pathlib import Path
from random import sample, choices
from reportlab.platypus import Paragraph, SimpleDocTemplate, Table, TableStyle, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors
from reportlab.pdfgen import canvas
from PyPDF2 import PdfReader, PdfWriter
from math import ceil

SUBLIST_SIZE = 4

class GuitarReference:
    def __init__(self, name, link, capo, status, bpm):
        self.name = name
        self.link = link
        self.capo = capo
        self.status = status
        self.bpm = bpm
    def __str__(self):
        return f'{self.name}'

    def __repr__(self):
        return f'{self.link}'

class Status:
    def __init__(self, name, percent, color):
        self.name = name
        self.percent = percent
        self.color = color  

class GuitarReferenceGenerator:
    def __init__(
            self, 
            guitar_references, 
            statusi=None,
            metronome_check=3,
            metronome_valid=["In progress", "Needs refinement", "Done"]
        ):
        # Default statusi if not provided
        if statusi is None:
            statusi = {
                "In pause" : Status("In pause", 0.05, colors.lightgrey), 
                "Not started" : Status("Not started", 0.025, colors.palevioletred),
                "In progress" : Status("In progress", 0.7, colors.lightgreen),
                "Needs refinement" : Status("Needs refinement", 0.4, colors.lightyellow),
                "Done" : Status("Done", 0.2, colors.lightblue)
            }
        
        self.statusi = statusi  # Fix 1: Assign to self
        SUBLIST_SIZE = 3 # Assuming a constant for grid width

        # Setup
        gr_by_status = sorted(guitar_references, key=lambda gr: gr.status)
        gr_grouped_by_status = {key: list(group) for key, group in groupby(gr_by_status, key=lambda gr: gr.status)}

        # Create metronome exercises
        # Fix 2: Safety check for weights/valid categories
        valid_available = [s for s in metronome_valid if s in gr_grouped_by_status]
        metronome_categories = choices(valid_available, weights=[self.statusi[i].percent for i in valid_available], k=metronome_check)
        metronome_counts = Counter(metronome_categories)
        
        self.metronome_references = []
        for i in metronome_counts:
            # Fix 3: Use min() to prevent sampling more than available
            count = min(len(gr_grouped_by_status[i]), metronome_counts[i])
            self.metronome_references.extend(sample(gr_grouped_by_status[i], count))
        self.metronome_references = sorted(self.metronome_references, key=lambda gr: gr.capo)

        # Create general references
        culled_guitar_references = []
        for key, value in gr_grouped_by_status.items():
            # Fix 4: Safety check for sampling
            sample_size = min(len(value), ceil(len(value) * self.statusi[key].percent))
            culled_guitar_references.extend(sample(value, sample_size))
            
        gr_by_capo = sorted(culled_guitar_references, key=lambda gr: gr.capo)
        self.guitar_references = {key: list(group) for key, group in groupby(gr_by_capo, key=lambda gr: gr.capo)}

    def draw(self, pdf_document):
        x_diff = 150
        SUBLIST_SIZE = 3
        story = []
        styles = getSampleStyleSheet()

        # --- Section: Legend ---
        story.append(Paragraph("<b>Practice Status Legend</b>", styles['Heading2']))
        legend_data = []
        for name, stat in self.statusi.items():
            legend_data.append([name, f"{int(stat.percent * 100)}% Probability"])
        
        legend_table = Table(legend_data, colWidths=[x_diff, x_diff])
        legend_style = [('GRID', (0, 0), (-1, -1), 0.5, colors.grey)]
        for i, (name, _) in enumerate(legend_data):
            legend_style.append(('BACKGROUND', (0, i), (0, i), self.statusi[name].color))
        
        legend_table.setStyle(TableStyle(legend_style))
        story.append(legend_table)
        story.append(Spacer(1, 12))

        # --- Section: Metronome ---
        story.append(Paragraph("<b>Metronome Focus</b>", styles['Heading2']))
        metronome_data_raw = [
            Paragraph(f'<a href="{val.link}">{val.name}</a><br/>BPM: {val.bpm or "TBD"} | Capo: {val.capo}', styles['BodyText']) 
            for val in self.metronome_references
        ]
        
        # Grid logic for metronome
        metronome_rows = [metronome_data_raw[i:i + SUBLIST_SIZE] for i in range(0, len(metronome_data_raw), SUBLIST_SIZE)]
        if metronome_rows:
            m_table = Table(metronome_rows, colWidths=[x_diff] * SUBLIST_SIZE)
            m_table.setStyle(TableStyle([
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ]))
            story.append(m_table)
        story.append(Spacer(1, 12))

        # --- Section: General References (By Capo) ---
        story.append(Paragraph("<b>General References (By Capo)</b>", styles['Heading2']))
        for capo, refs in self.guitar_references.items():
            # Build the data grid
            rows = [refs[i:i + SUBLIST_SIZE] for i in range(0, len(refs), SUBLIST_SIZE)]
            
            # Prepare paragraph data for Table
            table_data = [[f"CAPO {capo}"]] # Header row
            for row in rows:
                formatted_row = [Paragraph(f'<a href="{r.link}">{r.name}</a>', styles['BodyText']) for r in row]
                # Pad row if it's shorter than SUBLIST_SIZE
                while len(formatted_row) < SUBLIST_SIZE:
                    formatted_row.append("")
                table_data.append(formatted_row)

            # Build Style Commands dynamically for individual cell backgrounds
            style_cmds = [
                ('SPAN', (0, 0), (-1, 0)), # Merge header
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey), # Header background
            ]

            # Fix 5: Apply background color to each cell individually
            for r_idx, row in enumerate(rows):
                for c_idx, ref in enumerate(row):
                    color = self.statusi[ref.status].color
                    # r_idx + 1 because row 0 is the "CAPO" header
                    style_cmds.append(('BACKGROUND', (c_idx, r_idx + 1), (c_idx, r_idx + 1), color))

            t = Table(table_data, colWidths=[x_diff] * SUBLIST_SIZE)
            t.setStyle(TableStyle(style_cmds))
            story.append(t)
            story.append(Spacer(1, 12))

        pdf_document.build(story)
def get_all_references():
    basedir = Path(os.path.abspath(os.path.dirname(__file__)))
    secret_path = basedir / 'secret.json'
    with open (secret_path, 'r') as f:
        secret = json.load(f)
        headers = {
            "Authorization": f'Bearer {secret["secret"]}',
            "Content-Type": "application/json",
            "Notion-Version": "2022-06-28",
        }

        url = f'https://api.notion.com/v1/databases/{secret["database_id"]}/query'

        payload = {"page_size": 100}
        response = requests.post(url, json=payload, headers=headers)

        data = response.json()

        results = data["results"]
        while data["has_more"]:
            payload = {"page_size": 100, "start_cursor": data["next_cursor"]}
            response = requests.post(url, json=payload, headers=headers)
            data = response.json()
            results.extend(data["results"])
        useful_data = [ 
            GuitarReference(
            page["properties"]["Name"]["title"][0]["plain_text"], 
            page["properties"]["Link"]["url"], 
            page["properties"]["Capo"]["number"],
            page["properties"]["Status"]["status"]["name"],
            page["properties"]["BPM"]["number"],
            )
            for page in results
            if len(page["properties"]["Instrument"]["multi_select"]) == 1 and page["properties"]["Instrument"]["multi_select"][0].get("name") == "Guitar"
        ]

        return GuitarReferenceGenerator(useful_data)

def generate_reference_page(file_path, temp_file_path="tmp.pdf"):
    pdf_writer = PdfWriter()
    pdf_document = SimpleDocTemplate(temp_file_path)
    references = get_all_references()
    references.draw(pdf_document)
    pdf_writer.append(file_path)
    pdf_writer.append(temp_file_path)

    pdf_writer.write(file_path)
    pdf_writer.close()
    absolute_temp_file_path = Path(os.path.abspath(os.path.dirname(__file__))) / temp_file_path
    os.remove(absolute_temp_file_path)
