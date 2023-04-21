# IZU-IZU-izi

The name says it all.

  ## Instalation
 Assuming Python and Pip are already installed, run 
 `pip install -r requirements.txt`
 ## Usage
-	Place the **xlogin.txt** (do not change it's name) into the cloned folder, then simply run the script.
	```
	usage: izu.py [-h] [-f FILE] [-a ALPHA] [-b BETA] [-c CFILE] [--verbose] [-s]

	options:
	-h, --help            		show this help message and exit
	-f FILE, --file FILE  		path to the ORIGINAL txt you received by mail, do not fix it your self
	-a ALPHA, --alpha ALPHA		specify a custom alpha value
	-b BETA, --beta BETA  		specify a custom beta value
	-c CFILE, --cfile CFILE		specify a custom file, table must be in the same style as in the mail
	--verbose             		verbose mode
	-s, --silent          		silent mode
	```
-	If you specified a custom file, make sure to preface it with the size of the matrix on the first line. The rest of the file consists if the matrix and specified paths. You must also manually specify the alpha and beta values using `-a` and `-b`.
	```
	3x3
	0    0     0
	0    0     0
	0   rew=-1 rew=1
	1 2 3 6 9
	1 2 5 2 3 6 9
	1 4 1 2 3 6 9
	1 4 7 8
	1 2 5 8
	```

-	To generate the result step by step, turn on verbose mode.

---
In case you find any bugs or incorrect calculations, please report them.
