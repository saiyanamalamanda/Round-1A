import fitz  # PyMuPDF
import os
import json
from collections import Counter

def extract_outline(pdf_path):
    doc = fitz.open(pdf_path)
    text_elements = []

    for page_num in range(len(doc)):
        page = doc[page_num]
        blocks = page.get_text("dict")["blocks"]

        for block in blocks:
            for line in block.get("lines", []):
                line_text = ""
                font_sizes = []
                font_weights = []

                for span in line.get("spans", []):
                    if span['text'].strip():
                        line_text += span['text'].strip() + " "
                        font_sizes.append(round(span['size']))
                        font_weights.append(700 if "Bold" in span["font"] else 400)

                if line_text.strip():
                    avg_size = sum(font_sizes) / len(font_sizes)
                    avg_weight = sum(font_weights) / len(font_weights)
                    text_elements.append({
                        "text": line_text.strip(),
                        "size": avg_size,
                        "weight": avg_weight,
                        "y": line["bbox"][1],
                        "page": page_num + 1
                    })

    # Analyze font size frequency to determine heading levels
    size_freq = Counter(round(el["size"]) for el in text_elements)
    sorted_sizes = sorted(size_freq.items(), key=lambda x: (-x[1], -x[0]))
    unique_sizes = [s[0] for s in sorted_sizes]

    # Assign heading levels based on size
    level_map = {}
    if len(unique_sizes) > 0: level_map[unique_sizes[0]] = "body"
    if len(unique_sizes) > 1: level_map[unique_sizes[1]] = "H3"
    if len(unique_sizes) > 2: level_map[unique_sizes[2]] = "H2"
    if len(unique_sizes) > 3: level_map[unique_sizes[3]] = "H1"
    if len(unique_sizes) > 4: level_map[unique_sizes[4]] = "title"

    title = ""
    outline = []

    for el in text_elements:
        level = level_map.get(round(el["size"]), "")
        if level == "title" and not title:
            title = el["text"]
        elif level in {"H1", "H2", "H3"}:
            outline.append({
                "level": level,
                "text": el["text"],
                "page": el["page"]
            })

    return {
        "title": title,
        "outline": outline
    }

def process_all_pdfs(input_dir, output_dir):
    for file in os.listdir(input_dir):
        if file.endswith(".pdf"):
            pdf_path = os.path.join(input_dir, file)
            output = extract_outline(pdf_path)
            json_path = os.path.join(output_dir, file.replace(".pdf", ".json"))
            with open(json_path, "w", encoding="utf-8") as f:
                json.dump(output, f, indent=2, ensure_ascii=False)

if __name__ == "__main__":
    input_dir = "input"
    output_dir = "output"
    os.makedirs(output_dir, exist_ok=True)
    process_all_pdfs(input_dir, output_dir)
