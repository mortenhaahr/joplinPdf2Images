# joplinPdf2Images
Converts a PDF to images in Joplin and adds it to the specified note as a printout.

## How to use it?
- Make sure you have installed the Python requirements as found in `requirements.txt`.
    - It is recommended to use a virtual environment but not necessary.
- Make sure Joplin Web Clipper is enabled and started in the client.
    - Go to Tools -> Options -> Web Clipper and enable it.
- Replace the API token in the script (around line 10)
- Run `./joplinPdf2Images.py [parent-notebooks] <note-name> <pdf-file>`
    - Concrete example with zsh: `./joplinPdf2Images.py "Wireless Sensor Networks" "Week 1" "Practical info" Practical\ Info\ of\ Course\ WSNs.pdf`
        - Assumes notebook structure: Wireless Sensor Networks -> Week 1 -> Practical Info. Copies printout of "Practical\ Info\ of\ Course\ WSNs.pdf" to it.

## How does it work?
- The script converts the PDF into seperate images and places it in the `output` folder.
- It uses the Joplin Web Clipper API for all interactions with Joplin which includes:
    - Identifying correct note through a tree structure.
    - Uploads the correct resources.
    - Changes the body of the note to contain the images.

## Known issues:
Currently the script does not support:
- Changing server URL/port. Always assumes localhost:41184
- Creating note structure if it doesn't exist.