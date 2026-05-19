package com.autowifi.reconnector

import android.util.Log

class WifiShellUserService : IWifiShellService.Stub() {
    private val tag = "WifiShellUserService"
    private val adbTcpPort = 5555
    private val wifiRestoreDelayMs = 30000L
    private val monitorIntervalMs = 5000L
    private val adbTcpCheckIntervalMs = 30000L

    @Volatile
    private var monitorRunning = false
    private var monitorThread: Thread? = null
    private var lastAdbTcpCheckMs = 0L
    private val wifiCommandLock = Any()

    override fun enableWifi(): Boolean {
        return delayedEnableWifi()
    }

    override fun enableAdbTcp(port: Int): Boolean {
        return ensureAdbTcpEnabled(port)
    }

    override fun isAdbTcpListening(port: Int): Boolean {
        if (!isValidPort(port)) {
            return false
        }

        val sockets = runCommandForText(arrayOf("ss", "-ltn"))
        return sockets.lineSequence().any { line ->
            line.contains(":$port ") || line.trimEnd().endsWith(":$port")
        }
    }

    override fun startMonitor(): Boolean {
        if (monitorRunning && monitorThread?.isAlive == true) {
            Log.d(tag, "Shell Wi-Fi monitor is already running")
            return true
        }

        monitorRunning = true
        monitorThread = Thread {
            Log.d(tag, "Shell Wi-Fi monitor started")
            while (monitorRunning) {
                try {
                    if (shouldEnableWifi()) {
                        if (delayedEnableWifi()) {
                            Thread.sleep(2000)
                        }
                        ensureAdbTcpEnabled(adbTcpPort)
                    } else {
                        ensureAdbTcpEnabledIfDue()
                    }
                    Thread.sleep(monitorIntervalMs)
                } catch (_: InterruptedException) {
                    monitorRunning = false
                } catch (e: Exception) {
                    Log.w(tag, "Shell Wi-Fi monitor iteration failed: ${e.message}", e)
                    Thread.sleep(monitorIntervalMs)
                }
            }
            Log.d(tag, "Shell Wi-Fi monitor stopped")
        }.apply {
            name = "AutoWifiShellMonitor"
            isDaemon = true
            start()
        }

        return true
    }

    override fun stopMonitor(): Boolean {
        monitorRunning = false
        monitorThread?.interrupt()
        monitorThread = null
        return true
    }

    override fun isMonitorRunning(): Boolean {
        return monitorRunning && monitorThread?.isAlive == true
    }

    override fun destroy() {
        stopMonitor()
        System.exit(0)
    }

    private fun shouldEnableWifi(): Boolean {
        val status = runCommandForText(arrayOf("cmd", "wifi", "status")).lowercase()
        if (status.isBlank()) {
            Log.w(tag, "Wi-Fi status command returned no output; trying enable command")
            return true
        }

        return status.contains("wifi is disabled") ||
            status.contains("wifi is disabling") ||
            status.contains("wifi is unknown")
    }

    private fun delayedEnableWifi(): Boolean {
        synchronized(wifiCommandLock) {
            if (!shouldEnableWifi()) {
                Log.d(tag, "Wi-Fi became enabled before delayed restore")
                return true
            }

            Log.d(tag, "Wi-Fi disabled; waiting 30 seconds before restore")
            try {
                Thread.sleep(wifiRestoreDelayMs)
            } catch (_: InterruptedException) {
                Thread.currentThread().interrupt()
                return false
            }

            if (!shouldEnableWifi()) {
                Log.d(tag, "Wi-Fi restored manually during delay")
                return true
            }

            return runEnableCommand()
        }
    }

    private fun ensureAdbTcpEnabledIfDue(): Boolean {
        val now = System.currentTimeMillis()
        if (now - lastAdbTcpCheckMs < adbTcpCheckIntervalMs) {
            return true
        }

        lastAdbTcpCheckMs = now
        return ensureAdbTcpEnabled(adbTcpPort)
    }

    private fun ensureAdbTcpEnabled(port: Int): Boolean {
        if (!isValidPort(port)) {
            Log.w(tag, "Invalid ADB TCP port: $port")
            return false
        }

        runCommand(arrayOf("setprop", "service.adb.tcp.port", port.toString()))

        val configuredPort = runCommandForText(
            arrayOf("getprop", "service.adb.tcp.port")
        ).trim()
        val configured = configuredPort == port.toString()
        val listening = isAdbTcpListening(port)
        Log.d(tag, "ADB TCP port=$port configured=$configured listening=$listening")
        return configured && listening
    }

    private fun isValidPort(port: Int): Boolean {
        return port in 1..65535
    }

    private fun runEnableCommand(): Boolean {
        return try {
            Log.d(tag, "Executing shell Wi-Fi enable command")
            val process = Runtime.getRuntime().exec(
                arrayOf("cmd", "wifi", "set-wifi-enabled", "enabled")
            )
            val exitCode = process.waitFor()
            if (exitCode != 0) {
                val error = process.errorStream.bufferedReader().readText().trim()
                Log.w(tag, "Wi-Fi command failed with exit code $exitCode: $error")
                false
            } else {
                true
            }
        } catch (e: Exception) {
            Log.e(tag, "Wi-Fi command failed: ${e.message}", e)
            false
        }
    }

    private fun runCommand(command: Array<String>): Boolean {
        return try {
            val process = Runtime.getRuntime().exec(command)
            val error = process.errorStream.bufferedReader().readText().trim()
            val exitCode = process.waitFor()
            if (exitCode != 0) {
                Log.w(tag, "Command failed with exit code $exitCode: ${command.joinToString(" ")} $error")
                false
            } else {
                true
            }
        } catch (e: Exception) {
            Log.w(tag, "Command failed: ${command.joinToString(" ")} ${e.message}", e)
            false
        }
    }

    private fun runCommandForText(command: Array<String>): String {
        return try {
            val process = Runtime.getRuntime().exec(command)
            val output = process.inputStream.bufferedReader().readText().trim()
            val error = process.errorStream.bufferedReader().readText().trim()
            val exitCode = process.waitFor()

            if (exitCode != 0) {
                Log.w(tag, "Command failed with exit code $exitCode: $error")
                ""
            } else {
                output
            }
        } catch (e: Exception) {
            Log.w(tag, "Command failed: ${e.message}", e)
            ""
        }
    }
}
