from ...helpers import (
    common_helpers,
    model_helpers,  # for monkeypatch
    validation_helpers  # for monkeypatch
)
from ...models import ResourceModel  # for monkeypatch
from cloudformation_cli_python_lib import (
    ProgressEvent,
    OperationStatus,
)
from unittest.mock import MagicMock
from .. import unit_test_utils


def test_create_variable_and_return_progress_success():
    # Arrange
    mock_afd_client, input_model, output_model, progress = _setup_create_variable_test()

    # Act/Assert
    _act_and_assert_create_variable_for_given_model(mock_afd_client, input_model, output_model, progress)


def test_create_variable_and_return_progress_no_tags_attribute_success():
    # Arrange
    mock_afd_client, input_model, output_model, progress = _setup_create_variable_test()
    del input_model.Tags
    mock_afd_client.list_tags_for_resource = MagicMock(return_value={'tags': []})
    output_model.Tags = []
    progress = unit_test_utils.create_in_progress_progress(input_model)

    # Act/Assert
    _act_and_assert_create_variable_for_given_model(mock_afd_client, input_model, output_model, progress)


def test_update_tags():
    # Arrange
    list_tags_response = {'tags': unit_test_utils.FAKE_TAGS}
    fake_tag_keys = [tag.get('key', '') for tag in unit_test_utils.FAKE_TAGS]

    mock_afd_client = unit_test_utils.create_mock_afd_client()
    mock_afd_client.list_tags_for_resource = MagicMock(return_value=list_tags_response)
    mock_afd_client.tag_resource = MagicMock()
    mock_afd_client.untag_resource = MagicMock()

    # Act
    common_helpers.update_tags(mock_afd_client, unit_test_utils.FAKE_ARN, unit_test_utils.FAKE_TAG_MODELS_DIFFERENT)

    # Assert
    mock_afd_client.untag_resource.assert_called_once_with(resourceARN=unit_test_utils.FAKE_ARN, tagKeys=fake_tag_keys)
    mock_afd_client.tag_resource.assert_called_once_with(resourceARN=unit_test_utils.FAKE_ARN,
                                                         tags=unit_test_utils.FAKE_TAGS_DIFFERENT)


def test_update_tags_no_tag_difference_dont_call_apis():
    # Arrange
    list_tags_response = {'tags': unit_test_utils.FAKE_TAGS}

    mock_afd_client = unit_test_utils.create_mock_afd_client()
    mock_afd_client.list_tags_for_resource = MagicMock(return_value=list_tags_response)
    mock_afd_client.tag_resource = MagicMock()
    mock_afd_client.untag_resource = MagicMock()

    # Act
    common_helpers.update_tags(mock_afd_client, unit_test_utils.FAKE_ARN, unit_test_utils.FAKE_TAG_MODELS)

    # Assert
    mock_afd_client.untag_resource.assert_not_called()
    mock_afd_client.tag_resource.assert_not_called()


def _setup_create_variable_test():
    get_variables_response = {'variables': [unit_test_utils.FAKE_IP_VARIABLE]}
    list_tags_response = {'tags': unit_test_utils.FAKE_TAGS}

    mock_afd_client = unit_test_utils.create_mock_afd_client()
    mock_afd_client.create_variable = MagicMock()
    mock_afd_client.get_variables = MagicMock(return_value=get_variables_response)
    mock_afd_client.list_tags_for_resource = MagicMock(return_value=list_tags_response)

    model = unit_test_utils.create_fake_model()
    expected_model = unit_test_utils.create_fake_model(is_output_model=True)
    progress_event = unit_test_utils.create_in_progress_progress(model)
    return mock_afd_client, model, expected_model, progress_event


def _act_and_assert_create_variable_for_given_model(afd_client, input_model, output_model, progress):
    result: ProgressEvent = common_helpers.create_variable_and_return_progress(afd_client, input_model, progress)
    assert result.status == OperationStatus.SUCCESS
    assert result.resourceModel == output_model
