

def to_experiment_name(prompts):
    return " ".join(str.split(prompts)).strip().replace(".", " ")\
              .replace("-", " ").replace(",", " ")\
              .replace(" ", "_")