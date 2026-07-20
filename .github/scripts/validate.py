#!/usr/bin/env python3
import os
import re
import sys
import subprocess

def check_expected_outputs():
    print("Checking expected output files...")
    expected_files = [
        "dist/index.html",
        "dist/agent-archive.html",
        "dist/build-week.html",
        "dist/migration-evidence.html",
        "dist/pipeline.html",
        "dist/stress-tests.html",
        "dist/codex-showcase.html",
        "dist/assets/css/field-guide.css",
    ]
    missing = []
    for file_path in expected_files:
        if not os.path.exists(file_path):
            missing.append(file_path)
            print(f"Error: Missing expected output file: {file_path}")
        else:
            print(f"OK: {file_path} exists")
    if missing:
        return False
    print("All expected output files exist.\n")
    return True

def get_valid_ids(content_dir):
    print("Discovering valid page IDs...")
    valid_ids = set()
    for root, _, files in os.walk(content_dir):
        for file in files:
            if file.endswith(".md"):
                file_path = os.path.join(root, file)
                with open(file_path, "r", encoding="utf-8") as f:
                    content = f.read()
                    # Parse frontmatter id:
                    match = re.search(r"^id:\s*([a-zA-Z0-9_-]+)", content, re.MULTILINE)
                    if match:
                        page_id = match.group(1)
                        valid_ids.add(page_id)
                        print(f"Found page ID '{page_id}' in {file_path}")
                    else:
                        print(f"Warning: No ID found in frontmatter of {file_path}")
    return valid_ids

def check_internal_links(content_dir, valid_ids):
    print("\nChecking internal documentation links...")
    # Matches [[target_id]] or [[target_id|text]]
    wiki_link_re = re.compile(r"\[\[([a-zA-Z0-9_-]+)(?:\|[^\]]+)?\]\]")
    errors = 0
    for root, _, files in os.walk(content_dir):
        for file in files:
            if file.endswith(".md"):
                file_path = os.path.join(root, file)
                with open(file_path, "r", encoding="utf-8") as f:
                    lines = f.readlines()
                    for line_num, line in enumerate(lines, 1):
                        matches = wiki_link_re.findall(line)
                        for target in matches:
                            if target not in valid_ids:
                                print(f"Error in {file_path}:{line_num}: wiki-link target '{target}' not found!")
                                errors += 1
                            else:
                                print(f"Link OK: {file_path}:{line_num}: [[{target}]]")
    return errors == 0

def check_not_committed():
    print("\nChecking that generated output is not committed in git...")
    try:
        output = subprocess.check_output(["git", "ls-files", "dist/"], text=True).strip()
        if output:
            print("Error: Generated files under dist/ are committed/tracked in git:")
            print(output)
            return False
        else:
            print("OK: No files in dist/ are committed or tracked.")
            return True
    except Exception as e:
        print(f"Error checking git files: {e}")
        return False

def main():
    content_dir = "site/content"
    success = True
    
    if not check_expected_outputs():
        success = False
        
    valid_ids = get_valid_ids(content_dir)
    if not valid_ids:
        print("Error: No valid page IDs found!")
        success = False
    
    if not check_internal_links(content_dir, valid_ids):
        success = False
        
    if not check_not_committed():
        success = False
        
    if not success:
        print("\nValidation failed!")
        sys.exit(1)
    else:
        print("\nAll validation checks passed successfully!")
        sys.exit(0)

if __name__ == "__main__":
    main()
