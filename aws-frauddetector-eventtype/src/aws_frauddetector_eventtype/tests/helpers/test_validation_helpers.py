from ...helpers import validation_helpers
from botocore.exceptions import ClientError
from unittest.mock import MagicMock
from .. import unit_test_utils


def test_check_if_get_labels_succeeds_client_error_returns_false():
    # Arrange
    mock_afd_client = unit_test_utils.create_mock_afd_client()
    mock_afd_client.get_labels = MagicMock()
    mock_afd_client.exceptions.ResourceNotFoundException = ClientError
    # We retry NotFound (for consistency), so return not found twice
    mock_afd_client.get_labels.side_effect = [
        ClientError({"Code": "", "Message": ""}, "get_labels"),
        ClientError({"Code": "", "Message": ""}, "get_labels"),
    ]

    # Act
    result = validation_helpers.check_if_get_labels_succeeds(mock_afd_client, unit_test_utils.FAKE_NAME)

    # Assert
    assert len(result) == 2
    assert result[0] is False
    assert result[1] is None


def test_check_if_get_labels_succeeds_client_success_returns_true_and_response():
    # Arrange
    get_labels_response = {"labels": [unit_test_utils.FAKE_FRAUD_LABEL]}

    mock_afd_client = unit_test_utils.create_mock_afd_client()
    mock_afd_client.get_labels = MagicMock(return_value=get_labels_response)

    # Act
    result = validation_helpers.check_if_get_labels_succeeds(mock_afd_client, unit_test_utils.FAKE_NAME)

    # Assert
    assert len(result) == 2
    assert result[0] is True
    assert result[1] is get_labels_response


def test_check_if_get_entity_types_succeeds_client_error_returns_false():
    # Arrange
    mock_afd_client = unit_test_utils.create_mock_afd_client()
    mock_afd_client.get_entity_types = MagicMock()
    mock_afd_client.exceptions.ResourceNotFoundException = ClientError
    # We retry NotFound (for consistency), so return not found twice
    mock_afd_client.get_entity_types.side_effect = [
        ClientError({"Code": "", "Message": ""}, "get_entity_types"),
        ClientError({"Code": "", "Message": ""}, "get_entity_types"),
    ]

    # Act
    result = validation_helpers.check_if_get_entity_types_succeeds(mock_afd_client, unit_test_utils.FAKE_NAME)

    # Assert
    assert len(result) == 2
    assert result[0] is False
    assert result[1] is None


def test_check_if_get_entity_types_succeeds_client_success_returns_true_and_response():
    # Arrange
    get_entity_types_response = {"entity_types": [unit_test_utils.FAKE_ENTITY_TYPE]}

    mock_afd_client = unit_test_utils.create_mock_afd_client()
    mock_afd_client.get_entity_types = MagicMock(return_value=get_entity_types_response)

    # Act
    result = validation_helpers.check_if_get_entity_types_succeeds(mock_afd_client, unit_test_utils.FAKE_NAME)

    # Assert
    assert len(result) == 2
    assert result[0] is True
    assert result[1] is get_entity_types_response


def test_check_if_get_variables_succeeds_client_error_returns_false():
    # Arrange
    mock_afd_client = unit_test_utils.create_mock_afd_client()
    mock_afd_client.get_variables = MagicMock()
    mock_afd_client.exceptions.ResourceNotFoundException = ClientError
    # We retry NotFound (for consistency), so return not found twice
    mock_afd_client.get_variables.side_effect = [
        ClientError({"Code": "", "Message": ""}, "get_variables"),
        ClientError({"Code": "", "Message": ""}, "get_variables"),
    ]

    # Act
    result = validation_helpers.check_if_get_variables_succeeds(mock_afd_client, unit_test_utils.FAKE_NAME)

    # Assert
    assert len(result) == 2
    assert result[0] is False
    assert result[1] is None


def test_check_if_get_variables_succeeds_client_success_returns_true_and_response():
    # Arrange
    get_variables_response = {"variables": [unit_test_utils.FAKE_IP_VARIABLE]}

    mock_afd_client = unit_test_utils.create_mock_afd_client()
    mock_afd_client.get_variables = MagicMock(return_value=get_variables_response)

    # Act
    result = validation_helpers.check_if_get_variables_succeeds(mock_afd_client, unit_test_utils.FAKE_NAME)

    # Assert
    assert len(result) == 2
    assert result[0] is True
    assert result[1] is get_variables_response


def test_check_if_get_event_types_succeeds_client_error_returns_false():
    # Arrange
    mock_afd_client = unit_test_utils.create_mock_afd_client()
    mock_afd_client.get_event_types = MagicMock()
    mock_afd_client.exceptions.ResourceNotFoundException = ClientError
    # We retry NotFound (for consistency), so return not found twice
    mock_afd_client.get_event_types.side_effect = [
        ClientError({"Code": "", "Message": ""}, "get_event_types"),
        ClientError({"Code": "", "Message": ""}, "get_event_types"),
    ]

    # Act
    result = validation_helpers.check_if_get_event_types_succeeds(mock_afd_client, unit_test_utils.FAKE_NAME)

    # Assert
    assert len(result) == 2
    assert result[0] is False
    assert result[1] is None


def test_check_if_get_event_types_succeeds_client_success_returns_true_and_response():
    # Arrange
    get_event_types_response = {"event_types": [unit_test_utils.FAKE_EVENT_TYPE]}

    mock_afd_client = unit_test_utils.create_mock_afd_client()
    mock_afd_client.get_event_types = MagicMock(return_value=get_event_types_response)

    # Act
    result = validation_helpers.check_if_get_event_types_succeeds(mock_afd_client, unit_test_utils.FAKE_NAME)

    # Assert
    assert len(result) == 2
    assert result[0] is True
    assert result[1] is get_event_types_response
