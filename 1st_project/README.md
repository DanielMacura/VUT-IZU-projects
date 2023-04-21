# IZU-IZU-izi

The name says it all.

  ## Instalation
 Assuming Python and Pip are already installed, run 
 `pip install -r requirements.txt`
 ## Usage
Place the **xlogin.pdf** (do not change it's name) into the cloned folder, then simply run the script.

	usage: izu.py [-h] [-p PDF_PATH] [-l] [-n NAME] [--verbose] [-s]

	optional arguments:
	  -h, --help            			show this help message and exit
	  -p PDF_PATH, --pdf_path PDF_PATH	        path to the pdf you received by mail
	  -l, --latex           			generate LaTeX output tp xlogin.tex
	  -n NAME, --name NAME  			specify if exporting to LaTeX and your name has diacritics/accents
	  --verbose             			verbose mode
	  -s, --silent          			silent mode
If you specified the --latex flag, you still need to manually generate the PDF from the **xlogin.tex** file.
## Known issues

 If your name has diacritics/accents, they will be incorrectly parsed e.g.:
 
   Jožko Mokvička will be parsed as Joˇzko Mrkviˇcka. 
   To fix this undesired behavior, rerun with `izu.py -l -n Jožko\ Mrkvička` (don't forget to escape the space character)
## Acknowledgements
**Many thanks to galloj for his [izu_proj1_generator ](https://github.com/galloj/izu_proj1_generator).**

---
In case you find any bugs or incorrect calculations, please report them.
