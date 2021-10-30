# This function is not intended to be invoked directly. Instead it will be
# triggered by an orchestrator function.
# Before running this sample, please:
# - create a Durable orchestration function
# - create a Durable HTTP starter function
# - add azure-functions-durable to requirements.txt
# - run pip install -r requirements.txt

import logging
from .. import LaunchContainer
from typing import Dict

def main(imagine:  Dict[str,str]) -> str:
    
    return LaunchContainer.launchVqganClipWithPhraseOnExistingInstance(phrase=imagine["phrase"],
    initImage=imagine.get("initImage",None),
    model=imagine.get("model",None),
    iterations=imagine.get("iterations",None),
    size=imagine.get("size",None))
