package com.autowifi.reconnector

import android.content.BroadcastReceiver
import android.content.Context
import android.content.Intent
import android.net.wifi.WifiManager
import android.util.Log
import androidx.work.ExistingWorkPolicy
import androidx.work.OneTimeWorkRequestBuilder
import androidx.work.WorkManager

class WifiStateReceiver : BroadcastReceiver() {
    
    override fun onReceive(context: Context, intent: Intent) {
        when (intent.action) {
            WifiManager.WIFI_STATE_CHANGED_ACTION -> {
                if (!WifiRestorer.hasAutonomousPrivilege(context)) {
                    Log.w("WifiStateReceiver", "Auto WiFi requires Device Owner or Shizuku; ignoring Wi-Fi state broadcast")
                    return
                }

                val wifiState = intent.getIntExtra(WifiManager.EXTRA_WIFI_STATE, WifiManager.WIFI_STATE_UNKNOWN)
                
                when (wifiState) {
                    WifiManager.WIFI_STATE_DISABLED -> {
                        Log.d("WifiStateReceiver", "WiFi disabled, trying automatic restore")
                        runImmediateWifiCheck(context)
                        scheduleWifiWorker(context)
                    }
                    WifiManager.WIFI_STATE_ENABLED -> {
                        Log.d("WifiStateReceiver", "WiFi enabled")
                    }
                }
            }
        }
    }

    private fun runImmediateWifiCheck(context: Context) {
        val appContext = context.applicationContext
        val pendingResult = goAsync()

        Thread {
            try {
                WifiPrompt.handleWifiState(appContext)
            } finally {
                pendingResult.finish()
            }
        }.start()
    }

    private fun scheduleWifiWorker(context: Context) {
        val wifiCheckWork = OneTimeWorkRequestBuilder<WifiCheckWorker>().build()

        WorkManager.getInstance(context).enqueueUniqueWork(
            "wifiCheckWork",
            ExistingWorkPolicy.REPLACE,
            wifiCheckWork
        )
    }
}
