import ManipulateMasterClockRate
import MasterClockRateTenthSecond

print("Running 0.5 second test")

anomaly_config = {
    "33559CF": ("drift", 1),   # 50 ppm drift on 327125E
}

anomaly_config1 = {
    "33559CF": ("drift", 5) # 100 ppm jitter on 33559CF
}

anomaly_config2 = {
    "33559CF": ("drift", 10),   # 50 ppm drift on 327125E
}

anomaly_config3 = {
    "33559CF": ("drift", 20),   # 50 ppm drift on 327125E
}

anomaly_config4 = {
    "33559CF": ("drift", 30),   # 50 ppm drift on 327125E
}

anomaly_config5 = {
    "33559CF": ("drift", 40),   # 50 ppm drift on 327125E
}

anomaly_config6 = {
    "33559CF": ("drift", 50),   # 50 ppm drift on 327125E
}

anomaly_config7 = {
    "33559CF": ("drift", -30),   # 50 ppm drift on 327125E
}

anomaly_config8 = {
    "33559CF": ("drift", -40),   # 50 ppm drift on 327125E
}

anomaly_config9 = {
    "33559CF": ("drift", -50),   # 50 ppm drift on 327125E
}

anomaly_config10 = {
    "33559CF": ("drift", -10),   # 50 ppm drift on 327125E
}

ManipulateMasterClockRate.skew(3600, anom_start=1800, anom_config=anomaly_config) # 30 min
ManipulateMasterClockRate.skew(3600, anom_start=1800, anom_config=anomaly_config1) # 30 min
ManipulateMasterClockRate.skew(3600, anom_start=1800, anom_config=anomaly_config2) # 30 min
ManipulateMasterClockRate.skew(3600, anom_start=1800, anom_config=anomaly_config3) # 30 min
ManipulateMasterClockRate.skew(3600, anom_start=1800, anom_config=anomaly_config4) # 30 min
ManipulateMasterClockRate.skew(3600, anom_start=1800, anom_config=anomaly_config5) # 30 min
ManipulateMasterClockRate.skew(3600, anom_start=1800, anom_config=anomaly_config6) # 30 min
ManipulateMasterClockRate.skew(3600, anom_start=1800, anom_config=anomaly_config7) # 30 min
ManipulateMasterClockRate.skew(3600, anom_start=1800, anom_config=anomaly_config8) # 30 min
ManipulateMasterClockRate.skew(3600, anom_start=1800, anom_config=anomaly_config9) # 30 min
ManipulateMasterClockRate.skew(3600, anom_start=1800, anom_config=anomaly_config10) # 30 min

print("Running tenth second test")


MasterClockRateTenthSecond.skew(36000, anom_start=18000, anom_config=anomaly_config) # 30 min
MasterClockRateTenthSecond.skew(36000, anom_start=18000, anom_config=anomaly_config1) # 30 min
MasterClockRateTenthSecond.skew(36000, anom_start=18000, anom_config=anomaly_config2) # 30 min
MasterClockRateTenthSecond.skew(36000, anom_start=18000, anom_config=anomaly_config3) # 30 min
MasterClockRateTenthSecond.skew(36000, anom_start=18000, anom_config=anomaly_config4) # 30 min
MasterClockRateTenthSecond.skew(36000, anom_start=18000, anom_config=anomaly_config5) # 30 min
MasterClockRateTenthSecond.skew(36000, anom_start=18000, anom_config=anomaly_config6) # 30 min
MasterClockRateTenthSecond.skew(36000, anom_start=18000, anom_config=anomaly_config7) # 30 min
MasterClockRateTenthSecond.skew(36000, anom_start=18000, anom_config=anomaly_config8) # 30 min
MasterClockRateTenthSecond.skew(36000, anom_start=18000, anom_config=anomaly_config9) # 30 min
MasterClockRateTenthSecond.skew(36000, anom_start=18000, anom_config=anomaly_config10) # 30 min