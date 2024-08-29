# Reaper NLP

This repository provides a framework for controlling REAPER DAW through its API with natural language.


# Installation

1. Install REAPER.
2. Install python-reapy and follow its installation instructions (i.e. do not forget to run `python -c "import reapy; reapy.configure_reaper()"`).
3. Install this Python package.
4. Implement a Python function that takes a string of a prompt to an LLM as input and outputs the LLM anser. Use for example the OpenAI API.
5. Open REAPER.
6. Import this package and call `nl_reaper_command`.