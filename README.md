# yt-summarizer
Summarizes youtube videos with the link using AI


## FastAPI
It is used to build APIs using Python.

- Used to have a backend web framework, and it handles all the backend work
like processing images, transcribing, captions.
- Uses the python functions as HTTP endpoints "/transcribe", "/caption"
- Used to communicate from the frontend to the backend 

### Virtual Environment
Used to isolate the packages you install for each project.
-  Create a new directory in the main dir 
- To create virtual environment : python -m venv .venv
  - python: use the program called python
  - -m: call a module as a script, we'll tell it which module next
  - venv: use the module called venv that normally comes installed with Python
  - .venv: create the virtual environment in the new directory .venv
- To activate the environment: source .venv/bin/activate
-  echo "*" > .venv/.gitignore: "echo" creates the file and writes "*" (all) in the gitignore file