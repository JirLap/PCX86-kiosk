"""Exercise registry updates without requiring a running Home Assistant instance.

Load the pure update helper in isolation. The strict registry signatures model
the HA API so unsupported keywords fail just as they do in Home Assistant.
"""

import ast
from pathlib import Path
from types import SimpleNamespace
import unittest


class Registry:
    def __init__(self, device):
        self.device = device
        self.lookup = None
        self.updated = None

    def async_get_device_by_identifier(self, identifier, config_entry_id):
        self.lookup = (identifier, config_entry_id)
        return self.device

    def async_update_device(
        self, device_id, *, new_connections=None, area_id=None,
        manufacturer=None, model=None, sw_version=None,
    ):
        self.updated = (device_id, new_connections, area_id, manufacturer, model, sw_version)


class DeviceRegistryUpdateTests(unittest.TestCase):
    def setUp(self):
        path = Path(__file__).resolve().parents[1] / 'custom_components/pcx86_kiosk/__init__.py'
        tree = ast.parse(path.read_text(encoding='utf-8'))
        function = next(node for node in tree.body if isinstance(node, ast.FunctionDef)
                        and node.name == '_async_update_device_registry')
        module = ast.Module(body=[ast.ImportFrom(module='__future__', names=[ast.alias(name='annotations')], level=0), function], type_ignores=[])
        self.registry = Registry(SimpleNamespace(id='device-1', connections={('mac', '00:00:00:00:00:01'), ('upnp', 'keep-me')}))
        namespace = {
            'dr': SimpleNamespace(async_get=lambda hass: self.registry, CONNECTION_NETWORK_MAC='mac'),
            'DOMAIN': 'pcx86_kiosk', 'CONF_DEVICE_ID': 'device_id',
            'CONF_MAC_ADDRESS': 'mac_address', 'CONF_AREA_ID': 'area_id',
        }
        exec(compile(ast.fix_missing_locations(module), str(path), 'exec'), namespace)
        self.update = namespace['_async_update_device_registry']
        self.entry = SimpleNamespace(entry_id='entry-1', data={'device_id': 'patro', 'area_id': 'hall'})

    def test_updates_mac_and_metadata_with_supported_keywords(self):
        self.update(None, self.entry, {'mac_address': 'AA:BB:CC:DD:EE:FF', 'manufacturer': 'Acer', 'model': 'Laptop', 'os_version': 'Debian 13'})
        self.assertEqual(self.registry.lookup, (('pcx86_kiosk', 'patro'), 'entry-1'))
        self.assertEqual(self.registry.updated, ('device-1', {('upnp', 'keep-me'), ('mac', 'aa:bb:cc:dd:ee:ff')}, 'hall', 'Acer', 'Laptop', 'Debian 13'))

    def test_offline_message_does_not_clear_mac(self):
        self.update(None, self.entry, {'availability': 'offline'})
        self.assertIsNone(self.registry.updated[1])

    def test_message_before_device_registration_is_safe(self):
        self.registry.device = None
        self.update(None, self.entry, {'mac_address': 'aa:bb:cc:dd:ee:ff'})
        self.assertIsNone(self.registry.updated)

    def test_legacy_lookup_is_supported(self):
        legacy = SimpleNamespace(async_get_device=lambda *, identifiers: self.registry.device,
                                 async_update_device=self.registry.async_update_device)
        self.update.__globals__['dr'].async_get = lambda hass: legacy
        self.update(None, self.entry, {'model': 'Laptop'})
        self.assertEqual(self.registry.updated[4], 'Laptop')


if __name__ == '__main__':
    unittest.main()
