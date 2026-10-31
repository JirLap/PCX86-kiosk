"""Regression checks for MQTT push updates, camera callbacks and translations."""

import ast
import json
from pathlib import Path
from types import SimpleNamespace
import unittest

ROOT = Path(__file__).resolve().parents[1] / 'custom_components/pcx86_kiosk'


class FakeEntity:
    def async_write_ha_state(self):
        self.writes = getattr(self, 'writes', 0) + 1

    def async_on_remove(self, callback):
        self.remove = callback


def callback(function):
    function.in_event_loop = True
    return function


class PushUpdateTests(unittest.TestCase):
    def test_screen_switch_follows_screensaver_and_sends_mqtt_wake(self):
        tree = ast.parse((ROOT/'switch.py').read_text())
        cls = next(n for n in tree.body if isinstance(n,ast.ClassDef))
        state = {'availability':'online','monitor':'off','screensaver_active':True}
        sent = []
        async def send(hass, entry, command):
            sent.append(command)
        namespace = {'SwitchEntity':FakeEntity,'panel_state':lambda hass,entry:state,'async_send_command':send}
        exec(compile(ast.Module(body=[cls],type_ignores=[]),'switch.py','exec'),namespace)
        entry = SimpleNamespace(data={'device_id':'kiosk'})
        entity = namespace['PanelControlSwitch'](None,entry,'screen','Screen','monitor','wake','sleep','mdi:monitor')
        self.assertFalse(entity.is_on)
        with self.assertRaises(StopIteration):
            entity.async_turn_on().send(None)
        self.assertEqual(sent,['wake'])
        state.update(monitor='on',screensaver_active=False)
        self.assertTrue(entity.is_on)

    def test_sleep_and_wake_use_mqtt_and_preserve_entity_ids_without_mac(self):
        tree = ast.parse((ROOT/'button.py').read_text())
        classes = [n for n in tree.body if isinstance(n,ast.ClassDef)]
        sent = []
        async def send(hass, entry, command):
            sent.append(command)
        namespace = {'ButtonEntity':FakeEntity, 'panel_state':lambda hass, entry:{'availability':'online'},
                     'async_send_command':send}
        exec(compile(ast.Module(body=classes,type_ignores=[]),'button.py','exec'),namespace)
        entry = SimpleNamespace(data={'device_id':'kiosk'},entry_id='entry')
        sleep = namespace['PanelCommandButton'](None,entry,'sleep','Sleep panel','mdi:sleep')
        wake = namespace['PanelWakeButton'](None,entry)
        self.assertEqual(sleep._attr_unique_id,'kiosk_suspend')
        self.assertEqual(wake._attr_unique_id,'kiosk_wake_system')
        self.assertTrue(wake.available)
        for entity in (sleep,wake):
            with self.assertRaises(StopIteration):
                entity.async_press().send(None)
        self.assertEqual(sent,['sleep','wake'])

    def test_command_buttons_follow_online_offline_messages(self):
        state = {}
        listeners = []
        def connect(hass, signal, listener):
            listeners.append((signal, listener))
            return lambda: listeners.clear()

        tree = ast.parse((ROOT / 'button.py').read_text())
        cls = next(n for n in tree.body if isinstance(n, ast.ClassDef) and n.name == 'PanelCommandButton')
        namespace = {
            'ButtonEntity': FakeEntity, 'panel_state': lambda hass, entry: state,
            'SIGNAL_STATUS': 'pcx86_kiosk_status_{}', 'async_dispatcher_connect': connect,
        }
        exec(compile(ast.Module(body=[cls], type_ignores=[]), 'button.py', 'exec'), namespace)
        entry = SimpleNamespace(entry_id='entry', data={'device_id':'kiosk'})
        entity = namespace['PanelCommandButton'](None, entry, 'status', 'Refresh status', 'mdi:refresh')
        self.assertFalse(entity.available)
        # The hook registers a synchronous dispatcher subscription and never
        # suspends, so run it without creating a Windows I/O event loop.
        hook = entity.async_added_to_hass()
        with self.assertRaises(StopIteration):
            hook.send(None)
        self.assertEqual(listeners[0][0], 'pcx86_kiosk_status_entry')
        state['availability'] = 'online'
        listeners[0][1]()
        self.assertTrue(entity.available)
        self.assertEqual(entity.writes, 1)
        state['availability'] = 'offline'
        listeners[0][1]()
        self.assertFalse(entity.available)
        self.assertEqual(entity.writes, 2)
        entity.remove()
        self.assertEqual(listeners, [])

    def test_camera_dispatcher_callback_runs_in_event_loop(self):
        tree = ast.parse((ROOT / 'camera.py').read_text())
        cls = next(n for n in tree.body if isinstance(n, ast.ClassDef) and n.name == 'PanelCamera')
        method = next(n for n in cls.body if isinstance(n, ast.FunctionDef) and n.name == '_status_updated')
        namespace = {'callback':callback}
        exec(compile(ast.Module(body=[method], type_ignores=[]), 'camera.py', 'exec'), namespace)
        receiver = FakeEntity()
        handler = namespace['_status_updated']
        self.assertTrue(handler.in_event_loop)
        handler(receiver)
        self.assertEqual(receiver.writes, 1)


class TranslationTests(unittest.TestCase):
    def test_languages_cover_same_keys_and_placeholders(self):
        en = json.loads((ROOT/'translations/en.json').read_text(encoding='utf-8'))
        cs = json.loads((ROOT/'translations/cs.json').read_text(encoding='utf-8'))
        def keys(data, prefix=''):
            return {prefix+k for k,v in data.items() if not isinstance(v,dict)} | set().union(*(keys(v,prefix+k+'.') for k,v in data.items() if isinstance(v,dict)))
        self.assertEqual(keys(en), keys(cs))
        self.assertEqual(en, json.loads((ROOT/'strings.json').read_text(encoding='utf-8')))
        self.assertEqual(cs['config']['step']['confirm']['data']['area_id'], 'Oblast')
        self.assertIn('{name}', cs['config']['step']['confirm']['title'])

    def test_all_entity_translation_keys_exist(self):
        en = json.loads((ROOT/'translations/en.json').read_text(encoding='utf-8'))['entity']
        for domain in en:
            tree = ast.parse((ROOT/f'{domain}.py').read_text(encoding='utf-8'))
            for node in ast.walk(tree):
                if isinstance(node, ast.Assign):
                    if any(isinstance(t, ast.Name) and t.id == '_attr_translation_key' for t in node.targets):
                        self.assertIn(ast.literal_eval(node.value), en[domain])
                if isinstance(node, ast.keyword) and node.arg == 'translation_key':
                    self.assertIn(ast.literal_eval(node.value), en[domain])
        self.assertEqual(len(en['sensor']), 24)
        self.assertEqual(len(en['button']), 9)


if __name__ == '__main__':
    unittest.main()
