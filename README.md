# sciXplain
Have any of you science questions answered in well structured way... with references!

<img width="1509" alt="Screenshot 2023-12-15 at 12 30 57 PM" src="https://github.com/rmikulec/scixplain/assets/15821744/e6cb1e52-3781-4a65-accb-c5b1325fa6b9">



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
python3 -m scixplain.app
```

#### Start the react app:

If reqs have not been installed by running

```bash
npx npm install
```

Then run the following to start the frontend server

```bash
cd frontend/scixplain
npx npm start
```


Go to `http://localhost:3000/` and enjoy!

