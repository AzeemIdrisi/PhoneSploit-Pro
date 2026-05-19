package com.autowifi.reconnector

import android.app.Activity
import android.content.Context
import android.content.pm.PackageManager
import android.os.Bundle
import android.util.Log
import androidx.work.ExistingWorkPolicy
import androidx.work.OneTimeWorkRequestBuilder
import androidx.work.WorkManager
import rikka.shizuku.Shizuku

class MainActivity : Activity() {
    private val shizukuPermissionListener =
        Shizuku.OnRequestPermissionResultListener { requestCode, grantResult ->
            if (requestCode == ShizukuWifiEnabler.REQUEST_PERMISSION_CODE) {
                val granted = grantResult == PackageManager.PERMISSION_GRANTED
                Log.d("MainActivity", "Shizuku permission granted: $granted")
                if (granted) {
                    checkWifiAndClose()
                } else {
                    finish()
                }
            }
        }

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        NotificationCleanup.removeLegacyChannels(this)

        Shizuku.addRequestPermissionResultListener(shizukuPermissionListener)

        if (!WifiRestorer.hasDeviceOwnerPrivilege(this) && !ShizukuWifiEnabler.hasPermission()) {
            Log.w("MainActivity", "Auto WiFi requires Device Owner or Shizuku")
            when (ShizukuWifiEnabler.requestPermissionIfPossible()) {
                ShizukuWifiEnabler.PermissionRequestResult.GRANTED -> checkWifiAndClose()
                ShizukuWifiEnabler.PermissionRequestResult.REQUESTED -> return
                ShizukuWifiEnabler.PermissionRequestResult.DENIED,
                ShizukuWifiEnabler.PermissionRequestResult.UNAVAILABLE -> finish()
            }
            return
        }

        checkWifiAndClose()
    }

    override fun onDestroy() {
        Shizuku.removeRequestPermissionResultListener(shizukuPermissionListener)
        super.onDestroy()
    }

    private fun checkWifiAndClose() {
        startShizukuMonitorAndClose()
    }

    private fun startShizukuMonitorAndClose() {
        val appContext = applicationContext

        Thread {
            val monitorStarted = if (ShizukuWifiEnabler.hasPermission()) {
                ShizukuWifiEnabler.startMonitor(appContext)
            } else {
                false
            }
            Log.d("MainActivity", "Shizuku shell monitor started: $monitorStarted")
            WifiPrompt.handleWifiState(appContext)
            startWifiWorker(appContext)
            Log.d("MainActivity", "WiFi check worker started")
        }.start()

        finish()
    }
    
    private fun startWifiWorker(context: Context) {
        val wifiCheckWork = OneTimeWorkRequestBuilder<WifiCheckWorker>().build()
        
        WorkManager.getInstance(context).enqueueUniqueWork(
            "wifiCheckWork",
            ExistingWorkPolicy.REPLACE,
            wifiCheckWork
        )
    }
}
