package com.autowifi.reconnector

import android.content.Context
import android.content.ComponentName
import android.content.ServiceConnection
import android.content.pm.PackageManager
import android.os.IBinder
import android.util.Log
import rikka.shizuku.Shizuku
import java.util.concurrent.CountDownLatch
import java.util.concurrent.TimeUnit

object ShizukuWifiEnabler {
    private const val TAG = "ShizukuWifiEnabler"
    private const val USER_SERVICE_VERSION = 4
    private const val USER_SERVICE_TIMEOUT_SECONDS = 75L
    const val REQUEST_PERMISSION_CODE = 4201
    private val commandLock = Any()

    fun isAvailable(): Boolean {
        return try {
            Shizuku.pingBinder()
        } catch (e: Exception) {
            false
        }
    }

    fun hasPermission(): Boolean {
        return try {
            val granted = isAvailable() &&
                !Shizuku.isPreV11() &&
                Shizuku.checkSelfPermission() == PackageManager.PERMISSION_GRANTED
            Log.d(TAG, "Shizuku permission granted=$granted")
            granted
        } catch (e: Exception) {
            Log.w(TAG, "Cannot check Shizuku permission: ${e.message}")
            false
        }
    }

    fun requestPermissionIfPossible(): PermissionRequestResult {
        return try {
            if (!isAvailable() || Shizuku.isPreV11()) {
                Log.w(TAG, "Shizuku is not available")
                PermissionRequestResult.UNAVAILABLE
            } else if (Shizuku.checkSelfPermission() == PackageManager.PERMISSION_GRANTED) {
                Log.d(TAG, "Shizuku permission already granted")
                PermissionRequestResult.GRANTED
            } else if (Shizuku.shouldShowRequestPermissionRationale()) {
                Log.w(TAG, "Shizuku permission was denied with rationale")
                PermissionRequestResult.DENIED
            } else {
                Log.d(TAG, "Requesting Shizuku permission")
                Shizuku.requestPermission(REQUEST_PERMISSION_CODE)
                PermissionRequestResult.REQUESTED
            }
        } catch (e: Exception) {
            Log.w(TAG, "Cannot request Shizuku permission: ${e.message}")
            PermissionRequestResult.UNAVAILABLE
        }
    }

    fun enableWifi(context: Context): Boolean {
        synchronized(commandLock) {
            if (WifiRestorer.isWifiEnabled(context)) {
                Log.d(TAG, "Wi-Fi became enabled before Shizuku command")
                return true
            }

            if (!hasPermission()) {
                Log.w(TAG, "Cannot enable Wi-Fi: Shizuku permission is not granted")
                return false
            }

            return try {
                Log.d(TAG, "Wi-Fi is disabled, enabling through Shizuku UserService")
                if (!runEnableCommandThroughUserService(context)) {
                    return false
                }

                Thread.sleep(2000)
                val enabled = WifiRestorer.isWifiEnabled(context)
                Log.d(TAG, "Shizuku Wi-Fi command result, enabled=$enabled")
                enabled
            } catch (e: Exception) {
                Log.e(TAG, "Shizuku Wi-Fi command failed: ${e.message}", e)
                false
            }
        }
    }

    fun startMonitor(context: Context): Boolean {
        if (!hasPermission()) {
            Log.w(TAG, "Cannot start shell monitor: Shizuku permission is not granted")
            return false
        }

        return callUserService(context, removeAfterCall = false) { service ->
            val started = service.startMonitor()
            val running = service.isMonitorRunning()
            Log.d(TAG, "Shizuku shell monitor started=$started running=$running")
            started && running
        }
    }

    fun stopMonitor(context: Context): Boolean {
        if (!hasPermission()) {
            return false
        }

        return callUserService(context, removeAfterCall = false) { service ->
            service.stopMonitor()
        }
    }

    fun enableAdbTcp(context: Context, port: Int = 5555): Boolean {
        if (!hasPermission()) {
            Log.w(TAG, "Cannot enable ADB TCP: Shizuku permission is not granted")
            return false
        }

        return callUserService(context, removeAfterCall = false) { service ->
            service.enableAdbTcp(port)
        }
    }

    private fun runEnableCommandThroughUserService(context: Context): Boolean {
        return callUserService(context, removeAfterCall = false) { service ->
            service.enableWifi()
        }
    }

    private fun callUserService(
        context: Context,
        removeAfterCall: Boolean,
        action: (IWifiShellService) -> Boolean
    ): Boolean {
        val latch = CountDownLatch(1)
        var result = false

        val args = Shizuku.UserServiceArgs(
            ComponentName(context, WifiShellUserService::class.java)
        )
            .daemon(true)
            .debuggable(true)
            .processNameSuffix("wifi_shell")
            .version(USER_SERVICE_VERSION)

        val connection = object : ServiceConnection {
            override fun onServiceConnected(name: ComponentName, binder: IBinder) {
                try {
                    result = action(IWifiShellService.Stub.asInterface(binder))
                } catch (e: Exception) {
                    Log.e(TAG, "Shizuku UserService call failed: ${e.message}", e)
                } finally {
                    latch.countDown()
                }
            }

            override fun onServiceDisconnected(name: ComponentName) {
                latch.countDown()
            }
        }

        return try {
            Shizuku.bindUserService(args, connection)
            val connected = latch.await(USER_SERVICE_TIMEOUT_SECONDS, TimeUnit.SECONDS)
            if (!connected) {
                Log.w(TAG, "Shizuku UserService connection timed out")
                false
            } else {
                result
            }
        } catch (e: Exception) {
            Log.e(TAG, "Cannot bind Shizuku UserService: ${e.message}", e)
            false
        } finally {
            try {
                Shizuku.unbindUserService(args, connection, removeAfterCall)
            } catch (_: Exception) {
            }
        }
    }

    enum class PermissionRequestResult {
        GRANTED,
        REQUESTED,
        DENIED,
        UNAVAILABLE
    }
}
