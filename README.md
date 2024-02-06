# Ada
Have any of you science questions answered in **well structured way**...

![image](https://github.com/rmikulec/ada/assets/15821744/d3804f92-22d3-4da0-87b5-0234b29ce4bc)


**With references!!**

![image](https://github.com/rmikulec/ada/assets/15821744/b2bbe25e-bfd4-4fdd-95b9-93dc1ef2a09c)



## Run Locally

### Prequisites
 - NodeJS
 - Python (>= version 3.9)
 - Have an OpenAI Key


### Steps


#### Start the backend

If reqs have not been installed by running

```bash
pip install -r requirements.txt
```

Export your openai key to environment variables. Can can either run directly in terminal, or create a `.env` file.

Terminal:

```bash
export OPENAI_API_KEY="<your-key>"
```

`.env`:
```.env
OPENAI_API_KEY=<your-key>
```

Then run the following to start the backend server

```bash
cd ./backend
python3 -m ada.app
```

#### Start the react app:

If reqs have not been installed by running

```bash
npx npm install
```

Then run the following to start the frontend server

```bash
cd frontend/ada
npx npm start
```


Go to `http://localhost:3000/` and enjoy!

