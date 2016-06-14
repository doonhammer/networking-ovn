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

import six

from neutron.agent.ovsdb.native.commands import BaseCommand
from neutron.agent.ovsdb.native import idlutils

from networking_ovn._i18n import _
from networking_ovn.common import utils

class AddLSwitchCommand(BaseCommand):
    def __init__(self, api, name, may_exist, **columns):
        super(AddLSwitchCommand, self).__init__(api)
        self.name = name
        self.columns = columns
        self.may_exist = may_exist

    def run_idl(self, txn):
        if self.may_exist:
            lswitch = idlutils.row_by_value(self.api.idl, 'Logical_Switch',
                                            'name', self.name, None)
            if lswitch:
                return
        row = txn.insert(self.api._tables['Logical_Switch'])
        row.name = self.name
        for col, val in self.columns.items():
            setattr(row, col, val)


class DelLSwitchCommand(BaseCommand):
    def __init__(self, api, name, if_exists):
        super(DelLSwitchCommand, self).__init__(api)
        self.name = name
        self.if_exists = if_exists

    def run_idl(self, txn):
        try:
            lswitch = idlutils.row_by_value(self.api.idl, 'Logical_Switch',
                                            'name', self.name)
        except idlutils.RowNotFound:
            if self.if_exists:
                return
            msg = _("Logical Switch %s does not exist") % self.name
            raise RuntimeError(msg)

        self.api._tables['Logical_Switch'].rows[lswitch.uuid].delete()


class LSwitchSetExternalIdCommand(BaseCommand):
    def __init__(self, api, name, field, value, if_exists):
        super(LSwitchSetExternalIdCommand, self).__init__(api)
        self.name = name
        self.field = field
        self.value = value
        self.if_exists = if_exists

    def run_idl(self, txn):
        try:
            lswitch = idlutils.row_by_value(self.api.idl, 'Logical_Switch',
                                            'name', self.name)

        except idlutils.RowNotFound:
            if self.if_exists:
                return
            msg = _("Logical Switch %s does not exist") % self.name
            raise RuntimeError(msg)

        lswitch.verify('external_ids')

        external_ids = getattr(lswitch, 'external_ids', {})
        external_ids[self.field] = self.value
        lswitch.external_ids = external_ids

class AddLPortChainCommand(BaseCommand):
    def __init__(self, api, name, may_exist, **columns):
        super(AddLPortChainCommand, self).__init__(api)
        self.name = name
        self.columns = columns
        self.may_exist = may_exist

    def run_idl(self, txn):
        if self.may_exist:
            lport_chain = idlutils.row_by_value(self.api.idl, 'Logical_Port_Chain',
                                            'name', self.name, None)
            if lport_chain:
                return
        row = txn.insert(self.api._tables['Logical_Port_Chain'])
        row.name = self.name
        for col, val in self.columns.items():
            setattr(row, col, val)


class DelLPortChainCommand(BaseCommand):
    def __init__(self, api, name, if_exists):
        super(DelLPortChainCommand, self).__init__(api)
        self.name = name
        self.if_exists = if_exists

    def run_idl(self, txn):
        try:
            lswitch = idlutils.row_by_value(self.api.idl, 'Logical_Port_Chain',
                                            'name', self.name)
        except idlutils.RowNotFound:
            if self.if_exists:
                return
            msg = _("Logical Port Chain %s does not exist") % self.name
            raise RuntimeError(msg)

        self.api._tables['Logical_Port_Chain'].rows[lport_chain.uuid].delete()

class SetLogicalPortChainCommand(BaseCommand):
    def __init__(self, api, lport_chain, if_exists, **columns):
        super(SetLogicalPortChainCommand, self).__init__(api)
        self.lport_chain = lport_chain
        self.columns = columns
        self.if_exists = if_exists

    def run_idl(self, txn):
        try:
            lport_chain = idlutils.row_by_value(self.api.idl, 'Logical_Port_Chain',
                                         'name', self.lport_chain)
        except idlutils.RowNotFound:
            if self.if_exists:
                return
            msg = _("Logical Port Chain %s does not exist") % self.lport_chain
            raise RuntimeError(msg)

        for col, val in self.columns.items():
            setattr(lport_chain, col, val)


class AddLogicalPortPairGroupCommand(BaseCommand):
    def __init__(self, api, lport_pair_group, lport_chain, may_exist, **columns):
        super(AddLogicalPortPairGroupCommand, self).__init__(api)
        self.lport_pair_group = lport_pair_group
        self.lport_chain = lport_chain
        self.may_exist = may_exist
        self.columns = columns

    def run_idl(self, txn):
        try:
            lport_chain = idlutils.row_by_value(self.api.idl, 'Logical_Port_Chain',
                                                'name', self.lport_chain)
            port_pair_groups = getattr(lport_chain, 'port_pair_groups', [])
        except idlutils.RowNotFound:
            msg = _("Logical Port Chain %s does not exist") % self.lport_chain
            raise RuntimeError(msg)
        if self.may_exist:
            port_pair_group = idlutils.row_by_value(self.api.idl,
                                         'Logical_Port_Pair_Group', 'name',
                                         self.lport_pair_group, None)
            if port_pair_group:
                return

        lport_chain.verify('port_pair_groups')

        port_pair_group = txn.insert(self.api._tables['Logical_Port_Pair_Group'])
        port_pair_group.name = self.lport_pair_group
        for col, val in self.columns.items():
            setattr(port_pair_group, col, val)
        # add the newly created port_pair to existing lswitch
        port_pair_groups.append(port_pair_group.uuid)
        setattr(lport_chain, 'port_pair_groups', port_pair_groups)

class SetLogicalPortPairGroupCommand(BaseCommand):
    def __init__(self, api, lport_pair_group, if_exists, **columns):
        super(SetLogicalPortPairGroupCommand, self).__init__(api)
        self.lport_pair_group = lport_pair_group
        self.columns = columns
        self.if_exists = if_exists

    def run_idl(self, txn):
        try:
            port_pair_group = idlutils.row_by_value(self.api.idl, 'Logical_Port_Pair_Group',
                                                    'name', self.lport_pair_group)
        except idlutils.RowNotFound:
            if self.if_exists:
                return
            msg = _("Logical Port Pair Group %s does not exist") % self.lport_pair_group
            raise RuntimeError(msg)

        for col, val in self.columns.items():
            setattr(port_pair_group, col, val)

class DelLogicalPortPairGroupCommand(BaseCommand):
    def __init__(self, api, lport_pair_group, lport_chain, if_exists):
        super(DelLogicalPortPairGroupCommand, self).__init__(api)
        self.lport_pair_group = lport_pair_group
        self.lport_chain = lport_chain
        self.if_exists = if_exists

    def run_idl(self, txn):
        try:
            lport_pair_group = idlutils.row_by_value(self.api.idl, 'Logical_Port_Pair_Group',
                                                     'name', self.lport_pair_group)
            lport_chain = idlutils.row_by_value(self.api.idl, 'Logical_Port_Chain',
                                            'name', self.lport_chain)
            port_pair_groups = getattr(lport_chain, 'port_pair_groups', [])
        except idlutils.RowNotFound:
            if self.if_exists:
                return
            msg = _("Port Pair Group %s does not exist") % self.lport_pair_group
            raise RuntimeError(msg)

        lswitch.verify('port_pair_groups')

        port_pair_groups.remove(lport_pair_group)
        setattr(lport_chain, 'port_pair_groups', port_pair_groups)
        self.api._tables['Logical_Port_Pair_Group'].rows[lport_pair_group.uuid].delete()

class AddLogicalPortCommand(BaseCommand):
    def __init__(self, api, lport, lswitch, may_exist, **columns):
        super(AddLogicalPortCommand, self).__init__(api)
        self.lport = lport
        self.lswitch = lswitch
        self.may_exist = may_exist
        self.columns = columns

    def run_idl(self, txn):
        try:
            lswitch = idlutils.row_by_value(self.api.idl, 'Logical_Switch',
                                            'name', self.lswitch)
            ports = getattr(lswitch, 'ports', [])
        except idlutils.RowNotFound:
            msg = _("Logical Switch %s does not exist") % self.lswitch
            raise RuntimeError(msg)
        if self.may_exist:
            port = idlutils.row_by_value(self.api.idl,
                                         'Logical_Port', 'name',
                                         self.lport, None)
            if port:
                return

        lswitch.verify('ports')

        port = txn.insert(self.api._tables['Logical_Port'])
        port.name = self.lport
        for col, val in self.columns.items():
            setattr(port, col, val)
        # add the newly created port to existing lswitch
        ports.append(port.uuid)
        setattr(lswitch, 'ports', ports)


class SetLogicalPortCommand(BaseCommand):
    def __init__(self, api, lport, if_exists, **columns):
        super(SetLogicalPortCommand, self).__init__(api)
        self.lport = lport
        self.columns = columns
        self.if_exists = if_exists

    def run_idl(self, txn):
        try:
            port = idlutils.row_by_value(self.api.idl, 'Logical_Port',
                                         'name', self.lport)
        except idlutils.RowNotFound:
            if self.if_exists:
                return
            msg = _("Logical Port %s does not exist") % self.lport
            raise RuntimeError(msg)

        for col, val in self.columns.items():
            setattr(port, col, val)


class DelLogicalPortCommand(BaseCommand):
    def __init__(self, api, lport, lswitch, if_exists):
        super(DelLogicalPortCommand, self).__init__(api)
        self.lport = lport
        self.lswitch = lswitch
        self.if_exists = if_exists

    def run_idl(self, txn):
        try:
            lport = idlutils.row_by_value(self.api.idl, 'Logical_Port',
                                          'name', self.lport)
            lswitch = idlutils.row_by_value(self.api.idl, 'Logical_Switch',
                                            'name', self.lswitch)
            ports = getattr(lswitch, 'ports', [])
        except idlutils.RowNotFound:
            if self.if_exists:
                return
            msg = _("Port %s does not exist") % self.lport
            raise RuntimeError(msg)

        lswitch.verify('ports')

        ports.remove(lport)
        setattr(lswitch, 'ports', ports)
        self.api._tables['Logical_Port'].rows[lport.uuid].delete()

class AddLogicalPortPairCommand(BaseCommand):
    def __init__(self, api, lport_pair, lswitch, may_exist, **columns):
        super(AddLogicalPortPairCommand, self).__init__(api)
        self.lport_pair = lport_pair
        self.lswitch = lswitch
        self.may_exist = may_exist
        self.columns = columns

    def run_idl(self, txn):
        try:
            lswitch = idlutils.row_by_value(self.api.idl, 'Logical_Switch',
                                            'name', self.lswitch)
            port_pairs = getattr(lswitch, 'port-pairs', [])
        except idlutils.RowNotFound:
            msg = _("Logical Switch %s does not exist") % self.lswitch
            raise RuntimeError(msg)
        if self.may_exist:
            port_pair = idlutils.row_by_value(self.api.idl,
                                         'Logical_Port_Pair', 'name',
                                         self.lport_pair, None)
            if port_pair:
                return

        lswitch.verify('port_pairs')

        port_pair = txn.insert(self.api._tables['Logical_Port_Pair'])
        port_pair.name = self.lport_pair
        for col, val in self.columns.items():
            setattr(port_pair, col, val)
        # add the newly created port_pair to existing lswitch
        port_pairs.append(port_pair.uuid)
        setattr(lswitch, 'port_pairs', port_pairs)

class SetLogicalPortPairCommand(BaseCommand):
    def __init__(self, api, lport_pair, if_exists, **columns):
        super(SetLogicalPortPairCommand, self).__init__(api)
        self.lport_pair = lport_pair
        self.columns = columns
        self.if_exists = if_exists

    def run_idl(self, txn):
        try:
            port_pair = idlutils.row_by_value(self.api.idl, 'Logical_Port_Pair',
                                              'name', self.lport_pair)
        except idlutils.RowNotFound:
            if self.if_exists:
                return
            msg = _("Logical Port Pair%s does not exist") % self.lport_pair
            raise RuntimeError(msg)

        for col, val in self.columns.items():
            setattr(port_pair, col, val)

class DelLogicalPortPairCommand(BaseCommand):
    def __init__(self, api, lport_pair, lswitch, if_exists):
        super(DelLogicalPortPairCommand, self).__init__(api)
        self.lport_pair = lport_pair
        self.lswitch = lswitch
        self.if_exists = if_exists

    def run_idl(self, txn):
        try:
            lport_pair = idlutils.row_by_value(self.api.idl, 'Logical_Port_Pair',
                                               'name', self.lport_pair)
            lswitch = idlutils.row_by_value(self.api.idl, 'Logical_Switch',
                                            'name', self.lswitch)
            port_pairs = getattr(lswitch, 'port_pairs', [])
        except idlutils.RowNotFound:
            if self.if_exists:
                return
            msg = _("Port Pair %s does not exist") % self.lport_pair
            raise RuntimeError(msg)

        lswitch.verify('port_pairs')

        port_pairs.remove(lport_pair)
        setattr(lswitch, 'port_pairs', port_pairs)
        self.api._tables['Logical_Port_Pair'].rows[lport_pair.uuid].delete()

class AddLogicalFlowClassifierCommand(BaseCommand):
    def __init__(self, api, lflow_classifier, lswitch, may_exist, **columns):
        super(AddLogicalFlowClassifierCommand, self).__init__(api)
        self.lflow_classifier = lflow_classifier
        self.lswitch = lswitch
        self.may_exist = may_exist
        self.columns = columns

    def run_idl(self, txn):
        try:
            lswitch = idlutils.row_by_value(self.api.idl, 'Logical_Switch',
                                            'name', self.lswitch)
            flow_classifiers = getattr(lswitch, 'flow-classifiers', [])
        except idlutils.RowNotFound:
            msg = _("Logical Switch %s does not exist") % self.lswitch
            raise RuntimeError(msg)
        if self.may_exist:
            flow_classifier = idlutils.row_by_value(self.api.idl,
                                         'Logical_Flow_Classifier', 'name',
                                         self.lflow_classifier, None)
            if flow_classifier:
                return
        lswitch.verify('flow_classifiers')

        flow_classifier = txn.insert(self.api._tables['Logical_Flow_Classifier'])
        flow_classifier.name = self.lflow_classifier
        for col, val in self.columns.items():
            setattr(flow_classifier, col, val)
        # add the newly created flow_classifier to existing lswitch
        flow_classifiers.append(flow_classifier.uuid)
        setattr(lswitch, 'flow_classifiers', flow_classifiers)

class SetLogicalFlowClassifierCommand(BaseCommand):
    def __init__(self, api, lflow_classifier, if_exists, **columns):
        super(SetLogicalFlowCLassifierCommand, self).__init__(api)
        self.lflow_classifier = lflow_classifier
        self.columns = columns
        self.if_exists = if_exists

    def run_idl(self, txn):
        try:
            flow_classifier = idlutils.row_by_value(self.api.idl, 'Logical_Flow_Classifier',
                                              'name', self.lflow_classifier)
        except idlutils.RowNotFound:
            if self.if_exists:
                return
            msg = _("Logical Flow Classifier %s does not exist") % self.lflow_classifier
            raise RuntimeError(msg)

        for col, val in self.columns.items():
            setattr(flow_classifier, col, val)

class DelLogicalFlowClassifierCommand(BaseCommand):
    def __init__(self, api, lflow_classifier, lswitch, if_exists):
        super(DelLogicalFlowClassifierCommand, self).__init__(api)
        self.lflow_classifier = lflow_classifier
        self.lswitch = lswitch
        self.if_exists = if_exists

    def run_idl(self, txn):
        try:
            lflow_classifier = idlutils.row_by_value(self.api.idl, 'Logical_Flow_Classifier',
                                                     'name', self.lflow_classifier)
            lswitch = idlutils.row_by_value(self.api.idl, 'Logical_Switch',
                                            'name', self.lswitch)
            flow_classifiers = getattr(lswitch, 'flow_classifiers', [])
        except idlutils.RowNotFound:
            if self.if_exists:
                return
            msg = _("Flow CLassifier %s does not exist") % self.lflow_classifier
            raise RuntimeError(msg)

        lswitch.verify('flow_classifiers')

        flow_classifiers.remove(lflow_classifier)
        setattr(lswitch, 'flow_classifiers', flow_classifiers)
        self.api._tables['Logical_Flow_Classifier'].rows[lflow_classifier.uuid].delete()

class AddLRouterCommand(BaseCommand):
    def __init__(self, api, name, may_exist, **columns):
        super(AddLRouterCommand, self).__init__(api)
        self.name = name
        self.columns = columns
        self.may_exist = may_exist

    def run_idl(self, txn):
        if self.may_exist:
            lrouter = idlutils.row_by_value(self.api.idl, 'Logical_Router',
                                            'name', self.name, None)
            if lrouter:
                return

        row = txn.insert(self.api._tables['Logical_Router'])
        row.name = self.name
        for col, val in self.columns.items():
            setattr(row, col, val)


class UpdateLRouterCommand(BaseCommand):
    def __init__(self, api, name, if_exists, **columns):
        super(UpdateLRouterCommand, self).__init__(api)
        self.name = name
        self.columns = columns
        self.if_exists = if_exists

    def run_idl(self, txn):
        try:
            lrouter = idlutils.row_by_value(self.api.idl, 'Logical_Router',
                                            'name', self.name, None)
        except idlutils.RowNotFound:
            if self.if_exists:
                return
            msg = _("Logical Router %s does not exist") % self.name
            raise RuntimeError(msg)

        if lrouter:
            for col, val in self.columns.items():
                setattr(lrouter, col, val)
            return


class DelLRouterCommand(BaseCommand):
    def __init__(self, api, name, if_exists):
        super(DelLRouterCommand, self).__init__(api)
        self.name = name
        self.if_exists = if_exists

    def run_idl(self, txn):
        try:
            lrouter = idlutils.row_by_value(self.api.idl, 'Logical_Router',
                                            'name', self.name)
        except idlutils.RowNotFound:
            if self.if_exists:
                return
            msg = _("Logical Router %s does not exist") % self.name
            raise RuntimeError(msg)

        self.api._tables['Logical_Router'].rows[lrouter.uuid].delete()


class AddLRouterPortCommand(BaseCommand):
    def __init__(self, api, name, lrouter, **columns):
        super(AddLRouterPortCommand, self).__init__(api)
        self.name = name
        self.lrouter = lrouter
        self.columns = columns

    def run_idl(self, txn):

        try:
            lrouter = idlutils.row_by_value(self.api.idl, 'Logical_Router',
                                            'name', self.lrouter)
        except idlutils.RowNotFound:
            msg = _("Logical Router %s does not exist") % self.lrouter
            raise RuntimeError(msg)
        try:
            idlutils.row_by_value(self.api.idl, 'Logical_Router_Port',
                                  'name', self.name)
            # TODO(chandrav) This might be a case of multiple prefixes
            # on the same port. yet to figure out if and how OVN needs
            # to cater to this case
        except idlutils.RowNotFound:
            lrouter_port = txn.insert(self.api._tables['Logical_Router_Port'])
            lrouter_port.name = self.name
            for col, val in self.columns.items():
                setattr(lrouter_port, col, val)
            lrouter.verify('ports')
            lrouter_ports = getattr(lrouter, 'ports', [])
            if lrouter_port not in lrouter_ports:
                lrouter_ports.append(lrouter_port)
                setattr(lrouter, 'ports', lrouter_ports)


class DelLRouterPortCommand(BaseCommand):
    def __init__(self, api, name, lrouter, if_exists):
        super(DelLRouterPortCommand, self).__init__(api)
        self.name = name
        self.lrouter = lrouter
        self.if_exists = if_exists

    def run_idl(self, txn):
        try:
            lrouter_port = idlutils.row_by_value(self.api.idl,
                                                 'Logical_Router_Port',
                                                 'name', self.name)
        except idlutils.RowNotFound:
            if self.if_exists:
                return
            msg = _("Logical Router Port %s does not exist") % self.name
            raise RuntimeError(msg)
        try:
            lrouter = idlutils.row_by_value(self.api.idl, 'Logical_Router',
                                            'name', self.lrouter)
        except idlutils.RowNotFound:
            msg = _("Logical Router %s does not exist") % self.lrouter
            raise RuntimeError(msg)

        lrouter.verify('ports')
        lrouter_ports = getattr(lrouter, 'ports', [])
        if (lrouter_port in lrouter_ports):
            lrouter_ports.remove(lrouter_port)
            setattr(lrouter, 'ports', lrouter_ports)


class SetLRouterPortInLPortCommand(BaseCommand):
    def __init__(self, api, lport, lrouter_port):
        super(SetLRouterPortInLPortCommand, self).__init__(api)
        self.lport = lport
        self.lrouter_port = lrouter_port

    def run_idl(self, txn):
        try:
            port = idlutils.row_by_value(self.api.idl, 'Logical_Port',
                                         'name', self.lport)
        except idlutils.RowNotFound:
            msg = _("Logical Port %s does not exist") % self.lport
            raise RuntimeError(msg)

        options = {'router-port': self.lrouter_port}
        setattr(port, 'options', options)
        setattr(port, 'type', 'router')


class AddACLCommand(BaseCommand):
    def __init__(self, api, lswitch, lport, **columns):
        super(AddACLCommand, self).__init__(api)
        self.lswitch = lswitch
        self.lport = lport
        self.columns = columns

    def run_idl(self, txn):
        try:
            lswitch = idlutils.row_by_value(self.api.idl, 'Logical_Switch',
                                            'name', self.lswitch)
        except idlutils.RowNotFound:
            msg = _("Logical Switch %s does not exist") % self.lswitch
            raise RuntimeError(msg)

        row = txn.insert(self.api._tables['ACL'])
        for col, val in self.columns.items():
            setattr(row, col, val)
        row.external_ids = {'neutron:lport': self.lport}
        lswitch.verify('acls')
        acls = getattr(lswitch, 'acls', [])
        acls.append(row.uuid)
        setattr(lswitch, 'acls', acls)


class DelACLCommand(BaseCommand):
    def __init__(self, api, lswitch, lport, if_exists):
        super(DelACLCommand, self).__init__(api)
        self.lswitch = lswitch
        self.lport = lport
        self.if_exists = if_exists

    def run_idl(self, txn):
        try:
            lswitch = idlutils.row_by_value(self.api.idl, 'Logical_Switch',
                                            'name', self.lswitch)
        except idlutils.RowNotFound:
            if self.if_exists:
                return
            msg = _("Logical Switch %s does not exist") % self.lswitch
            raise RuntimeError(msg)

        lswitch.verify('acls')

        acls_to_del = []
        acls = getattr(lswitch, 'acls', [])
        for acl in acls:
            ext_ids = getattr(acl, 'external_ids', {})
            if ext_ids.get('neutron:lport') == self.lport:
                acls_to_del.append(acl)
        for acl in acls_to_del:
            acls.remove(acl)
            acl.delete()
        setattr(lswitch, 'acls', acls)


class UpdateACLsCommand(BaseCommand):
    def __init__(self, api, lswitch_names, port_list, acl_new_values_dict,
                 need_compare=True, is_add_acl=True):
        """This command updates the acl list for the logical switches

        @param lswitch_names: List of Logical Switch Names
        @type lswitch_names: []
        @param port_list: Iterator of List of Ports
        @type port_list: []
        @param acl_new_values_dict: Dictionary of acls indexed by port id
        @type acl_new_values_dict: {}
        @need_compare: If acl_new_values_dict needs be compared with existing
                       acls.
        @type: Boolean.
        @is_add_acl: If updating is caused by acl adding action.
        @type: Boolean.

        """
        super(UpdateACLsCommand, self).__init__(api)
        self.lswitch_names = lswitch_names
        self.port_list = port_list
        self.acl_new_values_dict = acl_new_values_dict
        self.need_compare = need_compare
        self.is_add_acl = is_add_acl

    def _acl_list_sub(self, acl_list1, acl_list2):
        """Compute the elements in acl_list1 but not in acl_list2.

        If acl_list1 and acl_list2 were sets, the result of this routine
        could be thought of as acl_list1 - acl_list2. Note that acl_list1
        and acl_list2 cannot actually be sets as they contain dictionary
        items i.e. set([{'a':1}) doesn't work.
        """
        acl_diff = []
        for acl in acl_list1:
            if acl not in acl_list2:
                acl_diff.append(acl)
        return acl_diff

    def _compute_acl_differences(self, port_list, acl_old_values_dict,
                                 acl_new_values_dict, acl_obj_dict):
        """Compute the difference between the new and old sets of acls

        @param port_list: Iterator of a List of ports
        @type port_list: []
        @param acl_old_values_dict: Dictionary of old acl values indexed
                                    by port id
        @param acl_new_values_dict: Dictionary of new acl values indexed
                                    by port id
        @param acl_obj_dict: Dictionary of acl objects indexed by the acl
                             value in string format.
        @var acl_del_objs_dict: Dictionary of acl objects to be deleted
                                indexed by the lswitch.
        @var acl_add_values_dict: Dictionary of acl values to be added
                                  indexed by the lswitch.
        @return: (acl_del_objs_dict, acl_add_values_dict)
        @rtype: ({}, {})
        """

        acl_del_objs_dict = {}
        acl_add_values_dict = {}
        for port in port_list:
            lswitch_name = port['network_id']
            acls_old = acl_old_values_dict.get(port['id'], [])
            acls_new = acl_new_values_dict.get(port['id'], [])
            acls_del = self._acl_list_sub(acls_old, acls_new)
            acls_add = self._acl_list_sub(acls_new, acls_old)
            acl_del_objs = acl_del_objs_dict.setdefault(lswitch_name, [])
            for acl in acls_del:
                acl_del_objs.append(acl_obj_dict[str(acl)])
            acl_add_values = acl_add_values_dict.setdefault(lswitch_name, [])
            for acl in acls_add:
                # Remove lport and lswitch columns
                del acl['lswitch']
                del acl['lport']
                acl_add_values.append(acl)
        return acl_del_objs_dict, acl_add_values_dict

    def _delete_acls(self, lswitch_name, acls, acls_delete):
        for acl_delete in acls_delete:
            try:
                acls.remove(acl_delete)
            except ValueError:
                msg = _("Logical Switch %s missing acl") % lswitch_name
                raise RuntimeError(msg)
            acl_delete.delete()

    def _add_acls(self, txn, acls, acl_values):
        rows = []
        for acl_value in acl_values:
            row = txn.insert(self.api._tables['ACL'])
            for col, val in acl_value.items():
                setattr(row, col, val)
            rows.append(row)
        for row in rows:
            acls.append(row.uuid)

    def _get_update_data_without_compare(self):
        lswitch_ovsdb_dict = {}
        for switch_name in self.lswitch_names:
            switch_name = utils.ovn_name(switch_name)
            lswitch = idlutils.row_by_value(self.api.idl, 'Logical_Switch',
                                            'name', switch_name)
            lswitch_ovsdb_dict[switch_name] = lswitch
        if self.is_add_acl:
            acl_add_values_dict = {}
            for port in self.port_list:
                switch_name = utils.ovn_name(port['network_id'])
                if switch_name not in acl_add_values_dict:
                    acl_add_values_dict[switch_name] = []
                if port['id'] in self.acl_new_values_dict:
                    acl_add_values_dict[switch_name].append(
                        self.acl_new_values_dict[port['id']])
            acl_del_objs_dict = {}
        else:
            acl_add_values_dict = {}
            acl_del_objs_dict = {}
            del_acl_matches = []
            for acl_dict in self.acl_new_values_dict.values():
                del_acl_matches.append(acl_dict['match'])
            for switch_name, lswitch in six.iteritems(lswitch_ovsdb_dict):
                if switch_name not in acl_del_objs_dict:
                    acl_del_objs_dict[switch_name] = []
                lswitch.verify('acls')
                acls = getattr(lswitch, 'acls', [])
                for acl in acls:
                    if getattr(acl, 'match') in del_acl_matches:
                        acl_del_objs_dict[switch_name].append(acl)
        return lswitch_ovsdb_dict, acl_del_objs_dict, acl_add_values_dict

    def run_idl(self, txn):

        if self.need_compare:
            # Get all relevant ACLs in 1 shot
            acl_values_dict, acl_obj_dict, lswitch_ovsdb_dict = \
                self.api.get_acls_for_lswitches(self.lswitch_names)

            # Compute the difference between the new and old set of ACLs
            acl_del_objs_dict, acl_add_values_dict = \
                self._compute_acl_differences(
                    self.port_list, acl_values_dict,
                    self.acl_new_values_dict, acl_obj_dict)
        else:
            lswitch_ovsdb_dict, acl_del_objs_dict, acl_add_values_dict = \
                self._get_update_data_without_compare()

        for lswitch_name, lswitch in six.iteritems(lswitch_ovsdb_dict):
            lswitch.verify('acls')
            acls = getattr(lswitch, 'acls', [])

            # Delete ACLs
            acl_del_objs = acl_del_objs_dict.get(lswitch_name, [])
            if acl_del_objs:
                self._delete_acls(lswitch_name, acls, acl_del_objs)

            # Add new ACLs
            acl_add_values = acl_add_values_dict.get(lswitch_name, [])
            if acl_add_values:
                self._add_acls(txn, acls, acl_add_values)

            setattr(lswitch, 'acls', acls)


class AddStaticRouteCommand(BaseCommand):
    def __init__(self, api, lrouter, **columns):
        super(AddStaticRouteCommand, self).__init__(api)
        self.lrouter = lrouter
        self.columns = columns

    def run_idl(self, txn):
        try:
            lrouter = idlutils.row_by_value(self.api.idl, 'Logical_Router',
                                            'name', self.lrouter)
        except idlutils.RowNotFound:
            msg = _("Logical Router %s does not exist") % self.lrouter
            raise RuntimeError(msg)

        row = txn.insert(self.api._tables['Logical_Router_Static_Route'])
        for col, val in self.columns.items():
            setattr(row, col, val)
        lrouter.verify('static_routes')
        static_routes = getattr(lrouter, 'static_routes', [])
        static_routes.append(row.uuid)
        setattr(lrouter, 'static_routes', static_routes)


class DelStaticRouteCommand(BaseCommand):
    def __init__(self, api, lrouter, ip_prefix, nexthop, if_exists):
        super(DelStaticRouteCommand, self).__init__(api)
        self.lrouter = lrouter
        self.ip_prefix = ip_prefix
        self.nexthop = nexthop
        self.if_exists = if_exists

    def run_idl(self, txn):
        try:
            lrouter = idlutils.row_by_value(self.api.idl, 'Logical_Router',
                                            'name', self.lrouter)
        except idlutils.RowNotFound:
            if self.if_exists:
                return
            msg = _("Logical Router %s does not exist") % self.lrouter
            raise RuntimeError(msg)

        lrouter.verify('static_routes')

        static_routes = getattr(lrouter, 'static_routes', [])
        for route in static_routes:
            ip_prefix = getattr(route, 'ip_prefix', '')
            nexthop = getattr(route, 'nexthop', '')
            if self.ip_prefix == ip_prefix and self.nexthop == nexthop:
                static_routes.remove(route)
                route.delete()
                break
        setattr(lrouter, 'static_routes', static_routes)
