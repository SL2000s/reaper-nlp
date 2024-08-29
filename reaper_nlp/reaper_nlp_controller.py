import os
import re

from langchain.prompts.prompt import PromptTemplate
from reapy import reascript_api as RPR
from typing import Callable

from config import (
    EXAMPLES_DIR_PATH,
    EXAMPLES_DATA,
    LLM_PYTHON_ANSWER_PATTERN,
    PROMPT_EXAMPLE_TEMPLATE,
    PROMPT_TEMPLATE,
)
from utils import file_content


def _build_examples_str(examples_dir_path: str = EXAMPLES_DIR_PATH,
                        examples_data: str = EXAMPLES_DATA):
    """
    Build a formatted string containing examples for use in a prompt.

    Args:
        examples_dir_path (str): The directory path where example answer files are stored.
        examples_data (str): A list of dicts the keys 'instruction' and 'answer_file'.

    Returns:
        str: A formatted string of examples, each consisting of an instruction and corresponding code.
    """
    examples_sb = []
    for example_data in examples_data:
        instruction = example_data.get("instruction", "")
        answer_file = example_data["answer_file"]
        answer_file_path = os.path.join(examples_dir_path, answer_file)
        answer_code = file_content(answer_file_path)
        example_str = PROMPT_EXAMPLE_TEMPLATE.format(
            instruction=instruction,
            answer_code=answer_code
        )
        examples_sb.append(example_str)
    examples_str = "\n\n".join(examples_sb)
    return examples_str


def _render_rpp_project(rpp_path: str, render_path: str = None,
                        audio_format: str = "mp3"):
    """
    Render a Reaper project file (.RPP) to an audio file.

    Args:
        rpp_path (str): Path to the .RPP project file.
        render_path (str, optional): Path to save the rendered audio file. If not provided, the 
                                     rendered file will be saved with the same name as the project 
                                     file, but with the specified audio format.
        audio_format (str, optional): Format of the rendered audio file. Defaults to "mp3".

    Returns:
        str: The path to the rendered audio file.
    """
    if render_path:
        audio_format = render_path.split(".")[-1]
    else:
        render_path = rpp_path.replace(".RPP", f".{audio_format}")

    output_dir = os.path.dirname(render_path)
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    if audio_format == 'mp3':
        audio_format_coding = 'l3pm'
    else:  # set to wav encoding
        audio_format_coding = 'evaw'

    RPR.GetSetProjectInfo_String(0, "RENDER_FORMAT", audio_format_coding, True)  # Set render format
    RPR.GetSetProjectInfo_String(0, "RENDER_FILE", os.path.dirname(render_path), True)  # Set output directory
    RPR.GetSetProjectInfo_String(0, "RENDER_PATTERN", os.path.basename(render_path), True)  # Set output file name
    
    # Additional rendering options can be set here using RPR.GetSetProjectInfo_* functions
    # For example, to set sample rate, you could use RPR.GetSetProjectInfo(PROJECT_INDEX, "RENDER_SRATE", 44100, True)

    RPR.Main_OnCommand(41824, 0)  # Command 41824 corresponds to the "File: Render project, using the most recent render settings" action
    return render_path


def _get_prompt(prompt_template: str, rpp_path: str, examples: str,
                instruction: str):
    """
    Generate a formatted prompt string for the LLM based on the provided template.

    Args:
        prompt_template (str): Template string for the prompt.
        rpp_path (str): Path to the .RPP project file.
        examples (str): Examples string containing formatted example instructions and code.
        instruction (str): Natural language instruction to Reaper for the LLM to process.

    Returns:
        str: A formatted prompt string ready for the LLM.
    """
    rpp_content = file_content(rpp_path)
    prompt = prompt_template.format(
        rpp_content=rpp_content,
        examples=examples,
        instruction=instruction,
        rpp_path=rpp_path
    )
    return prompt


def _post_process_llm_ans_python(llm_ans_python: str):
    """
    Post-process the LLM's output to extract valid Python code.

    Args:
        llm_ans_python (str): The raw output from the LLM.

    Returns:
        str: Extracted Python code from the LLM's output.
    """
    matches = re.findall(LLM_PYTHON_ANSWER_PATTERN, llm_ans_python, re.DOTALL)
    python_code = matches[0] if matches else llm_ans_python
    return python_code


def nl_reaper_command(
    rpp_path: str,
    nl_instruction: str,
    render_path: str,
    llm: Callable,
    audio_output_format: str = 'mp3',
    post_process: bool = False,
    examples: str = None,
    prompt_template: PromptTemplate = None
):
    """
    Execute a natural language Reaper command using an LLM and render the project to an audio file.

    Args:
        rpp_path (str): Path to the .RPP project file.
        nl_instruction (str): Natural language instruction for the LLM.
        render_path (str): Path to save the rendered audio file.
        llm (Callable): A callable LLM that accepts a prompt and returns Python code as a string.
        audio_output_format (str, optional): Format of the rendered audio file. Defaults to 'mp3'.
        post_process (bool, optional): Whether to post-process the LLM's output to extract Python code. Defaults to False.
        examples (str, optional): String containing examples to include in the prompt. Defaults to None.
        prompt_template (PromptTemplate, optional): Template for generating the LLM prompt. Defaults to None.

    Returns:
        str: The path to the rendered audio file.
    """
    examples = examples or _build_examples_str()
    prompt_template = prompt_template or PROMPT_TEMPLATE
    prompt = _get_prompt(prompt_template, rpp_path, examples, nl_instruction)
    code = llm(prompt)
    if post_process:
        code = _post_process_llm_ans_python(code)
    exec(code, globals())
    render_path = _render_rpp_project(rpp_path, render_path, audio_output_format)
    return render_path