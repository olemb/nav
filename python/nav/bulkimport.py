#
# Copyright (C) 2010 UNINETT
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
"""Import seed data in bulk."""

from nav.models.manage import Device, Netbox, Room, Organization
from nav.models.manage import Category, NetboxInfo, Subcategory
from nav.models.manage import Subcategory, NetboxCategory, Interface
from nav.models.manage import Location, Usage, NetboxType, Vendor
from nav.models.manage import Prefix, Vlan, NetType
from nav.models.cabling import Cabling, Patch

from nav.bulkparse import *

from nav.models.manage import models

class BulkImporter(object):
    def __init__(self, parser):
        self.parser = parser

    def __iter__(self):
        return self

    def next(self):
        try:
            row = self.parser.next()
            row = self.decode_as_utf8(row)
            objects = self.create_objects_from_row(row)
        except BulkParseError, error:
            objects = error
        return (self.parser.line_num, objects)

    def decode_as_utf8(self, row):
        for key, value in row.items():
            if isinstance(value, str):
                row[key] = value.decode('utf-8')
        return row

    def create_objects_from_row(self, row):
        raise Exception("Not Implemented")

class NetboxImporter(BulkImporter):
    def create_objects_from_row(self, row):
        raise_if_exists(Netbox, ip=row['ip'])
        raise_if_exists(Netbox, sysname=row['ip'])

        device = self.get_device_from_serial(row['serial'])
        netbox = self.get_netbox_from_row(row)
        netbox.device = device
        objects = [device, netbox]

        netboxinfo = self.get_netboxinfo_from_function(
            netbox, row['function'])
        if netboxinfo:
            objects.append(netboxinfo)

        subcats = self.get_subcats_from_subcat(netbox, row.get('subcat', []))
        if subcats:
            objects.extend(subcats)

        return objects

    def get_device_from_serial(self, serial):
        if not serial:
            return Device(serial=None)

        try:
            device = Device.objects.get(serial=serial)
        except Device.DoesNotExist, e:
            return Device(serial=serial)
        else:
            return device

    def get_netbox_from_row(self, row):
        netbox = Netbox(ip=row['ip'], read_only=row['ro'],
                        read_write=row['rw'], snmp_version=1)
        netbox.room = get_object_or_fail(Room, id=row['roomid'])
        netbox.organization = get_object_or_fail(Organization, id=row['orgid'])
        netbox.category = get_object_or_fail(Category, id=row['catid'])
        netbox.sysname = netbox.ip
        return netbox

    def get_netboxinfo_from_function(self, netbox, function):
        if function:
            return NetboxInfo(netbox=netbox, key=None, variable='function',
                              value=function)

    def get_subcats_from_subcat(self, netbox, subcat):
        if not subcat:
            return

        subcats = []
        for subcatid in [s for s in subcat if s]:
            subcategory = get_object_or_fail(Subcategory, id=subcatid,
                                             category__id=netbox.category_id)
            subcats.append(NetboxCategory(netbox=netbox, category=subcategory))
        return subcats

class LocationImporter(BulkImporter):
    def create_objects_from_row(self, row):
        raise_if_exists(Location, id=row['locationid'])
        location = Location(id=row['locationid'],
                            description=row['descr'])
        return [location]

class RoomImporter(BulkImporter):
    def create_objects_from_row(self, row):
        raise_if_exists(Room, id=row['roomid'])
        if row['locationid']:
            location = get_object_or_fail(Location, id=row['locationid'])
        else:
            location = None
        room = Room(id=row['roomid'], location=location,
                    description=row['descr'], optional_1=row['opt1'],
                    optional_2=row['opt2'], optional_3=row['opt3'],
                    optional_4=row['opt4'])
        return [room]

class OrgImporter(BulkImporter):
    def create_objects_from_row(self, row):
        raise_if_exists(Organization, id=row['orgid'])
        if row['parent']:
            parent = get_object_or_fail(Organization, id=row['parent'])
        else:
            parent = None
        org = Organization(id=row['orgid'], parent=parent,
                           description=row['description'],
                           optional_1=row['opt1'], optional_2=row['opt2'],
                           optional_3=row['opt3'])
        return [org]

class PrefixImporter(BulkImporter):
    def create_objects_from_row(self, row):
        raise_if_exists(Prefix, net_address=row['netaddr'])
        net_type = get_object_or_fail(NetType, id=row['nettype'])

        org = None
        if row['orgid']:
            org = get_object_or_fail(Organization, id=row['orgid'])

        usage = None
        if row['usage']:
            usage = get_object_or_fail(Usage, id=row['usage'])

        vlan, created = Vlan.objects.get_or_create(
            vlan=int(row['vlan']),
            net_type=net_type,
            organization=org,
            net_ident=row['netident'],
            usage=usage,
            description=row['description'])
        prefix = Prefix(net_address=row['netaddr'], vlan=vlan)
        return [vlan, prefix]

class UsageImporter(BulkImporter):
    def create_objects_from_row(self, row):
        raise_if_exists(Usage, id=row['usageid'])
        usage = Usage(id=row['usageid'], description=row['descr'])
        return [usage]

class NetboxTypeImporter(BulkImporter):
    def create_objects_from_row(self, row):
        vendor = get_object_or_fail(Vendor, id=row['vendorid'])
        raise_if_exists(NetboxType, sysobjectid=row['sysobjectid'])
        raise_if_exists(NetboxType, vendor=vendor, name=row['typename'])

        netbox_type = NetboxType(vendor=vendor, name=row['typename'],
                                 sysobjectid=row['sysobjectid'],
                                 description=row['description'],
                                 cdp=row['cdp'], tftp=row['tftp'])
        return [netbox_type]

class VendorImporter(BulkImporter):
    def create_objects_from_row(self, row):
        raise_if_exists(Vendor, id=row['vendorid'])
        vendor = Vendor(id=row['vendorid'])
        return [vendor]

class SubcatImporter(BulkImporter):
    def create_objects_from_row(self, row):
        raise_if_exists(Subcategory, id=row['subcatid'])
        cat = get_object_or_fail(Category, id=row['catid'])
        subcat = Subcategory(id=row['subcatid'], category=cat,
                             description=row['description'])
        return [subcat]

class CablingImporter(BulkImporter):
    def create_objects_from_row(self, row):
        room = get_object_or_fail(Room, id=row['roomid'])
        raise_if_exists(Cabling, room=room, jack=row['jack'])
        cabling = Cabling(room=room, jack=row['jack'],
                          building=row['building'],
                          target_room=row['targetroom'],
                          category=row['category'],
                          description=row['descr'])
        return [cabling]

class PatchImporter(BulkImporter):
    def create_objects_from_row(self, row):
        netbox = get_object_or_fail(Netbox, sysname=row['sysname'])
        interface = get_object_or_fail(Interface, netbox=netbox, ifname=row['port'])
        room = get_object_or_fail(Room, id=row['roomid'])
        cabling = get_object_or_fail(Cabling, room=room, jack=row['jack'])

        if not row['split']:
            row['split'] = 'no'
        patch = Patch(interface=interface, cabling=cabling,
                      split=row['split'])
        return [patch]

def get_object_or_fail(cls, **kwargs):
    try:
        return cls.objects.get(**kwargs)
    except cls.DoesNotExist, e:
        raise DoesNotExist("%s does not exist: %r" %
                           (cls.__name__, kwargs))
    except cls.MultipleObjectsReturned, e:
        raise MultipleObjectsReturned("%s returned multiple: %r" %
                                       (cls.__name__, kwargs))

def raise_if_exists(cls, **kwargs):
    result = cls.objects.filter(**kwargs)
    if result.count() > 0:
        raise AlreadyExists("%s already exists: %r" %
                            (cls.__name__, kwargs))

class BulkImportError(BulkParseError):
    "Import failed."
    pass

class DoesNotExist(BulkImportError):
    "Object does not exist"
    pass

class MultipleObjectsReturned(BulkImportError):
    "Multiple objects returned"
    pass

class AlreadyExists(BulkImportError):
    "Object already exist in database"
    pass

def reset_object_foreignkeys(obj):
    """Re-sets foreign key objects on obj.

    This makes sure that the ID's of foreignkey objects are updated on obj
    before obj.save() is attempted.

    """
    foreign_fields = [field for field in obj._meta.fields
                      if isinstance(field, models.fields.related.ForeignKey)]
    for field in foreign_fields:
        value = getattr(obj, field.name)
        if value:
            setattr(obj, field.name, value)

