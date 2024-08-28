import os

from langchain.prompts.prompt import PromptTemplate

LLM_PYTHON_ANSWER_PATTERN = r"```python\s*(.*?)\s*```"

EXAMPLES_DIR_PATH = os.path.join(__file__, 'reaper_api_examples')
EXAMPLES_DATA = [
    {
        "instruction": "Create a new track with the file '/Documents/reaper_material/vocals.wav'",
        "answer_file": "new_media_track.py"
    },
    {
        "instruction": "Mute the track at index 0",
        "answer_file": "mute_track_by_index.py"
    },
    {
        "instruction": "Mute all tracks",
        "answer_file": "mute_all_tracks.py"
    },
    {
        "instruction": "Solo the track at index 0",
        "answer_file": "solo_track_by_index.py"
    },
    {
        "instruction": "Mute the track with the name 'my_track_name'",
        "answer_file": "mute_track_by_name.py"
    },
    {
        "instruction": "Decrease the volume of the track at index 0 by 50%",
        "answer_file": "track_volume.py"
    },
    {
        "instruction": "Change panning of the track at index 0 to 50% left",
        "answer_file": "track_pan.py"
    },
    {
        "instruction": "Increase the volume of the master track by 100%",
        "answer_file": "master_volume.py"
    },
    {
        "instruction": "Change panning of the master track to 75% right",
        "answer_file": "master_pan.py"
    },
    {
        "instruction": "For the track at index 0: add an equalization (EQ) with three bands:\n-A hipass filter: frequency 100 Hz, gain +6 dB, bandwidth 1.0 oct\n-A loshelf filter: frequency 1000 Hz, gain -3 dB, bandwidth 1.0 oct\n-A band filter: frequency 8000 Hz, gain +2 dB, bandwidth 1.0 oct",
        "answer_file": "track_eq.py"
    },
    {
        "instruction": "Disable the first bandpass filter on the track at index 0",
        "answer_file": "track_eq_disable_band.py"
    },
    {
        "instruction": "Disable the equalizer of the track at index 0",
        "answer_file": "track_eq_disable.py"
    },
    {
        "instruction": "Remove the EQ of the track at index 0",
        "answer_file": "track_eq_remove.py"
    } 
]

PROMPT_TEMPLATE_STR = """######## START OF RPP FILE ########
{rpp_content}
######## END OF RPP FILE ########

You are a code co-pilot, writing Python code to controll the digital audio workstation Reaper through its Python API.
Given the existing (potientially empty) Reaper project in the RPP file above, write Python code that edits the Reaper project according to the instruction below.
A Reaper Python API method `method_name` can be called with this line of code: `RPR.method_name` (see examples below).
Output code according to the examples below.
Output nothing else than the Python code.

{examples}

INSTRUCTION: {instruction}
RPP PROJECT PATH: {rpp_path}"""

PROMPT_EXAMPLE_TEMPLATE = """Here is an example:
Instruction: {instruction}
RPP project path: /Documents/my_reaper_projects/my_reaper_project.RPP
Output:
{answer_code}"""

PROMPT_TEMPLATE = PromptTemplate(
    input_variables=[
        "rpp_content",
        "examples",
        "instruction",
        "rpp_path"
    ],
    template=PROMPT_TEMPLATE_STR
)