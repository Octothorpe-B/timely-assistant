"""Test for implementing the R1 model."""

import assistant
import os

question = "What are my calendar events for today?"


if __name__ == "__main__":
    # Setup and obtain the classification and conversational models.
    classification_model = assistant.initialize_classification_model(
        "prompt-templates/r1-classifier-prompt.txt"
    )

    # Query the classifier to obtain the classifier values.
    classifications, classifier_tokens = assistant.query_classifier(
        classification_model, question
    )
