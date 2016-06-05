# Copyright 2016   All rights reserved.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.
import netaddr

# from eventlet import greenthread

from neutron.common import constants as nc_const
from neutron.common import rpc as n_rpc
from neutron import context as n_context
from neutron.db import api as db_api
from neutron import manager

from neutron.i18n import _LE
from neutron.i18n import _LW

from neutron.agent.ovsdb.native import idlutils
from neutron.plugins.common import constants as np_const

from oslo_log import helpers as log_helpers
from oslo_log import log as logging
from oslo_serialization import jsonutils

from networking_ovn.common import config
from networking_ovn.common import constants as ovn_const
from networking_ovn.common import utils
from networking_ovn.ovsdb import impl_idl_ovn

LOG = logging.getLogger(__name__)

def sfc_name(id):
    # The name of the OVN entry will be neutron-sfc-<UUID>
    # This is due to the fact that the OVN application checks if the name
    # is a UUID. If so then there will be no matches.
    # We prefix the UUID to enable us to use the Neutron UUID when
    # updating, deleting etc.
    return 'neutron-sfc-%s' % id
#
# Check logical switch exists for network port
#
def check_lswitch_exists(self, context, port_id):
    status = True
    core_plugin = manager.NeutronManager.get_plugin()
    #
    # Get network id belonging to port
    #
    port = core_plugin.get_port(context,port_id)
    #
    # Check network exists
    #
    lswitch_name = utils.ovn_name(port['network_id'])
    try:
        lswitch = idlutils.row_by_value(self._ovn.idl, 'Logical_Switch',
                                            'name', lswitch_name)
    except idlutils.RowNotFound:
        msg = _("Logical Switch %s does not exist got port_id %s") % (lswitch_name, port_id)
        LOG.error(msg)
        #raise RuntimeError(msg)
        status = False
    return status
#
# Interface into OVN - adds new rules to direct
# traffic to VNF port-pair
#
def create_ovn_sfc(self, context, sfc_instance):
    status = True
    #
    # Insert Flow Classifier into OVN
    # 
    flow_classifier = sfc_instance['flow_classifier']
    port_pair_groups = sfc_instance['port_pair_groups']
    with self._ovn.transaction(check_error=True) as txn:
        txn.add(self._ovn.create_lflow_classifier(
            lflow_classifier_name = sfc_name(flow_classifier['id']),
            lswitch_name = lswitch_name,
            logical_destination_port = flow_classifier['logical_destination_port'],
            logical_source_port = flow_classifier['logical_source_port'],
            source_port_range_min = flow_classifier['source_port_range_min'], 
            destination_ip_prefix = flow_classifier['destination_ip_prefix'],
            protocol= flow_classifier['protocol'],
            source_port_range_max = flow_classifier['source_port_range_max'], 
            ethertype = flow_classifier['ethertype'], 
            source_ip_prefix = flow_classifier['source_ip_prefix'], 
            destination_port_range_min = flow_classifier['destination_port_range_min'],
            destination_port_range_max =flow_classifier['destination_port_range_max']
        ))
        port_pairs_groups = []
        for group in port_pair_groups:
            port_pairs = group['port_pairs']
            lport_group_name = 'sfc-%s' % group['id']

            port_pair_group = []
            #
            # Insert Ports Pair into OVN
            #
            for port_pair in port_pairs:
                lport_pair_name = 'sfc-%s' % port_pair['id'],
                txn.add(self._ovn.create_lport_pair(
                    lport_pair_name = lport_pair_name,
                    lswitch_name = lswitch_name,
                    name  = port_pair['name'],
                    ingress = port_pair['ingress'],
                    egress = port_pair['egress']
                    ))
                port_pair_group.append(lport_pair_name)
            #
            # Insert Port Pair Group into OVN
            #
            txn.add(self.ovn_create_lport_group(
                lport_group_name = lport_group_name,
                lswitch_name = lswitch_name,
                port_pairs = port_pair_group    ,
                ))
            port_pair_groups.append(lport_group_name)
        #
        # Create Port Chain in OVN
        #
        txn.add(self.ovn.create_lport_pair_groups(
            lport_chain_name = 'sfc-%s' % sfc_instance['id']
            flow_classifier = flow_classifier
            port_pair_groups = poart_pair_groups
            ))
                
    return status
#
# Interface to delete entry in OVN nb-db for VNF port-pair
#
def delete_ovn_sfc(self,context, port_chain):
    status = False
    LOG.debug("delete ovn vnf %s" % port_chain)
    #
    # Get Network id of application port
    #
    fcs = self._get_portchain_fcs(port_chain)
    app_port =  fcs[0]['logical_source_port']
    #
    # Get the network id from the application por
    #
    # TODO: In cases where the VNF and Application are on seperate
    #       networks need to change logic - at minimum add an error
    #       handler that limits VNFs and Applications to same core.
    #
    core_plugin = manager.NeutronManager.get_plugin()
    port = core_plugin.get_port(self.admin_context, app_port)
    network_id = port['network_id']
    portchain_id = port_chain['id']
    with self._ovn.transaction(check_error=True) as txn:
        txn.add(self._ovn.delete_lservice(portchain_id,network_id))
        status = True
                
    return status
