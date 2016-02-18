# Copyright 2016 PaloAltoNetworks
#
# Create Service Function Insertion extension for networking-ovn
#
# Created: 17th Feb 2016
# Author: John McDowall jmcdowall@paloaltonetworks.com
#
from neutron.api import extensions
from neutron import manager
from neutron.api.v2 import base

RESOURCE_ATTRIBUTE_MAP = {
    'sfi': {
    'name': {'allow_post': True, 'allow_put': True, 'is_visible': True},
    'priority': {'allow_post': True, 'allow_put': True, 'is_visible': True},
    'credential': {'allow_post': True, 'allow_put': True, 'is_visible': True},
    'tenant_id':  {'allow_post': True, 'allow_put': True, 
                   'required_by_policy': True,
                   'validate': {'type:string': None},
                   'is_visible': True},
    }
}

class Sfi(extensions.ExtensionDescriptor):
    #
    # Class to define the methods for service function insertion
    #
    @classmethod
    def get_name(cls):
        return "Service Function Insertion"
    
    @classmethod
    def get_alias(cls):
        return "sfi"

    @classmethod
    def get_description(cls):
        return "Simple Service Function Insertion mechanism for OVN"

    @classmethod
    def get_namespace(cls):
        # The XML namespace of the SFU extension
        return "http://paloaltonetworks.com/sfi"

    @classmethod
    def get_updated(cls):
        return "2016-02-16T10:00:00-00:00"

    @classmethod
    def get_resources(cls):
        #
        # Register the URL and dictionary with the Neutron Server
        #
        exts=list()
        plugin = manager.NeutronManager.get_plugin()
        resource_name = 'sfi'
        collection_name = resource_name + 's'
        params = RESOURCE_ATTRIBUTE_MAP.get(resource_name +'s', dict())
        controller = base.create_resource(collection_name, resource_name,
                                          plugin,params,allow_bulk=False)
        ex = extensions.ResourceExtension(collection_name, controller)
        exts.append(ex)

        return exts
