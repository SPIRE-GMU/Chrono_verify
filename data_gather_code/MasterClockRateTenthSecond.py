import time
import random
import csv
import uhd
from datetime import datetime

# This version of the data collection now includes an anomaly generation function
# The anomaly generation is done by manipulating the Master Clock rate of some USRP
# Hopefully this will create some obviously anomalous Skew data that the Kalman can view

def pps_set(usrp, usrp1, usrp2, source):
    
    # Set clock and time sources to source preference
    usrp.set_clock_source(f"{source}")
    usrp1.set_clock_source(f"{source}")
    usrp2.set_clock_source(f"{source}")
    if source == "internal": # set to none if internal
        usrp.set_time_source("none")
        usrp1.set_time_source("none")
        usrp2.set_time_source("none")
    else:
        usrp.set_time_source(f"{source}")
        usrp1.set_time_source(f"{source}")
        usrp2.set_time_source(f"{source}")
    
    print(f"USRP 327125E Clock Source: {usrp.get_clock_source(0)}")
    print(f"USRP 33559CF Clock Source: {usrp1.get_clock_source(0)}")
    print(f"USRP 329089E Clock Source: {usrp2.get_clock_source(0)}")


def mcr_anomaly_make(usrp, anomaly_type, deviation=0.1): # deviation is the severity of anomalous activity
    clock_rate = usrp.get_master_clock_rate()

    if anomaly_type == "drift":
        new_rate = clock_rate * (1 + deviation / 1e6)
        print(f"Applying clock drift: Setting MCR from {clock_rate} Hz to {new_rate} Hz")
    
    elif anomaly_type == "jitter":
        new_rate = clock_rate * (1 + random.uniform(-deviation, deviation) / 1e6)
        print(f"Applying jitter: Fluctuating MCR to {new_rate} Hz")
    
    elif anomaly_type == "offset":
        new_rate = clock_rate + deviation * 1e3
        print(f"Applying frequency offset: Changing MCR from {clock_rate} Hz to {new_rate} Hz")
    
    elif anomaly_type == "phase":
        # Simulating phase offset by temporarily changing MCR and resetting
        new_rate = clock_rate * (1 + deviation / 1e6)
        print(f"Applying phase anomaly: Short-term change to {new_rate} Hz before resetting")
        usrp.set_master_clock_rate(new_rate)
        time.sleep(0.1)  # Simulate phase error
        new_rate = clock_rate  # Reset to original MCR

    usrp.set_master_clock_rate(new_rate)

def skew(iterations, anom_start=0, anom_config=None):
    # Initialize each USRP device and record their initialization times
    init_time_327125E = time.time()
    usrp = uhd.usrp.MultiUSRP("serial=327125E")
    usrp_mcr = usrp.get_master_clock_rate()
    
    init_time_33559CF = time.time()
    usrp1 = uhd.usrp.MultiUSRP("serial=33559CF")
    usrp1_mcr = usrp1.get_master_clock_rate()

    init_time_329089E = time.time()
    usrp2 = uhd.usrp.MultiUSRP("serial=329089E")
    usrp2_mcr = usrp2.get_master_clock_rate()

    pps_set(usrp, usrp1, usrp2, "external")

    # Prepare CSV file
    timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
    filename = f'Positive_MCRTest_TenthSecond_{timestamp}.csv'

    with open(filename, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow([
            'Iteration', 'Time', 
            'Skew_327125E', 'Elapsed_327125E', 
            'Skew_33559CF', 'Elapsed_33559CF', 
            'Skew_329089E', 'Elapsed_329089E', 
            'Last_PPS_327125E', 'Last_PPS_33559CF', 'Last_PPS_329089E',
            'Anomaly_327125E', 'Anomaly_33559CF', 'Anomaly_329089E'
        ])

        iteration = 0
        while iteration < iterations:
            anomaly_327125E = anomaly_33559CF = anomaly_329089E = "None"
            
            if anom_start != 0 and iteration >= anom_start:
                if anom_config:
                    if "327125E" in anom_config:
                        anomaly_327125E = f"{anom_config['327125E'][0]} ({anom_config['327125E'][1]} ppm)"
                        mcr_anomaly_make(usrp, *anom_config["327125E"])
                    if "33559CF" in anom_config:
                        anomaly_33559CF = f"{anom_config['33559CF'][0]} ({anom_config['33559CF'][1]} ppm)"
                        mcr_anomaly_make(usrp1, *anom_config["33559CF"])
                    if "329089E" in anom_config:
                        anomaly_329089E = f"{anom_config['329089E'][0]} ({anom_config['329089E'][1]} kHz)"
                        mcr_anomaly_make(usrp2, *anom_config["329089E"])

            # Get current time for all devices
            now_327125E = usrp.get_time_now().get_real_secs()
            skew_327125E = (time.time() - init_time_327125E) - now_327125E
            now_33559CF = usrp1.get_time_now().get_real_secs()
            skew_33559CF = (time.time() - init_time_33559CF) - now_33559CF
            now_329089E = usrp2.get_time_now().get_real_secs()
            skew_329089E = (time.time() - init_time_329089E) - now_329089E

            last_pps327125E = usrp.get_time_last_pps().get_real_secs()
            last_pps33559CF = usrp1.get_time_last_pps().get_real_secs()
            last_pps329089E = usrp2.get_time_last_pps().get_real_secs()
            
            print(f"Iteration {iteration}:")
            print(f"  Skew - 327125E: {skew_327125E}, Elapsed: {skew_327125E + now_327125E}, Last PPS: {last_pps327125E}, Anomaly: {anomaly_327125E}")
            print(f"  Skew - 33559CF: {skew_33559CF}, Elapsed: {skew_33559CF + now_33559CF}, Last PPS: {last_pps33559CF}, Anomaly: {anomaly_33559CF}")
            print(f"  Skew - 329089E: {skew_329089E}, Elapsed: {skew_329089E + now_329089E}, Last PPS: {last_pps329089E}, Anomaly: {anomaly_329089E}")

            # Write data
            writer.writerow([
                iteration, time.time(), 
                skew_327125E, skew_327125E + now_327125E, 
                skew_33559CF, skew_33559CF + now_33559CF, 
                skew_329089E, skew_329089E + now_329089E,
                last_pps327125E, last_pps33559CF, last_pps329089E,
                anomaly_327125E, anomaly_33559CF, anomaly_329089E
            ])

            # Sleep - this will change depending on how and what observing
            time.sleep(0.1)

            # Increment iteration count
            iteration += 1
        
        # Reset Clock Rates back to normal for next run
        usrp.set_master_clock_rate(usrp_mcr)
        usrp1.set_master_clock_rate(usrp1_mcr)
        usrp2.set_master_clock_rate(usrp2_mcr)

        print("\nRestored original master clock rates:")
        print(f"  USRP 327125E: {usrp_mcr} Hz")
        print(f"  USRP 33559CF: {usrp1_mcr} Hz")
        print(f"  USRP 329089E: {usrp2_mcr} Hz")


anomaly_config = {
    "327125E": ("drift", 50),   # 50 ppm drift on 327125E
    "33559CF": ("jitter", 100), # 100 ppm jitter on 33559CF
    "329089E": ("offset", 10)   # 10 kHz frequency offset on 329089E
}

anomaly_config1 = {
    "33559CF": ("jitter", 100) # 100 ppm jitter on 33559CF
}

anomaly_config2 = {
    "327125E": ("drift", 50),   # 50 ppm drift on 327125E
}

# skew(7200, anom_start=3600, anom_config=anomaly_config) # 1 hour
# skew(7200, anom_start=3600, anom_config=anomaly_config1) # 1 hour
# skew(7200, anom_start=3600, anom_config=anomaly_config2) # 1 hour