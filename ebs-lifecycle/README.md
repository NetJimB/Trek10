# EBS Lifecycle Manager

Gov Cloud does not have AWS Lifecycle Manager, so until then there is this...

## TODO

- The template has the functions defined but each one doesn't have their required persmissions or schedul.
- Some simple unit tests would be useful.
- Some code reuse between functions could be added.

## Usage

### Install Dependencies

`PIPENV_VENV_IN_PROJECT=true pipenv sync --dev`

### Run Tests

`pipenv run pytest`

### Run Shell

`pipenv run python -i shell.py`
