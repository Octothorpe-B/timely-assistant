import json
import pytest
from unittest.mock import patch, mock_open
from src.assistant import (
    save_json_to_dict,
    initialize_classification_model,
    initialize_conversational_model,
    query_classifier,
    query_ai_assistant,
    calculate_model_diagnostics,
    get_session_history,
    InMemoryHistory
)

def test_save_json_to_dict_valid_json():
    response = '{"key": "value"}'
    expected_output = {"key": "value"}
    assert save_json_to_dict(response) == expected_output

def test_save_json_to_dict_invalid_json():
    response = '{"key": "value"'
    assert save_json_to_dict(response) is None

@patch("builtins.open", new_callable=mock_open, read_data="template content")
@patch("src.assistant.ChatOllama")
def test_initialize_classification_model(mock_chat_ollama, mock_open):
    prompt_template = "path/to/template"
    model_chain = initialize_classification_model(prompt_template)
    assert model_chain is not None
    mock_open.assert_called_once_with(prompt_template, "r")
    mock_chat_ollama.assert_called_once()

@patch("src.assistant.ChatOllama")
def test_initialize_conversational_model(mock_chat_ollama):
    action_prompt = "action prompt"
    model_chain = initialize_conversational_model(action_prompt)
    assert model_chain is not None
    mock_chat_ollama.assert_called_once()

@patch("src.assistant.save_json_to_dict")
def test_query_classifier(mock_save_json_to_dict):
    mock_model = unittest.mock.Mock()
    mock_model.stream.return_value = [unittest.mock.Mock(content="response chunk")]
    mock_save_json_to_dict.return_value = {"key": "value"}

    question = "What is AI?"
    output, total_tokens = query_classifier(mock_model, question)

    assert output == {"key": "value"}
    assert total_tokens == len("response chunk".split())

@patch("src.assistant.save_json_to_dict")
def test_query_ai_assistant(mock_save_json_to_dict):
    mock_model = unittest.mock.Mock()
    mock_model.stream.return_value = [unittest.mock.Mock(content="response chunk")]

    question = "What is AI?"
    response, total_tokens = query_ai_assistant(mock_model, question)

    assert response == "response chunk"
    assert total_tokens == len("response chunk".split())

def test_calculate_model_diagnostics():
    start_time = 0
    end_time = 10
    total_tokens = 100
    with patch("builtins.print") as mock_print:
        calculate_model_diagnostics(start_time, end_time, total_tokens)
        mock_print.assert_any_call("\n\n\tModel diagnostics:")
        mock_print.assert_any_call("* Total tokens: 100")
        mock_print.assert_any_call("* Elapsed time: 10.00 seconds")
        mock_print.assert_any_call("* Average tokens per second: 10.00 t/s")

def test_get_session_history():
    user_id = "user1"
    conversation_id = "conv1"
    history = get_session_history(user_id, conversation_id)
    assert isinstance(history, InMemoryHistory)

def test_in_memory_history_add_messages():
    history = InMemoryHistory()
    messages = [unittest.mock.Mock()]
    history.add_messages(messages)
    assert history.messages == messages

def test_in_memory_history_clear():
    history = InMemoryHistory(messages=[unittest.mock.Mock()])
    history.clear()
    assert history.messages == []