package com.autowifi.reconnector

import android.content.Context
import android.util.Log

object WifiPrompt {
    private const val TAG = "WifiPrompt"

    fun handleWifiState(context: Context) {
        val restored = WifiRestorer.ensureWifiEnabled(context)
        Log.d(TAG, "Wi-Fi restore check finished: $restored")
    }
}
