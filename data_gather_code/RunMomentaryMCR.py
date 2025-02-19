import MomentaryChangeMCR

anomaly_config = {
    "327125E": ("drift", 10),
    "33559CF": ("drift", 10),
}
anomaly_config1 = {
    "327125E": ("drift", 10),
}
anomaly_config2 = {
    "327125E": ("drift", 50),
    "33559CF": ("drift", 50),
}
anomaly_config3 = {
    "327125E": ("drift", 50),
}

print("Running 0.5 second test")

# anomaly lasts a second
MomentaryChangeMCR.skew(1800, anom_start=900, anom_end=902, anom_config=anomaly_config)
MomentaryChangeMCR.skew(1800, anom_start=900, anom_end=902, anom_config=anomaly_config1)
MomentaryChangeMCR.skew(1800, anom_start=900, anom_end=902, anom_config=anomaly_config2)
MomentaryChangeMCR.skew(1800, anom_start=900, anom_end=902, anom_config=anomaly_config3)

# anomaly lasts 2 seconds
MomentaryChangeMCR.skew(1800, anom_start=900, anom_end=904, anom_config=anomaly_config)
MomentaryChangeMCR.skew(1800, anom_start=900, anom_end=904, anom_config=anomaly_config1)
MomentaryChangeMCR.skew(1800, anom_start=900, anom_end=904, anom_config=anomaly_config2)
MomentaryChangeMCR.skew(1800, anom_start=900, anom_end=904, anom_config=anomaly_config3)

# anomaly lasts 10 seconds
MomentaryChangeMCR.skew(1800, anom_start=900, anom_end=920, anom_config=anomaly_config)
MomentaryChangeMCR.skew(1800, anom_start=900, anom_end=920, anom_config=anomaly_config1)
MomentaryChangeMCR.skew(1800, anom_start=900, anom_end=920, anom_config=anomaly_config2)
MomentaryChangeMCR.skew(1800, anom_start=900, anom_end=920, anom_config=anomaly_config3)

# anomaly lasts 50 seconds
MomentaryChangeMCR.skew(1800, anom_start=900, anom_end=1000, anom_config=anomaly_config)
MomentaryChangeMCR.skew(1800, anom_start=900, anom_end=1000, anom_config=anomaly_config1)
MomentaryChangeMCR.skew(1800, anom_start=900, anom_end=1000, anom_config=anomaly_config2)
MomentaryChangeMCR.skew(1800, anom_start=900, anom_end=1000, anom_config=anomaly_config3)
