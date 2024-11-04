
import logging
import os
from openai import OpenAI

import time
import re
from pathlib import Path
import threading

file_dir = os.path.dirname(os.path.abspath(__file__))  # Location of this file
with open(Path(f"{file_dir}/../gpt/system_prompt.txt")) as f:
    system_prompt = f.read()
with open(Path(f"{file_dir}/../gpt/evolution_prompt.txt")) as f:
    evolution_prompt = f.read()
with open(Path(f"{file_dir}/../gpt/initial_example_prompt.txt")) as f:
    initial_example_prompt = f.read()
with open(Path(f"{file_dir}/../gpt/evolution_example_prompt.txt")) as f:
    evolution_example_prompt = f.read()
with open(Path(f"{file_dir}/../gpt/terrain_example_initial.py")) as f:
    initial_terrain_example = f.read()
with open(Path(f"{file_dir}/../gpt/terrain_example_evolution.py")) as f:
    evolution_terrain_example = f.read()

client = OpenAI()
replay_run = "/home/exx/Projects/autoenv/autoenv/outputs/autoenv/2024-07-04_23-19-34/gpt_queries"  # Set to a log directory (e.g., "outputs/.../gpt_queries") to replay a specific run's LLM responses
replay_idx = 0   # Used to keep track of which response to load from a run (if replay_run is set)
replay_idx_lock = threading.Lock()
replay_initial_only = False  # Set to True to only replay initial queries and generate evolution queries from scratch

gpt_pricing = {
    "gpt-4o-2024-05-13": (5e-6, 1.5e-5),  # GPT-4o: $0.005/1K input, $0.015/1K output
    "gpt-4-0125-preview": (1e-5, 3e-5),   # GPT-4 Turbo: $0.01/1K input, $0.03/1K output
    "gpt-4-0613": (3e-5, 6e-5),           # GPT-4: $0.03/1K input, $0.06/1K output
    "gpt-3.5-turbo-0125": (5e-7, 1.5e-6)  # GPT-3.5 Turbo: $0.0005/1K input, $0.0015/1K output
}

def prepare_prompts(cfg):
    global system_prompt, initial_example_message, evolution_example_message
    
    initial_example_message = initial_example_prompt.replace("<INSERT EXAMPLE HERE>", initial_terrain_example)
    evolution_example_message = evolution_example_prompt.replace("<INSERT INITIAL EXAMPLE HERE>", initial_terrain_example)
    evolution_example_message = evolution_example_message.replace("<INSERT EVOLUTION EXAMPLE HERE>", evolution_terrain_example)

def query_gpt_initial(cfg, num_samples=1):
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": initial_example_message}
    ]
    return query_gpt(cfg, messages, num_samples)

def query_gpt_evolution(cfg, prev_terrain_code, eval_statistics, terrain_stats, all_best_terrain_descriptions, num_samples=1):
    global replay_run
    if replay_initial_only:
        replay_run = ""

    all_best_terrain_descriptions = "\n".join(["- " + desc for desc in all_best_terrain_descriptions])

    evolution_message = evolution_prompt
    evolution_message = evolution_message.replace("<INSERT POLICY STATISTICS HERE>", eval_statistics)
    evolution_message = evolution_message.replace("<INSERT TERRAIN STATISTICS HERE>", terrain_stats)
    evolution_message = evolution_message.replace("<INSERT TERRAIN DESCRIPTIONS HERE>", all_best_terrain_descriptions)

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "assistant", "content": "```python\n" + prev_terrain_code + "\n```"},
        {"role": "user", "content": evolution_message},
        {"role": "user", "content": evolution_example_message}
    ]
    return query_gpt(cfg, messages, num_samples)

def query_gpt(cfg, messages, num_samples=1):
    logging.info(f"Querying OpenAI API for {num_samples} samples using {cfg.gpt_model}...")

    if replay_run:
        global replay_idx

        log_dir_list = []
        for root, dirs, _ in os.walk(replay_run):
            for dir in dirs:
                if "query" in dir:
                    log_dir_list.append(os.path.join(root, dir))
        log_dir_list = sorted(log_dir_list)

        with replay_idx_lock:
            log_dir = log_dir_list[replay_idx]
            responses = []
            files = [i for i in os.listdir(log_dir) if "response" in i]
            files = sorted(files, key=lambda x: int(x.rstrip(".txt").split("-")[-1]))  # Sort numerically
            for file in files[:num_samples]:
                with open(os.path.join(log_dir, file), "r") as f:
                    responses.append(f.read())
            prompt_cost, response_cost = 0, 0
            logging.info(f"Loaded past response from {log_dir}")
            replay_idx = (replay_idx + 1) % len(log_dir_list)
    else:
        responses = None
        attempts = 10
        for i in range(attempts):
            try:
                responses = client.chat.completions.create(
                    model=cfg.gpt_model,
                    messages=messages,
                    n=num_samples
                )
                break
            except Exception as e:
                logging.warning(f"Error querying OpenAI API (attempt {i})...")
                logging.warning(e)
                time.sleep(1)
        if not responses:
            logging.error(f"Failed to query OpenAI API {attempts} times!")
            return None

        prompt_tokens, response_tokens = responses.usage.prompt_tokens, responses.usage.completion_tokens
        prompt_pricing, response_pricing = gpt_pricing[cfg.gpt_model]
        prompt_cost, response_cost = prompt_pricing * prompt_tokens, response_pricing * response_tokens  # GPT-4 Turbo pricing, $0.01/1K input, $0.03/1K output
        logging.info(f"Received response, used {prompt_tokens} prompt tokens (${prompt_cost:.2f}) and {response_tokens} response tokens (${response_cost:.2f})")
        responses = [choice.message.content for choice in responses.choices]

    parsed_responses = []
    for response in responses:
        patterns = [
            r'```python(.*?)```',
            r'```(.*?)```',
            r'^(.*?)$',
        ]
        for pattern in patterns:
            string = re.search(pattern, response, re.DOTALL)
            if string:
                parsed_response = string.group(1).strip()
                # Delete code outside of the function (check for un-indented lines)
                parsed_response = parsed_response.split("\n")
                parsed_response = [line for line in parsed_response
                                   if line == "" or line.startswith(" ") or line.startswith("def") or line.startswith("import")]
                parsed_response = "\n".join(parsed_response)
                parsed_responses.append(parsed_response)
                break
    
    return messages, responses, parsed_responses, prompt_cost, response_cost

def log_gpt_query(messages, responses, save_dir):
    if not os.path.exists(save_dir):
        os.makedirs(save_dir)
    
    with open(f"{save_dir}/prompt.txt", "w") as f:
        f.write("\n\n".join([message["content"] for message in messages]))
    
    for i, response in enumerate(responses):
        with open(f"{save_dir}/response-{i}.txt", "w") as f:
            f.write(response)