import os
import re
import shutil
import pathlib
import argparse

# Collections definition
COLLECTIONS = [
    {"src_path": "src/content/aphorisms", "name": "aphorisms", "title": "Aphorisms"},
    {"src_path": "src/content/docs/mascots", "name": "mascots", "title": "Mascots"},
    {"src_path": "src/content/docs/lorelog", "name": "lorelog", "title": "Lorelog"},
    {"src_path": "src/content/limericks", "name": "limericks", "title": "Limericks"},
    {"src_path": "src/content/haikus", "name": "haikus", "title": "Haikus"}
]

def parse_simple_yaml(yaml_text):
    data = {}
    current_key = None
    lines = yaml_text.split('\n')
    i = 0
    while i < len(lines):
        line = lines[i]
        stripped = line.strip()
        if not stripped:
            i += 1
            continue
            
        # Check for list item
        if stripped.startswith('- '):
            val = stripped[2:].strip().strip("'\"")
            if current_key:
                if current_key not in data or not isinstance(data[current_key], list):
                    data[current_key] = []
                data[current_key].append(val)
            i += 1
            continue
            
        if ':' in line:
            parts = line.split(':', 1)
            key = parts[0].strip()
            val = parts[1].strip()
            
            # Check for inline list
            if val.startswith('[') and val.endswith(']'):
                items_str = val[1:-1]
                data[key] = [item.strip().strip("'\"") for item in items_str.split(',') if item.strip()]
                current_key = key
                i += 1
                continue
                
            # Check for multiline string indicator >- or >
            if val == '>-' or val == '>':
                multiline = []
                i += 1
                while i < len(lines):
                    # Check indentation
                    if lines[i] == '' or lines[i].isspace():
                        multiline.append('')
                        i += 1
                        continue
                    lead_space = len(lines[i]) - len(lines[i].lstrip())
                    if lead_space > 0:
                        multiline.append(lines[i].strip())
                        i += 1
                    else:
                        break
                data[key] = ' '.join(multiline)
                current_key = key
                continue
                
            # Simple value
            val = val.strip("'\"")
            data[key] = val
            current_key = key
            i += 1
            continue
            
        i += 1
    return data

def strip_mdx_tags(body):
    # Remove import lines
    lines = body.split('\n')
    clean_lines = []
    for line in lines:
        if line.strip().startswith('import '):
            continue
        clean_lines.append(line)
    body = '\n'.join(clean_lines)
    
    # Strip custom MDX components (any tag starting with an uppercase letter)
    body = re.sub(r'<[A-Z]\w*\b[^>]*/>', '', body)
    body = re.sub(r'<[A-Z]\w*\b[^>]*>', '', body)
    body = re.sub(r'</[A-Z]\w*>', '', body)
    
    # Strip standard inline HTML tags that shouldn't be here
    html_tags_to_strip = ['div', 'span', 'details', 'summary', 'aside', 'section', 'article', 'header', 'footer', 'nav', 'main']
    for tag in html_tags_to_strip:
        body = re.sub(rf'<{tag}\b[^>]*>', '', body, flags=re.IGNORECASE)
        body = re.sub(rf'</{tag}>', '', body, flags=re.IGNORECASE)
        
    # Strip markdown images to avoid local/out-of-tree asset reference errors (EASSET)
    body = re.sub(r'!\[.*?\]\(.*?\)', '', body)
    # Strip HTML images
    body = re.sub(r'<img\b[^>]*>', '', body, flags=re.IGNORECASE)
    
    # Collapse three or more consecutive newlines into a single blank line
    body = re.sub(r'\n[ \t]*\n[ \t]*\n+', '\n\n', body)
    
    if not body.strip():
        body = "*(no body content)*"
        
    return body

# Global mappings
CASE_MAP = {}
POETRY_MAP = {}

def build_case_map(src_dir):
    global CASE_MAP, POETRY_MAP
    CASE_MAP = {}
    POETRY_MAP = {}
    
    # 1. First map mascots and lorelog caseNumbers
    for coll in COLLECTIONS:
        if coll["name"] not in ["mascots", "lorelog"]:
            continue
        coll_src = src_dir / coll["src_path"]
        if not coll_src.exists():
            continue
        files = list(coll_src.glob("*.md")) + list(coll_src.glob("*.mdx"))
        for f in files:
            try:
                content = f.read_text(encoding="utf-8")
                parts = content.split('---')
                if len(parts) >= 3:
                    fm_data = parse_simple_yaml(parts[1])
                    case_num = fm_data.get('caseNumber')
                    if case_num:
                        stem = f.stem.lower().replace(' ', '-')
                        CASE_MAP[case_num.strip('"')] = f"{coll['name']}/{stem}"
            except Exception as e:
                pass
                
    # 2. Map related poetry/aphorisms to parent caseNumbers
    for coll in COLLECTIONS:
        if coll["name"] not in ["haikus", "limericks", "aphorisms"]:
            continue
        coll_src = src_dir / coll["src_path"]
        if not coll_src.exists():
            continue
        files = list(coll_src.glob("*.md")) + list(coll_src.glob("*.mdx"))
        for f in files:
            try:
                content = f.read_text(encoding="utf-8")
                parts = content.split('---')
                if len(parts) >= 3:
                    fm_data = parse_simple_yaml(parts[1])
                    parent_entry = fm_data.get('parentEntry')
                    if parent_entry:
                        if isinstance(parent_entry, list):
                            parent_entry = parent_entry[0] if parent_entry else None
                        if parent_entry:
                            parent_entry = str(parent_entry).strip('"')
                            
                            # Clean title and body
                            title = fm_data.get('title', f.stem)
                            body = '---'.join(parts[2:])
                            clean_body = strip_mdx_tags(body)
                            
                            POETRY_MAP.setdefault(parent_entry, []).append({
                                "title": title,
                                "body": clean_body,
                                "type": coll["name"]
                            })
            except Exception as e:
                pass
    print(f"Mapped {len(CASE_MAP)} trunks and cached poetry for {len(POETRY_MAP)} entities.")

def process_file(file_path, collection_name):
    content = file_path.read_text(encoding="utf-8")
    
    # Separate frontmatter and body
    parts = content.split('---')
    if len(parts) < 3:
        yaml_text = ""
        body = content
    else:
        yaml_text = parts[1]
        body = '---'.join(parts[2:])
        
    # Parse YAML frontmatter
    fm_data = parse_simple_yaml(yaml_text)
    
    # Derive stem
    stem = file_path.stem.lower().replace(' ', '-')
    
    # Clean body
    clean_body = strip_mdx_tags(body)
    
    # Build new frontmatter (everything points to its collection index for flat navigation)
    new_fm = {}
    new_fm['id'] = f"{collection_name}/{stem}"
    new_fm['parent'] = collection_name
    
    # Build inline content additions for trunks (mascots/lorelog)
    case_num = fm_data.get('caseNumber')
    if case_num and collection_name in ['mascots', 'lorelog']:
        case_num = case_num.strip('"')
        poetry = POETRY_MAP.get(case_num)
        if poetry:
            by_type = {}
            for item in poetry:
                by_type.setdefault(item['type'], []).append(item)
                
            poetry_blocks = []
            for ptype in ['aphorisms', 'haikus', 'limericks']:
                if ptype in by_type:
                    ptype_title = ptype.title()
                    poetry_blocks.append(f"\n\n## Related {ptype_title}\n")
                    for item in by_type[ptype]:
                        poetry_blocks.append(f"### {item['title']}\n\n{item['body'].strip()}\n")
            clean_body = clean_body + "\n" + "\n".join(poetry_blocks)
    
    if 'title' in fm_data:
        new_fm['title'] = fm_data['title']
    else:
        new_fm['title'] = file_path.stem.replace('-', ' ').replace('_', ' ').title()
        
    if 'tags' in fm_data:
        raw_tags = fm_data['tags']
        if isinstance(raw_tags, str):
            raw_tags = [raw_tags]
        elif not isinstance(raw_tags, list):
            raw_tags = []
        clean_tags = [str(t).strip() for t in raw_tags if len(str(t).strip()) <= 64]
        clean_tags = clean_tags[:32]
        if clean_tags:
            new_fm['tags'] = clean_tags
        
    # Build meta block to prepend to body
    meta_lines = []
    
    date_val = fm_data.get('updatedAt') or fm_data.get('date')
    if date_val:
        meta_lines.append(f"**Date:** {date_val}  ")
        
    if 'caseNumber' in fm_data:
        meta_lines.append(f"**Summary:** {fm_data['caseNumber']}  ")
        
    if 'description' in fm_data:
        meta_lines.append(f"**Description:** {fm_data['description']}  ")
        
    if meta_lines:
        clean_body = '\n'.join(meta_lines) + '\n\n---\n\n' + clean_body
        
    # Write output
    output_fm_lines = ["---"]
    for k, v in new_fm.items():
        if k == 'tags' and isinstance(v, list):
            tags_str = ", ".join(f'"{t}"' for t in v)
            output_fm_lines.append(f"tags: [{tags_str}]")
        else:
            escaped_val = str(v).replace('"', '\\"')
            output_fm_lines.append(f'{k}: "{escaped_val}"')
    output_fm_lines.append("---")
    
    output_content = '\n'.join(output_fm_lines) + '\n\n' + clean_body.strip()
    return output_content

def main():
    parser = argparse.ArgumentParser(description="Convert raw Filed corpus to clean flat-navigation markdown files.")
    parser.add_argument("--src", type=str, required=True, help="Raw Filed repository path")
    parser.add_argument("--dst", type=str, required=True, help="Output clean content directory path")
    args = parser.parse_args()

    src_dir = pathlib.Path(args.src)
    dst_dir = pathlib.Path(args.dst)
    
    print(f"Starting conversion from {src_dir} to {dst_dir}...")
    
    # Pass 1: Build mappings
    build_case_map(src_dir)
    
    # Clear and recreate output directory
    if dst_dir.exists():
        shutil.rmtree(dst_dir)
    dst_dir.mkdir(parents=True, exist_ok=True)
    
    total_processed = 0
    
    for coll in COLLECTIONS:
        coll_src = src_dir / coll["src_path"]
        if not coll_src.exists():
            print(f"Skipping {coll['name']} - directory does not exist: {coll_src}")
            continue
            
        coll_dst = dst_dir / coll["name"]
        coll_dst.mkdir(parents=True, exist_ok=True)
        
        # Create index.md for collection
        index_content = f"""---
id: "{coll['name']}"
title: "{coll['title']}"
---

{coll['title']} archive.
"""
        (coll_dst / "index.md").write_text(index_content, encoding="utf-8")
        
        # Process files in collection
        files = list(coll_src.glob("*.md")) + list(coll_src.glob("*.mdx"))
        print(f"Processing {len(files)} files in '{coll['name']}'...")
        
        for f in files:
            try:
                # Target filename is stem + .md
                out_name = f.stem + ".md"
                out_path = coll_dst / out_name
                
                clean_content = process_file(f, coll["name"])
                out_path.write_text(clean_content, encoding="utf-8")
                total_processed += 1
            except Exception as e:
                print(f"Error processing {f}: {e}")
                
    # Create the root index.md (Homepage)
    home_content = """---
id: "index"
title: "Filed & Forgotten Archive"
---

# Welcome to the Filed & Forgotten Archive

This is the central directory of all compiled records, mascots, lorelogs, and procedural poetry.

### Browse the Collections

*   [Mascots](mascots/index.html) — Database of identity officers and compliance entities.
*   [Lorelog](lorelog/index.html) — System logs and procedural failure audits.
*   [Aphorisms](aphorisms/index.html) — Sarcastic statements on deferred accountability.
*   [Limericks](limericks/index.html) — Rhyming compliance warnings.
*   [Haikus](haikus/index.html) — Syllabic routing logs.
"""
    (dst_dir / "index.md").write_text(home_content, encoding="utf-8")
    print("Created root index.md")
    
    print(f"Conversion complete! Processed {total_processed} files.")

if __name__ == "__main__":
    main()
