# yt-summarizer
Summarizes youtube videos with the link using AI


## FastAPI
It is used to build APIs using Python.

- Used to have a backend web framework, and it handles all the backend work
like processing images, transcribing, captions.
- Uses the python functions as HTTP endpoints "/transcribe", "/caption"
- Used to communicate from the frontend to the backend 
- Converts the http endpoints/requests from streamlit to json objects
  - POST: to create data. 
  - GET: to read data. 
  - PUT: to update data. 
  - DELETE: to delete data.
- @app.get("/"), @ -> decorator, the statement handles the requests that go the path '/'
- http://127.0.0.1:8000/items/?skip=0&limit=10 skip and limits are queries/params in the function associated with the decorator
### Virtual Environment
Used to isolate the packages you install for each project.
-  Create a new directory in the main dir 
- To create virtual environment : python -m venv .venv
  - python: use the program called python
  - -m: call a module as a script, we'll tell it which module next
  - venv: use the module called venv that normally comes installed with Python
  - .venv: create the virtual environment in the new directory .venv
- To activate the environment: source .venv/bin/activate
-  echo * > .venv/.gitignore: "echo" creates the file and writes "*" (all) in the gitignore file
- Uvicorn is a lightning-fast ASGI (Asynchronous Server Gateway Interface) web server used to run FastAPI (or other ASGI-compatible Python frameworks) in production or development