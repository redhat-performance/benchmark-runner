"""
Unit tests for the OCP resource factory.

The OC client is not created: resource-name validation runs before any cluster
interaction, so these tests only exercise that guard.
"""
import os

import pytest

import benchmark_runner.common.ocp_resources.create_ocp_resource as create_ocp_resource_module
from benchmark_runner.common.ocp_resources.create_ocp_resource import CreateOCPResource
from benchmark_runner.common.ocp_resources.create_ocp_resource_exceptions import UnknownOCPResource

OCP_RESOURCES_PATH = os.path.dirname(os.path.realpath(create_ocp_resource_module.__file__))


def _create_ocp_resource():
    """Bypass __init__ so no OC client is created; only the resource path is set."""
    create_ocp_resource = object.__new__(CreateOCPResource)
    create_ocp_resource._CreateOCPResource__dir_path = OCP_RESOURCES_PATH
    return create_ocp_resource


def test_create_resource_rejects_unknown_resource():
    """
    A resource name with no matching directory must raise UnknownOCPResource
    rather than a bare FileNotFoundError from os.listdir.
    """
    with pytest.raises(UnknownOCPResource):
        _create_ocp_resource().create_resource(resource='not_a_resource', upgrade_version=None)


def test_unknown_resource_message_lists_supported_resources():
    """The error message should tell the user which resource names are valid."""
    with pytest.raises(UnknownOCPResource) as excinfo:
        _create_ocp_resource().create_resource(resource='not_a_resource', upgrade_version=None)

    message = str(excinfo.value)
    assert 'not_a_resource' in message
    for resource in ('cnv', 'lso', 'lvms', 'odf'):
        assert resource in message
    assert '__pycache__' not in message
