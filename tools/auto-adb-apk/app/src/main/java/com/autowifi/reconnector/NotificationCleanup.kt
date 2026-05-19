package com.autowifi.reconnector

import android.app.NotificationManager
import android.content.Context
import android.os.Build

object NotificationCleanup {
    private const val LEGACY_MONITOR_CHANNEL_ID = "wifi_monitor"

    fun removeLegacyChannels(context: Context) {
        if (Build.VERSION.SDK_INT < Build.VERSION_CODES.O) {
            return
        }

        context.getSystemService(NotificationManager::class.java)
            .deleteNotificationChannel(LEGACY_MONITOR_CHANNEL_ID)
    }
}
