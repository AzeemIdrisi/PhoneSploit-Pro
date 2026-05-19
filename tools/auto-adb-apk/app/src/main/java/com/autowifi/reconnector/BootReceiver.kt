package com.autowifi.reconnector

import android.content.BroadcastReceiver
import android.content.Context
import android.content.Intent
import android.util.Log
import androidx.work.ExistingWorkPolicy
import androidx.work.OneTimeWorkRequestBuilder
import androidx.work.WorkManager

class BootReceiver : BroadcastReceiver() {
    
    override fun onReceive(context: Context, intent: Intent) {
        NotificationCleanup.removeLegacyChannels(context)

        if (intent.action == Intent.ACTION_BOOT_COMPLETED || 
            intent.action == "android.intent.action.QUICKBOOT_POWERON" ||
            intent.action == Intent.ACTION_MY_PACKAGE_REPLACED ||
            intent.action == Intent.ACTION_PACKAGE_REPLACED) {

            if (!WifiRestorer.hasAutonomousPrivilege(context)) {
                Log.w("BootReceiver", "Auto WiFi requires Device Owner or Shizuku; monitor service not started")
                return
            }
            
            Log.d("BootReceiver", "Boot or install completed, starting WiFi reconnector worker")
            startShizukuMonitor(context)
            runImmediateWifiCheck(context)
            scheduleWifiWorker(context)
            
            Log.d("BootReceiver", "WiFi check worker scheduled")
        }
    }

    private fun startShizukuMonitor(context: Context) {
        val appContext = context.applicationContext
        Thread {
            val started = ShizukuWifiEnabler.startMonitor(appContext)
            Log.d("BootReceiver", "Shizuku shell monitor started: $started")
        }.start()
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
