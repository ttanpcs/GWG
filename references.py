import requests 
from itertools import groupby
import os
import json
from pathlib import Path
from random import sample
from reportlab.platypus import Paragraph, SimpleDocTemplate, Table, TableStyle, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors
from reportlab.pdfgen import canvas
from PyPDF2 import PdfReader, PdfWriter
from math import ceil

class GuitarReference:
    def __init__(self, name, link, capo, status):
        self.name = name
        self.link = link
        self.capo = capo
        self.status = status
    def __str__(self):
        return f'{self.name}'

    def __repr__(self):
        return f'{self.link}'

class GuitarReferenceGenerator:
    def __init__(
            self, 
            guitar_references, 
            percents = {
                "In pause" : 0.1, 
                "Not started" : 0.025,
                "In progress" : 0.8,
                "Done" : 0.3
            }
        ):
        gr_by_status = sorted(guitar_references, key=lambda gr: gr.status)
        gr_grouped_by_status = {key: list(group) for key, group in groupby(gr_by_status, key=lambda gr: gr.status)}
        culled_guitar_references = []
        for key, value in gr_grouped_by_status.items():
            culled_guitar_references.extend(sample(value, ceil(len(value) * percents[key])))
        gr_by_capo = sorted(culled_guitar_references, key=lambda gr: gr.capo)
        gr_grouped_by_capo = {key: list(group) for key, group in groupby(gr_by_capo, key=lambda gr: gr.capo)}
        self.guitar_references = gr_grouped_by_capo
    
    def __str__(self):
        return str(self.guitar_references)
    
    def draw(self, pdf_document):
        x_diff = 100
        story = []
        for key, value in self.guitar_references.items():
            data_intermediate = [
                Paragraph(f'<a href="{val.link}">{val.name}</a>', getSampleStyleSheet()['BodyText']) for val in value
                ]
            sublist_size = 4
            data = [[key]]
            data.extend([data_intermediate[i:i + sublist_size] for i in range(0, len(data_intermediate), sublist_size)])
            table = Table(data, colWidths=[x_diff for i in range(sublist_size)], hAlign='LEFT')
            style = TableStyle([
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('BACKGROUND', (0, 1), (-1, -1), colors.lightgrey),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ])
            table.setStyle(style)
            story.append(table)
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
            page["properties"]["Status"]["status"]["name"]
            )
            for page in data["results"]
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
