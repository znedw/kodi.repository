import os, sys
import xbmcaddon, xbmc
import xbmcvfs
from threading import Timer
from xbmcgui import Dialog, WindowXMLDialog
tr = xbmcaddon.Addon().getLocalizedString
setSetting = xbmcaddon.Addon().setSetting

import xml.etree.ElementTree as ET

userdata = xbmcvfs.translatePath('special://userdata/keymaps')
key_file = os.path.join(userdata, 'playspeed.xml')

def indent(elem, level=0):
    #xml pretty print as xml.etree not supporting
    i = "\n" + level * "  "
    j = "\n" + (level - 1) * "  "
    if len(elem):
        if not elem.text or not elem.text.strip():
            elem.text = i + "  "
        if not elem.tail or not elem.tail.strip():
            elem.tail = i
        for subelem in elem:
            indent(subelem, level + 1)
        if not elem.tail or not elem.tail.strip():
            elem.tail = j
    else:
        if level and (not elem.tail or not elem.tail.strip()):
            elem.tail = j
    return elem


def Debug(msg):
    xbmc.log(f"#####[DefaultPlaybackSpeed]##### {msg}", xbmc.LOGDEBUG)


def setup_keymap_folder():
    if not os.path.exists(userdata):
        os.makedirs(userdata)

def _backup_file():

    fpathbak = f'{key_file}.bak'
    if xbmcvfs.exists(fpathbak):
        xbmcvfs.delete(fpathbak)
    return xbmcvfs.copy(key_file, fpathbak)

def main():

    key_set = sys.argv[-1]
    if key_set == 'up':
        command = 'PlayerControl(tempoup)'
    elif key_set == 'down':
        command = 'PlayerControl(tempodown)'
    elif key_set == 'default':
        setSetting('customkeyup', 'alt + RIGHT')
        setSetting('customkeydown', 'alt + LEFT')
        if xbmcvfs.exists(key_file):
            return xbmcvfs.delete(key_file)
        return

        ## load mappings ##
    try:
        setup_keymap_folder()
    except Exception as e:
        Debug(repr(e))
        return

    if os.path.exists(key_file):
        try:
            key_xml = ET.parse(key_file)
            root = key_xml.getroot()
            try:
                tag = [t for t in root.findall(f'.//key') if t.text == command][0]
            except IndexError:
                # If only one key stored in keymap file
                tag_up = root.find('.//keyboard')
                tag = ET.SubElement(tag_up, 'key')
                tag.text = command

            #key interception
            key = KeyListener.record_key()
            tag.set('id', key)
            _backup_file()
        except Exception as e:
            Debug(repr(e))
            return
    else:
        #build up keymap xml file
        root = ET.Element('keymap')
        tag1 = ET.SubElement(root, 'fullscreenvideo')
        tag2 = ET.SubElement(tag1, 'keyboard')
        key_tag = ET.SubElement(tag2, 'key')
        key = KeyListener.record_key()
        key_tag.set('id', key)
        key_tag.text = command
    # save keymap xml file and settings for display
    setSetting(f'customkey{key_set}', key)
    key_new_xml = ET.ElementTree(indent(root))
    key_new_xml.write(key_file, encoding='utf-8')


class KeyListener(WindowXMLDialog):
    TIMEOUT = 5

    def __new__(cls):
        gui_api = tuple(map(int, xbmcaddon.Addon(
            'xbmc.gui').getAddonInfo('version').split('.')))
        file_name = "DialogNotification.xml" if gui_api >= (
            5, 11, 0) else "DialogKaiToast.xml"
        return super(KeyListener, cls).__new__(cls, file_name, "")

    def __init__(self):
        """Initialize key variable."""
        self.key = str(None)

    def onInit(self):
        try:
            self.getControl(401).addLabel(tr(32111))
            self.getControl(402).addLabel(tr(32112) % self.TIMEOUT)
        except AttributeError:
            self.getControl(401).setLabel(tr(32111))
            self.getControl(402).setLabel(tr(32112) % self.TIMEOUT)

    def onAction(self, action):
        code = action.getButtonCode()
        self.key = str(None) if code == 0 else str(code)
        self.close()

    @staticmethod
    def record_key():
        dialog = KeyListener()
        timeout = Timer(KeyListener.TIMEOUT, dialog.close)
        timeout.start()
        dialog.doModal()
        timeout.cancel()
        key = dialog.key
        del dialog
        return key

