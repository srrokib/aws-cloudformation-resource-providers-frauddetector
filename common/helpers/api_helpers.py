from typing import List
from . import validation_helpers

import functools
import logging
import time

# Use this logger to forward log messages to CloudWatch Logs.
LOG = logging.getLogger(__name__)
LOG.setLevel(level=logging.DEBUG)

# Maximum number of pages to get for paginated calls
# for page size of 100, 100 pages is 10,000 resources, which is twice the largest default service limit
MAXIMUM_NUMBER_OF_PAGES = 100

# Number of seconds to wait for eventually consistency for `retry_not_found_exceptions` decorator
CONSISTENCY_SLEEP_TIME = 1.0


# Wrapper/decorator


def api_call_with_debug_logs(func):
    """
    Add some logs to the decorated function
    """

    @functools.wraps(func)
    def log_wrapper(*args, **kwargs):
        LOG.debug(f"Starting function {func.__name__!r} with args {args} and kwargs {kwargs}")
        value = func(*args, **kwargs)
        LOG.debug(f"Finished function {func.__name__!r}, returning {value}")
        return value

    return log_wrapper


def retry_not_found_exceptions(func):
    """
    Retries boto3 not found exception for the decorated function.
    """

    @functools.wraps(func)
    def retry_not_found_exceptions_wrapper(*args, **kwargs):
        afd_client = kwargs.get("frauddetector_client", None)
        if not afd_client:
            if len(args) > 0:
                afd_client = args[0]
            else:
                # We can't grab afd_client, so we can't compare to AFD's RNF Exception.
                # Just run the function, rather than throwing an error
                LOG.error(
                    "retry_not_found_exceptions_wrapper could not find the afd client! "
                    "Perhaps the decorator was added to a method that is not supported?"
                )
                return func(*args, **kwargs)
        try:
            return func(*args, **kwargs)
        except afd_client.exceptions.ResourceNotFoundException:
            LOG.warning(
                f"caught a resource not found exception."
                f" sleeping {CONSISTENCY_SLEEP_TIME} seconds and retrying api call for consistency..."
            )
            time.sleep(CONSISTENCY_SLEEP_TIME)
            return func(*args, **kwargs)

    return retry_not_found_exceptions_wrapper


def paginated_api_call(
    item_to_collect,
    criteria_to_keep=lambda x, y: True,
    max_pages=MAXIMUM_NUMBER_OF_PAGES,
):
    """
    For a method that calls a paginated API (returns an object w/ 'nextToken' key),
    decorate with @paginated_api_call to get an exhaustive list returned,
    stopping at the maximum number of pages
    :param item_to_collect: string representing the key of the object that should be accumulated
    :param criteria_to_keep: function to determine if items should be kept - item_list, item -> bool
    :param max_pages: maximum number of pages allowed
    :return: an exhaustive list, containing the accumulated items from all pages from the API call
    """

    def paginated_api_call_decorator(func):
        @functools.wraps(func)
        def api_call_wrapper(*args, **kwargs):
            collected_items = []
            response = func(*args, **kwargs)

            def collect_items_of_interest_from_current_response():
                for item_of_interest in response.get(item_to_collect, []):
                    if criteria_to_keep(collected_items, item_of_interest):
                        collected_items.append(item_of_interest)

            collect_items_of_interest_from_current_response()
            count = 1

            while "nextToken" in response and count < max_pages:
                next_token = response["nextToken"]
                response = func(*args, nextToken=next_token, **kwargs)
                collect_items_of_interest_from_current_response()
                count += 1

            response[item_to_collect] = collected_items
            return response

        return api_call_wrapper

    return paginated_api_call_decorator


# Put APIs


@api_call_with_debug_logs
def call_put_outcome(
    frauddetector_client,
    outcome_name: str,
    outcome_tags: List[dict] = None,
    outcome_description: str = None,
):
    """
    Call put_outcome with the given frauddetector client and the given arguments.
    :param frauddetector_client: boto3 frauddetector client to use to make the call
    :param outcome_name: name of the outcome
    :param outcome_tags: tags to attach to the outcome (default is None)
    :param outcome_description: description of the outcome (default is None)
    :return: API response from frauddetector_client
    """
    args = {
        "name": outcome_name,
        "tags": outcome_tags,
        "description": outcome_description,
    }
    args = validation_helpers.remove_none_arguments(args)
    return frauddetector_client.put_outcome(**args)


@api_call_with_debug_logs
def call_put_detector(
    frauddetector_client,
    detector_id: str,
    detector_event_type_name: str,
    detector_tags: List[dict] = None,
    detector_description: str = None,
):
    """
    This method calls put_detector with the given client and the given arguments.
    :param frauddetector_client: afd client to use to make the call
    :param detector_id: id of the detector
    :param detector_event_type_name: name for the associated event_type
    :param detector_tags: tags to attach to the detector (default is None)
    :param detector_description: description of the detector (default is None)
    :return: API response from frauddetector_client
    """
    args = {
        "detectorId": detector_id,
        "tags": detector_tags,
        "description": detector_description,
        "eventTypeName": detector_event_type_name,
    }
    args = validation_helpers.remove_none_arguments(args)
    return frauddetector_client.put_detector(**args)


@api_call_with_debug_logs
def call_put_label(
    frauddetector_client,
    label_name: str,
    label_tags: List[dict] = None,
    label_description: str = None,
):
    """
    This method calls put_label with the given client and the given arguments.
    :param frauddetector_client: afd client to use to make the call
    :param label_name: name of the label
    :param label_tags: tags to attach to the label (default is None)
    :param label_description: description of the label (default is None)
    :return: API response from frauddetector_client
    """
    args = {"name": label_name, "tags": label_tags, "description": label_description}
    args = validation_helpers.remove_none_arguments(args)
    return frauddetector_client.put_label(**args)


@api_call_with_debug_logs
def call_put_entity_type(
    frauddetector_client,
    entity_type_name: str,
    entity_type_tags: List[dict] = None,
    entity_type_description: str = None,
):
    """
    This method calls put_entity_type with the given client and the given arguments.
    :param frauddetector_client: afd client to use to make the call
    :param entity_type_name: name of the entity type
    :param entity_type_tags: tags to attach to the entity type (default is None)
    :param entity_type_description: description of the entity type (default is None)
    :return: API response from frauddetector_client
    """
    args = {
        "name": entity_type_name,
        "tags": entity_type_tags,
        "description": entity_type_description,
    }
    args = validation_helpers.remove_none_arguments(args)
    return frauddetector_client.put_entity_type(**args)


@api_call_with_debug_logs
def call_put_event_type(
    frauddetector_client,
    event_type_name: str,
    entity_type_names: List[str],
    event_variable_names: List[str],
    label_names: List[str] = None,
    event_type_tags: List[dict] = None,
    event_type_description: str = None,
):
    """
    This method calls put_event_type with the given client and the given arguments.
    :param frauddetector_client: afd client to use to make the call
    :param event_type_name: name of the event type
    :param entity_type_names: entity types to attach to the event type
    :param event_variable_names: event variables associated with the event type
    :param label_names: labels to associate with the event type
    :param event_type_tags: tags to attach to the event type (default is None)
    :param event_type_description: description of the event type (default is None)
    :return: API response from frauddetector_client
    """
    args = {
        "name": event_type_name,
        "tags": event_type_tags,
        "entityTypes": entity_type_names,
        "eventVariables": event_variable_names,
        "labels": label_names,
        "description": event_type_description,
    }
    validation_helpers.remove_none_arguments(args)
    return frauddetector_client.put_event_type(**args)


# Create APIs


@api_call_with_debug_logs
def call_create_variable(
    frauddetector_client,
    variable_name: str,
    variable_data_source: str,
    variable_data_type: str,
    variable_default_value: str,
    variable_description: str = None,
    variable_type: str = None,
    variable_tags: List[dict] = None,
):
    args = {
        "name": variable_name,
        "dataSource": variable_data_source,
        "dataType": variable_data_type,
        "defaultValue": variable_default_value,
        "description": variable_description,
        "variableType": variable_type,
        "tags": variable_tags,
    }
    validation_helpers.remove_none_arguments(args)
    return frauddetector_client.create_variable(**args)


@api_call_with_debug_logs
def call_batch_create_variable(
    frauddetector_client,
    variable_entries_to_create: List[dict],
    variable_tags: List[dict] = None,
):
    """
    Calls batch_create_variable using the provided frauddetector client.
    :param frauddetector_client: client to make the call with
    :param variable_entries_to_create: List[EventVariable] - list of EventVariable objects
    :param variable_tags: List[dict], list of tags to attach to the variables
    :return: API response from batch_create_variable
    """
    args = {"variableEntries": variable_entries_to_create, "tags": variable_tags}
    validation_helpers.remove_none_arguments(args)
    validation_helpers.check_variable_entries_are_valid(args)
    return frauddetector_client.batch_create_variable(**args)


# Update APIs
@retry_not_found_exceptions
@api_call_with_debug_logs
def call_update_variable(
    frauddetector_client,
    variable_name: str,
    variable_default_value: str,
    variable_description: str,
):
    """
    Calls update_variable with the given frauddetector client
    :param variable_description: new description for the variable
    :param variable_default_value: new default value for the variable
    :param variable_name: name of the variable
    :param frauddetector_client: boto3 client to make the call with
    :return: API response from update_variable
    """
    # Only update description, variable type, and default value
    args = {
        "defaultValue": variable_default_value,
        "description": variable_description,
        "name": variable_name,
    }
    validation_helpers.remove_none_arguments(args)
    return frauddetector_client.update_variable(**args)


# Get APIs


@retry_not_found_exceptions
@paginated_api_call(item_to_collect="outcomes")
@api_call_with_debug_logs
def call_get_outcomes(frauddetector_client, outcome_name: str = None):
    """
    Call get_outcomes with the given frauddetector client and the given arguments.
    :param frauddetector_client: boto3 frauddetector client to use to make the call
    :param outcome_name: name of the outcome to get (default is None)
    :return: get a single outcome if outcome_name is specified, otherwise get all outcomes
    """
    args = {"name": outcome_name}
    validation_helpers.remove_none_arguments(args)
    return frauddetector_client.get_outcomes(**args)


@retry_not_found_exceptions
@paginated_api_call(item_to_collect="variables")
@api_call_with_debug_logs
def call_get_variables(frauddetector_client, variable_name: str = None):
    """
    Call get_variables with the given frauddetector client and the given arguments.
    :param frauddetector_client: boto3 frauddetector client to use to make the call
    :param variable_name: name of the variable to get (default is None)
    :return: get a single variable if variable_name is specified, otherwise get all variables
    """
    args = {"name": variable_name}
    validation_helpers.remove_none_arguments(args)
    return frauddetector_client.get_variables(**args)


@retry_not_found_exceptions
@paginated_api_call(item_to_collect="detectors")
@api_call_with_debug_logs
def call_get_detectors(frauddetector_client, detector_id: str = None):
    args = {"detectorId": detector_id}
    validation_helpers.remove_none_arguments(args)
    return frauddetector_client.get_detectors(**args)


@retry_not_found_exceptions
@paginated_api_call(item_to_collect="labels")
@api_call_with_debug_logs
def call_get_labels(frauddetector_client, label_name: str = None):
    args = {"name": label_name}
    validation_helpers.remove_none_arguments(args)
    return frauddetector_client.get_labels(**args)


@retry_not_found_exceptions
@paginated_api_call(item_to_collect="entityTypes")
@api_call_with_debug_logs
def call_get_entity_types(frauddetector_client, entity_type_name: str = None):
    args = {"name": entity_type_name}
    validation_helpers.remove_none_arguments(args)
    return frauddetector_client.get_entity_types(**args)


@retry_not_found_exceptions
@paginated_api_call(item_to_collect="eventTypes")
@api_call_with_debug_logs
def call_get_event_types(frauddetector_client, event_type_name: str = None):
    args = {"name": event_type_name}
    validation_helpers.remove_none_arguments(args)
    return frauddetector_client.get_event_types(**args)


@api_call_with_debug_logs
def call_batch_get_variable(frauddetector_client, variable_names: List[str]):
    return frauddetector_client.batch_get_variable(names=variable_names)


# Delete APIs


@api_call_with_debug_logs
def call_delete_outcome(frauddetector_client, outcome_name: str):
    """
    Call delete_outcome for a given outcome name with the given frauddetector client.
    :param frauddetector_client: boto3 frauddetector client to use to make the call
    :param outcome_name: name of the outcome to delete
    :return: success will return a 200 with no body
    """
    return frauddetector_client.delete_outcome(name=outcome_name)


@api_call_with_debug_logs
def call_delete_detector(frauddetector_client, detector_id: str):
    return frauddetector_client.delete_detector(detectorId=detector_id)


@api_call_with_debug_logs
def call_delete_variable(frauddetector_client, variable_name: str):
    return frauddetector_client.delete_variable(name=variable_name)


@api_call_with_debug_logs
def call_delete_event_type(frauddetector_client, event_type_name: str):
    return frauddetector_client.delete_event_type(name=event_type_name)


@api_call_with_debug_logs
def call_delete_entity_type(frauddetector_client, entity_type_name: str):
    return frauddetector_client.delete_entity_type(name=entity_type_name)


@api_call_with_debug_logs
def call_delete_label(frauddetector_client, label_name: str):
    return frauddetector_client.delete_label(name=label_name)


# Tagging
@retry_not_found_exceptions
@paginated_api_call(item_to_collect="tags")
@api_call_with_debug_logs
def call_list_tags_for_resource(frauddetector_client, resource_arn: str):
    """
    Call list_tags_for_resource for a given ARN with the given frauddetector client.
    :param frauddetector_client: boto3 frauddetector client to use to make the call
    :param resource_arn: ARN of the resource to get tags for
    :return: result has an exhaustive list of tags attached to the resource
    """
    return frauddetector_client.list_tags_for_resource(resourceARN=resource_arn)


@retry_not_found_exceptions
@api_call_with_debug_logs
def call_tag_resource(frauddetector_client, resource_arn: str, tags: List[dict]):
    """
    Call tag_resource with the given frauddetector client and parameters.
    :param frauddetector_client: boto3 frauddetector client to use to make the call
    :param resource_arn: ARN of the resource to attach tags to
    :param tags: tags to attach to the resource, as a list of dicts [{'key': '...', 'value': '...'}]
    :return: success will return a 200 with no body
    """
    return frauddetector_client.tag_resource(resourceARN=resource_arn, tags=tags)


@retry_not_found_exceptions
@api_call_with_debug_logs
def call_untag_resource(frauddetector_client, resource_arn: str, tag_keys: List[str]):
    """
    Call untag_resource with the given frauddetector client and parameters.
    :param frauddetector_client: boto3 frauddetector client to use to make the call
    :param resource_arn: ARN of the resource to remove tags from
    :param tag_keys: tags to attach to the resource, as a list of str ['key1', 'key2']
    :return: success will return a 200 with no body
    """
    return frauddetector_client.untag_resource(resourceARN=resource_arn, tagKeys=tag_keys)
