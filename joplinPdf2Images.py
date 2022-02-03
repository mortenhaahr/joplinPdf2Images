#!/usr/bin/env python3
from pdf2image import convert_from_path
import sys
import os
import shutil
import requests
import json
import copy

API_TOKEN = '7302229ee77697943426f8b38bba4c154c562f330020c3e9bed4950580cb0ce0807ee23ffa0f71d07f1eee79833b0914b552c7cb71f649b686525fd5dedb49c9'
MIME = 'multipart/form-data'

def main():
    # Get parent folder:
    argv = sys.argv.copy() # Copy because we want to manipulate
    script_name = argv[0]
    argv.pop(0)
    tree_length = len(argv) - 1
    if(tree_length < 0 or argv[-1][-4:] != ".pdf"):
        print(f"Usage: {script_name} [parent-notebooks] <note-name> <pdf-file>")
        exit(-1)
    
    tree = []
    for i in range(tree_length):
        tree.append(argv[i])

    pdfFileName = argv[-1]
    parent_length = tree_length - 1
    parents_reversed = tree[:-1]
    parents_reversed.reverse()
    print(tree)
    print(pdfFileName)

    cwd = os.path.abspath(os.getcwd())
    output_dir = cwd + "/output"
    try:
        os.mkdir(output_dir)
    except FileExistsError:
        shutil.rmtree(output_dir)
        os.mkdir(output_dir)

    # Test connection
    params = {"token": API_TOKEN}
    try:
        response = requests.get(
            'http://localhost:41184/ping', params=params)
        response.raise_for_status()
    except requests.exceptions.HTTPError as err:
        print("Couldn't ping the server")
        raise SystemExit(err)
    
    # Search for notes:
    try:
        response = requests.get(
            f'http://localhost:41184/search?query="{tree[-1]}"', params=params)
        response.raise_for_status()
    except requests.exceptions.HTTPError as err:
        print("Couldn't ping the server")
        raise SystemExit(err)
    body = response.json()
    candidates = [{'id': x['id'], 'parent_id': x['parent_id']} for x in body['items']]
    candidates_copy = copy.deepcopy(candidates)
    candidate_index = 0
    # Search for correct notebook to isolate wrong candidates
    for candidate in candidates:
        search_id = candidate["parent_id"]
        parents_reversed_len = len(parents_reversed)
        for i, parent_title in enumerate(parents_reversed):
            try:
                response = requests.get(
                    f'http://localhost:41184/folders/{search_id}', params=params)
                response.raise_for_status()
            except requests.exceptions.HTTPError as err:
                print("Couldn't ping the server")
                raise SystemExit(err)
            body = response.json()
            if body['title'] != parent_title:
                candidates_copy.pop(candidate_index)
                candidate_index -= 1
                break
            # If we are not at the final parent, but the parent_id is empty.
            # Happens when the match is good, but we expected a parent.
            elif i != parents_reversed_len - 1 and not body['parent_id']:
                candidates_copy.pop(candidate_index)
                candidate_index -= 1
                break
            else:
                search_id = body['parent_id']
        candidate_index += 1

    candidates = candidates_copy
    if not len(candidates) == 1:
        print("Something went wrong with finding the correct note. Exiting")
        exit(-1)

    notebook_page_id = candidates[0]['id']
    pages = convert_from_path(pdf_path=os.path.join(
        cwd, pdfFileName), size=(1000, None))
    page_body = ""
    for i, page in enumerate(pages):
        filename = f'image{i}.jpg'
        image_path = f'{output_dir}/{filename}'
        page.save(image_path, 'JPEG')
        file = {'data': (image_path, open(image_path, 'rb'), MIME)}
        try:
            response = requests.post('http://localhost:41184/resources', params=params, files=file,
                                     data={'props': json.dumps({'title': "",
                                                                'filename': f"{filename}"})})
            response.raise_for_status()
        except requests.exceptions.HTTPError as err:
            print(f"Failed to upload image: {i}. Exiting")
            raise SystemExit(err)
        body = response.json()
        page_body += f"![{filename}](:/{body['id']})<br><br>\n"
    print("Done uploading images. Putting in note now")

    try:
        response = requests.put(f'http://localhost:41184/notes/{notebook_page_id}', params=params, data=json.dumps({'body': page_body}))
        response.raise_for_status()
    except requests.exceptions.HTTPError as err:
        print(f"Failed edit notebook page. Exiting")
        raise SystemExit(err)


if __name__ == "__main__":
    main()
