package com.autowifi.reconnector;

interface IWifiShellService {
    boolean enableWifi();
    boolean enableAdbTcp(int port);
    boolean isAdbTcpListening(int port);
    boolean startMonitor();
    boolean stopMonitor();
    boolean isMonitorRunning();
    void destroy();
}
