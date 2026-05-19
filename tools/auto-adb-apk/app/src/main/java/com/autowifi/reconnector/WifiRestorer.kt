package com.autowifi.reconnector

import android.app.admin.DevicePolicyManager
import android.content.Context
import android.net.wifi.WifiManager
import android.util.Log

object WifiRestorer {
    private const val TAG = "WifiRestorer"

    fun ensureWifiEnabled(context: Context): Boolean {
        val appContext = context.applicationContext
        val wifiManager = appContext.getSystemService(Context.WIFI_SERVICE) as WifiManager

        if (wifiManager.isWifiEnabled) {
            Log.d(TAG, "Wi-Fi is already enabled")
            return true
        }

        if (hasDeviceOwnerPrivilege(appContext)) {
            return enableWifi(wifiManager)
        }

        if (ShizukuWifiEnabler.hasPermission()) {
            return ShizukuWifiEnabler.enableWifi(appContext)
        }

        Log.w(TAG, "Cannot enable Wi-Fi: app is not Device Owner/Profile Owner and Shizuku is not granted")
        return false
    }

    fun isWifiEnabled(context: Context): Boolean {
        val wifiManager = context.applicationContext
            .getSystemService(Context.WIFI_SERVICE) as WifiManager
        return wifiManager.isWifiEnabled
    }

    fun hasDeviceOwnerPrivilege(context: Context): Boolean {
        val dpm = context.getSystemService(DevicePolicyManager::class.java)
        return dpm.isDeviceOwnerApp(context.packageName) ||
            dpm.isProfileOwnerApp(context.packageName)
    }

    fun hasAutonomousPrivilege(context: Context): Boolean {
        return hasDeviceOwnerPrivilege(context) || ShizukuWifiEnabler.hasPermission()
    }

    @Suppress("DEPRECATION")
    private fun enableWifi(wifiManager: WifiManager): Boolean {
        return try {
            Log.d(TAG, "Wi-Fi is disabled, enabling with Device Owner privilege")
            val enabled = wifiManager.setWifiEnabled(true)
            Log.d(TAG, "WifiManager#setWifiEnabled result: $enabled")
            enabled
        } catch (e: SecurityException) {
            Log.e(TAG, "Wi-Fi enable blocked by Android: ${e.message}", e)
            false
        } catch (e: Exception) {
            Log.e(TAG, "Wi-Fi enable failed: ${e.message}", e)
            false
        }
    }
}
