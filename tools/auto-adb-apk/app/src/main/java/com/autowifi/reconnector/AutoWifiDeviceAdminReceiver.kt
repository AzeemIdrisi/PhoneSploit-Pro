package com.autowifi.reconnector

import android.app.admin.DeviceAdminReceiver
import android.content.Context
import android.content.Intent
import android.util.Log

class AutoWifiDeviceAdminReceiver : DeviceAdminReceiver() {
    override fun onEnabled(context: Context, intent: Intent) {
        super.onEnabled(context, intent)
        Log.d("AutoWifiDeviceAdmin", "Device admin enabled")
        WifiRestorer.ensureWifiEnabled(context)
    }
}
