package com.autowifi.reconnector

import android.app.Service
import android.content.Intent
import android.os.IBinder
import android.os.Handler
import android.os.Looper
import android.util.Log

class WifiReconnectService : Service() {
    
    private val handler = Handler(Looper.getMainLooper())
    private var checkRunnable: Runnable? = null
    private val CHECK_INTERVAL = 2000L // Check every 2 seconds
    
    override fun onCreate() {
        super.onCreate()
        startWifiCheck()
    }
    
    override fun onStartCommand(intent: Intent?, flags: Int, startId: Int): Int {
        return START_STICKY
    }
    
    override fun onBind(intent: Intent?): IBinder? {
        return null
    }
    
    override fun onDestroy() {
        super.onDestroy()
        stopWifiCheck()
    }
    
    private fun startWifiCheck() {
        checkRunnable = object : Runnable {
            override fun run() {
                checkAndReconnectWifi()
                handler.postDelayed(this, CHECK_INTERVAL)
            }
        }
        handler.post(checkRunnable!!)
    }
    
    private fun stopWifiCheck() {
        checkRunnable?.let {
            handler.removeCallbacks(it)
        }
    }
    
    private fun checkAndReconnectWifi() {
        try {
            WifiPrompt.handleWifiState(applicationContext)
        } catch (e: Exception) {
            Log.e("WifiReconnect", "Error checking WiFi: ${e.message}")
        }
    }
}
