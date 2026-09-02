import { Monitor, HardDrive, Camera, Smartphone, Wifi, Terminal, Shield, Key, Globe, Database, Mic, Music, FileText, Image, Video, AppWindow, Download, Upload, Lock, Unlock, Power, RefreshCw, Search, Eye, Mic2, List, Settings, HelpCircle, Zap, ShieldCheck, Network, Server, Cpu, MemoryStick, MessageSquare, Trash2, Smartphone as SmartphoneIcon, Wifi as WifiIcon, Bluetooth, Usb, Monitor as MonitorIcon, Camera as CameraIcon, Mic as MicIcon, Speaker, HardDrive as HardDriveIcon, Database as DatabaseIcon, FileText as FileTextIcon, Image as ImageIcon, Video as VideoIcon, Music as MusicIcon, AppWindow as AppWindowIcon, Download as DownloadIcon, Upload as UploadIcon, Lock as LockIcon, Unlock as UnlockIcon, Power as PowerIcon, RefreshCw as RefreshCwIcon, Search as SearchIcon, Eye as EyeIcon, Mic2 as Mic2Icon, List as ListIcon, Settings as SettingsIcon, HelpCircle as HelpCircleIcon, Zap as ZapIcon, ShieldCheck as ShieldCheckIcon, Network as NetworkIcon, Server as ServerIcon, Cpu as CpuIcon, MemoryStick as MemoryStickIcon, Clipboard, MapPin, Fingerprint, BarChart3, Battery, Volume2, Bell, Radio, Home, PauseCircle, BatteryCharging, ToggleLeft } from 'lucide-react'

export type FeatureCategory = 'device' | 'data' | 'media' | 'apps' | 'network' | 'exploit'

export interface Feature {
  id: string
  name: string
  description: string
  icon: keyof typeof icons
  category: FeatureCategory
}

export const icons = {
  Monitor, HardDrive, Camera, Smartphone, Wifi, Terminal, Shield, Key, Globe, Database, Mic, Music, FileText, Image, Video, AppWindow, Download, Upload, Lock, Unlock, Power, RefreshCw, Search, Eye, Mic2, List, Settings, HelpCircle, Zap, ShieldCheck, Network, Server, Cpu, MemoryStick, MessageSquare, Trash2, SmartphoneIcon, WifiIcon, Bluetooth, Usb, MonitorIcon, CameraIcon, MicIcon, Speaker, HardDriveIcon, DatabaseIcon, FileTextIcon, ImageIcon, VideoIcon, MusicIcon, AppWindowIcon, DownloadIcon, UploadIcon, LockIcon, UnlockIcon, PowerIcon, RefreshCwIcon, SearchIcon, EyeIcon, Mic2Icon, ListIcon, SettingsIcon, HelpCircleIcon, ZapIcon, ShieldCheckIcon, NetworkIcon, ServerIcon, CpuIcon, MemoryStickIcon, Clipboard, MapPin, Fingerprint, BarChart3, Battery, Volume2, Bell, Radio, Home, PauseCircle, BatteryCharging, ToggleLeft,
}

export const featureCategories = [
  { id: 'device', label: 'Device Control', icon: Smartphone, count: 0 },
  { id: 'data', label: 'Data Extraction', icon: Database, count: 0 },
  { id: 'media', label: 'Media & Streaming', icon: Camera, count: 0 },
  { id: 'apps', label: 'App Management', icon: AppWindow, count: 0 },
  { id: 'network', label: 'Network & Security', icon: Network, count: 0 },
  { id: 'exploit', label: 'Exploitation', icon: Zap, count: 0 },
]

export const features: Feature[] = [
  // Device Control
  { id: 'connect', name: 'Connect Device', description: 'Connect to a device remotely using ADB over Wi-Fi or USB', icon: 'Smartphone', category: 'device' },
  { id: 'list-devices', name: 'List Devices', description: 'Show all devices currently attached to ADB', icon: 'List', category: 'device' },
  { id: 'disconnect', name: 'Disconnect All', description: 'Disconnect every ADB session with one command', icon: 'Unlock', category: 'device' },
  { id: 'multi-device', name: 'Multi-Device Selection', description: 'Choose which device to use when several are connected', icon: 'Smartphone', category: 'device' },
  { id: 'stop-adb', name: 'Stop ADB Server', description: 'Stop the ADB server process', icon: 'Power', category: 'device' },
  { id: 'shell', name: 'Device Shell', description: 'Open an interactive shell on the connected device', icon: 'Terminal', category: 'device' },
  { id: 'keycodes', name: 'Send Keycodes', description: 'Send keycodes to control the device remotely', icon: 'Key', category: 'device' },
  { id: 'unlock', name: 'Unlock Device', description: 'Turn screen on, swipe up, and enter password when needed', icon: 'Unlock', category: 'device' },
  { id: 'lock', name: 'Lock Device', description: 'Lock the device screen instantly', icon: 'Lock', category: 'device' },
  { id: 'reboot', name: 'Restart/Reboot', description: 'Restart to System, Recovery, Bootloader, or Fastboot', icon: 'RefreshCw', category: 'device' },
  { id: 'poweroff', name: 'Power Off', description: 'Power off the target device remotely', icon: 'Power', category: 'device' },
  { id: 'screenshot', name: 'Screenshot', description: 'Take a screenshot and pull it to the computer automatically', icon: 'Monitor', category: 'device' },
  { id: 'screen-record', name: 'Screen Recording', description: 'Record screen for specified time and pull automatically', icon: 'Video', category: 'device' },
  { id: 'anon-capture', name: 'Anonymous Capture', description: 'Screenshot/record and remove file from device afterward', icon: 'Eye', category: 'device' },
  { id: 'mirror', name: 'Mirror & Control', description: 'Mirror screen and control target device via scrcpy', icon: 'Monitor', category: 'device' },
  { id: 'stay-on', name: 'Screen Stay-On', description: 'Set svc power stayon (USB, always, or off)', icon: 'Monitor', category: 'device' },
  { id: 'dev-settings', name: 'Developer Settings', description: 'Open system Developer options screen on device', icon: 'Settings', category: 'device' },
  { id: 'locale', name: 'Read Locale', description: 'Read locale and language settings from device', icon: 'Globe', category: 'device' },
  { id: 'battery', name: 'Battery Info', description: 'Read battery status and related details', icon: 'Cpu', category: 'device' },
  { id: 'device-info', name: 'Device Information', description: 'Read comprehensive device information', icon: 'Smartphone', category: 'device' },
  { id: 'clipboard', name: 'Clipboard Management', description: 'Read, set, or clear the device clipboard', icon: 'Clipboard', category: 'device' },
  { id: 'location', name: 'GPS / Location', description: "Retrieve the device's last-known GPS location (latitude, longitude, provider)", icon: 'MapPin', category: 'device' },
  { id: 'identifiers', name: 'IMEI / Identifiers', description: 'Read IMEI, Android ID, serial number, and other hardware/software identifiers', icon: 'Fingerprint', category: 'device' },
  { id: 'mock-battery', name: 'Mock Battery', description: 'Fake a battery level, simulate plugged or unplugged, or reset readings', icon: 'Battery', category: 'device' },
  { id: 'display-size', name: 'Set Resolution & Display Size', description: 'Set screen resolution (wm size) from 720p/1080p/2K/4K presets or custom WxH; set display density (wm density); toggle display scaling; and reset to defaults', icon: 'MonitorIcon', category: 'device' },
  { id: 'sound-display', name: 'Sound & Display', description: 'Set media volume, screen brightness, screen timeout, and Do Not Disturb mode', icon: 'Volume2', category: 'device' },
  { id: 'notifications', name: 'Notifications', description: 'Post a notification, expand or collapse the notification panel and quick settings', icon: 'Bell', category: 'device' },

  // Data Extraction
  { id: 'list-files', name: 'List Files', description: 'List all files and folders on the target device', icon: 'HardDrive', category: 'data' },
  { id: 'download', name: 'Download from Device', description: 'Download a file or folder from the target device', icon: 'Download', category: 'data' },
  { id: 'upload', name: 'Send to Device', description: 'Send a file or folder from computer to target device', icon: 'Upload', category: 'data' },
  { id: 'whatsapp', name: 'Copy WhatsApp Data', description: 'Copy all WhatsApp data to the computer', icon: 'MessageSquare', category: 'data' },
  { id: 'screenshots-data', name: 'Copy Screenshots', description: 'Copy all screenshots to the computer', icon: 'Image', category: 'data' },
  { id: 'camera-photos', name: 'Copy Camera Photos', description: 'Copy all camera photos to the computer', icon: 'Camera', category: 'data' },
  { id: 'dump-sms', name: 'Dump SMS', description: 'Export all SMS from the device to the computer', icon: 'FileText', category: 'data' },
  { id: 'dump-contacts', name: 'Dump Contacts', description: 'Export all contacts from the device to the computer', icon: 'List', category: 'data' },
  { id: 'dump-calls', name: 'Dump Call Logs', description: 'Export all call logs from the device to the computer', icon: 'FileText', category: 'data' },
  { id: 'logcat-snippet', name: 'Save Logcat Snippet', description: 'Capture slice of logcat output and save to file', icon: 'FileText', category: 'data' },
  { id: 'live-logcat', name: 'Live Logcat Stream', description: 'Stream logcat live from the device', icon: 'Terminal', category: 'data' },
  { id: 'network-snapshot', name: 'Network Snapshot', description: 'Show snapshot of network interfaces and connectivity', icon: 'Network', category: 'data' },
  { id: 'wifi-status', name: 'Wi-Fi Status Dump', description: 'Dump detailed Wi-Fi status from the device', icon: 'Wifi', category: 'data' },
  { id: 'wlan-ip', name: 'WLAN IP Info', description: 'Show WLAN IP addressing information', icon: 'Wifi', category: 'data' },
  { id: 'saved-wifi', name: 'Saved Wi-Fi Networks', description: 'List saved Wi-Fi networks known to the device', icon: 'Wifi', category: 'data' },
  { id: 'ping', name: 'Ping Connectivity', description: 'Run ping checks against a host to test connectivity', icon: 'Search', category: 'data' },

  // Media & Streaming
  { id: 'camera-live', name: 'Camera Live', description: 'Stream live video from front or back camera', icon: 'Camera', category: 'media' },
  { id: 'mic-record', name: 'Record Microphone', description: 'Record audio from the microphone', icon: 'Mic', category: 'media' },
  { id: 'mic-stream', name: 'Stream Microphone', description: 'Stream live microphone audio', icon: 'Mic2', category: 'media' },
  { id: 'device-audio-record', name: 'Record Device Audio', description: 'Record internal device audio', icon: 'Speaker', category: 'media' },
  { id: 'device-audio-stream', name: 'Stream Device Audio', description: 'Stream live device audio', icon: 'Speaker', category: 'media' },
  { id: 'play-audio', name: 'Play Audio', description: 'Play an audio file on the target device', icon: 'Music', category: 'media' },
  { id: 'play-video', name: 'Play Video', description: 'Play a video on the target device', icon: 'Video', category: 'media' },
  { id: 'display-photo', name: 'Display Photo', description: 'Show an image or photo on the target device', icon: 'Image', category: 'media' },
  { id: 'wallpaper', name: 'Set Wallpaper', description: 'Push an image to the device and open the system wallpaper picker', icon: 'Image', category: 'media' },
  { id: 'open-link', name: 'Open Link', description: 'Open a URL on the target device', icon: 'Globe', category: 'media' },
  { id: 'send-sms', name: 'Send SMS', description: 'Send SMS messages through the target device', icon: 'MessageSquare', category: 'media' },

  // App Management
  { id: 'run-app', name: 'Run App', description: 'Launch an application on the device', icon: 'AppWindow', category: 'apps' },
  { id: 'install-apk', name: 'Install APK', description: 'Install an APK from computer to target device', icon: 'Download', category: 'apps' },
  { id: 'install-split', name: 'Install Split APKs', description: 'Install apps shipped as multiple APK splits', icon: 'Download', category: 'apps' },
  { id: 'uninstall', name: 'Uninstall App', description: 'Remove an installed application', icon: 'Trash2', category: 'apps' },
  { id: 'list-apps', name: 'List Installed Apps', description: 'List all apps installed on the target device', icon: 'List', category: 'apps' },
  { id: 'extract-apk', name: 'Extract APK', description: 'Extract the APK from an installed app', icon: 'Upload', category: 'apps' },
  { id: 'force-stop', name: 'Force-Stop App', description: 'Force-stop a running application', icon: 'Power', category: 'apps' },
  { id: 'clear-data', name: 'Clear App Data', description: 'Clear storage/data for a chosen app', icon: 'Database', category: 'apps' },
  { id: 'restart-app', name: 'Restart App', description: 'Restart an application (force-stop then relaunch)', icon: 'RefreshCw', category: 'apps' },
  { id: 'permissions', name: 'Grant/Revoke Permissions', description: 'Grant or revoke a runtime permission for an app', icon: 'ShieldCheck', category: 'apps' },
  { id: 'usage-stats', name: 'App Usage Statistics', description: 'Show foreground app usage stats over 1 day / 7 days / all time', icon: 'BarChart3', category: 'apps' },
  { id: 'enable-disable-app', name: 'Enable / Disable App', description: 'Disable a system or user app, or re-enable it later', icon: 'ToggleLeft', category: 'apps' },
  { id: 'suspend-app', name: 'Suspend / Unsuspend App', description: 'Suspend an app (icon greyed out, no data usage) or unsuspend it', icon: 'PauseCircle', category: 'apps' },
  { id: 'battery-optimization', name: 'Ignore Battery Optimization', description: 'Whitelist an app from Doze battery optimization, or un-whitelist it', icon: 'BatteryCharging', category: 'apps' },
  { id: 'default-home', name: 'Set Default Home App', description: 'Change the default launcher/home app to any installed launcher package', icon: 'Home', category: 'apps' },

  // Network & Security
  { id: 'port-forward', name: 'TCP Port Forwarding', description: 'Forward TCP ports over ADB, including reverse forwarding', icon: 'Network', category: 'network' },
  { id: 'lan-scan', name: 'LAN Network Scan', description: 'Discover hosts on local network, probe ports 5555/5554', icon: 'Search', category: 'network' },
  { id: 'wifi-toggle', name: 'Wi-Fi Radio Toggle', description: 'Turn the Wi-Fi radio on or off', icon: 'Wifi', category: 'network' },
  { id: 'radio-toggles', name: 'Radio Toggles', description: 'Toggle mobile data, Bluetooth, NFC, and airplane mode', icon: 'Radio', category: 'network' },
  { id: 'nearby-wifi', name: 'Nearby Wi-Fi Scan', description: 'Scan and list nearby Wi-Fi networks with SSID, BSSID, frequency, and signal', icon: 'Wifi', category: 'network' },
  { id: 'local-hotspot', name: 'Local Hotspot', description: 'Start a local-only Wi-Fi hotspot directly from the device', icon: 'Wifi', category: 'network' },
  { id: 'wireless-adb', name: 'Wireless ADB', description: 'Pair, connect, switch to TCP/IP, or switch back to USB — all wireless ADB commands', icon: 'Bluetooth', category: 'network' },
  { id: 'root-check', name: 'Root Heuristics', description: 'Heuristic checks for common signs of root access', icon: 'Shield', category: 'network' },

  // Exploitation
  { id: 'hack-device', name: 'Hack Device Completely', description: 'Automated Metasploit flow: create payload, install, run, get Meterpreter session', icon: 'Zap', category: 'exploit' },
  { id: 'metasploit', name: 'Metasploit Integration', description: 'Full Metasploit-Framework integration with msfvenom and msfconsole', icon: 'Server', category: 'exploit' },
]

// Update counts
featureCategories.forEach(cat => {
  cat.count = features.filter(f => f.category === cat.id).length
})