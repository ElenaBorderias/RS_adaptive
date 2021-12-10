
### Setting up an env
Copy the env_template.json file and create a new one called env.json which you fill in with the required info.

### Setting up the virtual environmnet for PIP
For a new setup use:

```
python3 -m venv venv
```

To freeze an existing environment run:
```
pip freeze > requirements.txt
```
To install from requirements then run:
```
pip install -r requirements.txt
```



Then you can activate your env with (Linux/Macos):
```
source venv/bin/activate
```
and windows
```
venv\Scripts\activate
```

to deactivate the environment run:
```
deactivate
```
