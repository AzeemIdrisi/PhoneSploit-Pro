package com.autowifi.reconnector

import android.content.Context
import android.util.Log
import androidx.work.Worker
import androidx.work.WorkerParameters

class WifiCheckWorker(context: Context, params: WorkerParameters) : Worker(context, params) {
    
    override fun doWork(): Result {
        try {
            if (!WifiRestorer.hasAutonomousPrivilege(applicationContext)) {
                Log.w("WifiCheckWorker", "Auto WiFi requires Device Owner or Shizuku; skipping")
                return Result.success()
            }

            if (ShizukuWifiEnabler.hasPermission()) {
                ShizukuWifiEnabler.startMonitor(applicationContext)
            }
            WifiPrompt.handleWifiState(applicationContext)
            return Result.success()
        } catch (e: Exception) {
            Log.e("WifiCheckWorker", "Error checking WiFi: ${e.message}", e)
            return Result.retry()
        }
    }
}
