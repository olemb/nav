#
# Copyright (C) 2009-2013 UNINETT AS
#
# This file is part of Network Administration Visualized (NAV).
#
# NAV is free software: you can redistribute it and/or modify it under
# the terms of the GNU General Public License version 2 as published by
# the Free Software Foundation.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
# FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for
# more details.  You should have received a copy of the GNU General Public
# License along with NAV. If not, see <http://www.gnu.org/licenses/>.
#
"""Machine tracker forms"""
from datetime import date, timedelta

from nav.macaddress import MacPrefix
from nav.web.machinetracker import iprange
from django import forms


class MachineTrackerForm(forms.Form):
    """General fields for forms in machinetracker"""
    dns = forms.BooleanField(required=False, initial=False,
                             help_text="Show dns (if any)")
    days = forms.IntegerField(initial=7,
                              widget=forms.TextInput(attrs={'size': 3}),
                              help_text="Days back in time to search")

    def clean_days(self):
        data = self.cleaned_data['days']
        try:
            date.today() - timedelta(days=int(data))
        except OverflowError:
            raise forms.ValidationError(
                "They didn't have computers %s days ago" % data)
        return int(data)


class IpTrackerForm(MachineTrackerForm):
    # IPAddressField only supports IPv4 as of Django 1.1
    choices = [('active', 'Active'), ('inactive', 'Inactive'),
               ('both', 'Both')]

    ip_range = forms.CharField(widget=forms.TextInput(
        attrs={'placeholder': 'IP-address or range'})
    )
    period_filter = forms.ChoiceField(widget=forms.RadioSelect(),
                                      choices=choices,
                                      initial='active')
    netbios = forms.BooleanField(required=False, initial=False,
                                 help_text="Show netbios name (if any)")

    def clean_ip_range(self):
        data = self.cleaned_data['ip_range']
        try:
            data = iprange.MachinetrackerIPRange.from_string(data)
        except ValueError as error:
            raise forms.ValidationError("Invalid syntax: %s" % error)
        return data


class MacTrackerForm(MachineTrackerForm):
    mac = forms.CharField(widget=forms.TextInput(
        attrs={'placeholder': 'Mac-address'})
    )
    netbios = forms.BooleanField(required=False, initial=False,
                                 help_text="Netbios name (if any)")

    def clean_mac(self):
        try:
            mac = MacPrefix(self.cleaned_data['mac'])
        except ValueError as error:
            raise forms.ValidationError(error)
        return mac


class SwitchTrackerForm(forms.Form):
    switch = forms.CharField()
    module = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={'size': 3}))
    port = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={'size': 16}))
    days = forms.IntegerField(
        initial=7,
        widget=forms.TextInput(attrs={'size': 3}))


class NetbiosTrackerForm(MachineTrackerForm):
    search = forms.CharField(widget=forms.TextInput(
        attrs={'placeholder': 'Netbios name'}))

    def clean_search(self):
        """Make sure blank spaces and such is removed from search"""
        return self.cleaned_data['search'].strip()
