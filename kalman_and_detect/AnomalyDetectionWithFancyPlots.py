import pandas as pd
import numpy as np
import math
import matplotlib.pyplot as plt
from filterpy.kalman import KalmanFilter
from collections import deque

# This code is the most up to date version of Anomaly Detection given Skew data of device clocks

filename = r"" # specify direct file path
df = pd.read_csv(filename) # data was saved to .csv files

# Extract Skew and Elapsed Time for each USRP
time_steps = df["Iteration"].values
elapsed_327125E = df["Elapsed_327125E"].values
skew_327125E = df["Skew_327125E"].values
elapsed_33559CF = df["Elapsed_33559CF"].values
skew_33559CF = df["Skew_33559CF"].values
elapsed_329089E = df["Elapsed_329089E"].values
skew_329089E = df["Skew_329089E"].values

def kalman(delta_t, fixed_dt=False): # delta t is decided by the clock's elapsed time or fixed dt

    if fixed_dt:
        delta_t = 1

    q1, q2, q3 = 1e-3, 1e-6, 1e-9 # clock noise

    filter = KalmanFilter(dim_x=3, dim_z=1)
    filter.F = np.array([[1, delta_t, (delta_t**2)/2],
                        [0,1,delta_t],
                        [0,0,1]])
    filter.Q = np.array([[q1*delta_t + q2*(delta_t**3)/3 + q3*(delta_t**5)/20, q2*(delta_t**2)/2 + q3*(delta_t**4)/8, q3*(delta_t**3)/6],
                        [q2*(delta_t**2)/2 + q3*(delta_t**4)/8, q2*delta_t + q3*(delta_t**3)/3, q3*(delta_t**2)/2],
                        [q3*(delta_t**3)/6, q3*(delta_t**2)/2, q3*delta_t]])
    
    filter.H = np.array([[1,0,0]])
    filter.R = np.array([[10]]) # Change between 0 and 10
    filter.x = np.array([[0],
                        [0],
                        [0]])
    filter.P = np.eye(3)

    return filter

# control delta_t
use_fixed_dt = False

# initialize Kalman Filters for each device

kf_327125E = kalman(elapsed_327125E[1] - elapsed_327125E[0], use_fixed_dt)
kf_33559CF = kalman(elapsed_33559CF[1] - elapsed_33559CF[0], use_fixed_dt)
kf_329089E = kalman(elapsed_329089E[1] - elapsed_329089E[0], use_fixed_dt)

# constants
smoothing_factor = 0.01
threshold = -300 # change as needed
k = 128 # change as needed

# using double ended queue to do the window
predictions_327125E = deque(maxlen=k)
predictions_33559CF = deque(maxlen=k)
predictions_329089E = deque(maxlen=k)

# initial LL values
log_likelihoods_327125E = [-1]
log_likelihoods_33559CF = [-1]
log_likelihoods_329089E = [-1]

anomalies_327125E = []
anomalies_33559CF = []
anomalies_329089E = []

for i in range(1, len(time_steps)):
    print(f"{i}th iteration with {len(time_steps)-i} remaining")
    
    # dynamically update delta_t with elapsed time at given iteration
    delta_t_327125E = 1 if use_fixed_dt else (elapsed_327125E[i] - elapsed_327125E[i - 1])
    delta_t_33559CF = 1 if use_fixed_dt else (elapsed_33559CF[i] - elapsed_33559CF[i - 1])
    delta_t_329089E = 1 if use_fixed_dt else (elapsed_329089E[i] - elapsed_329089E[i - 1])


    # update F matrices with new delta_t
    kf_327125E.F = np.array([[1, delta_t_327125E, (delta_t_327125E**2)/2],
                              [0, 1, delta_t_327125E],
                              [0, 0, 1]])
    
    kf_33559CF.F = np.array([[1, delta_t_33559CF, (delta_t_33559CF**2)/2],
                              [0, 1, delta_t_33559CF],
                              [0, 0, 1]])
    
    kf_329089E.F = np.array([[1, delta_t_329089E, (delta_t_329089E**2)/2],
                              [0, 1, delta_t_329089E],
                              [0, 0, 1]])

    # Get skew measurements
    z_327125E = np.array([[skew_327125E[i]]])
    z_33559CF = np.array([[skew_33559CF[i]]])
    z_329089E = np.array([[skew_329089E[i]]])

    # Predict step
    kf_327125E.predict()
    kf_33559CF.predict()
    kf_329089E.predict()

    predicted_327125E = kf_327125E.x[0, 0]
    predicted_33559CF = kf_33559CF.x[0, 0]
    predicted_329089E = kf_329089E.x[0, 0]

    predictions_327125E.append(predicted_327125E)
    predictions_33559CF.append(predicted_33559CF)
    predictions_329089E.append(predicted_329089E)

    if len(predictions_327125E) == k:
        def prob_dens_func(predictions):
            m_in = predictions[-1]
            mean = np.mean(list(predictions)[:-1])
            variance = np.var(list(predictions)[:-1], ddof=1)
            pdf = np.exp(-((m_in - mean) ** 2) / variance) / np.sqrt(2 * np.pi * variance)
            return pdf
        
        def log_likelihood(pdf, z_prev):
            if pdf == 0: # this is a current solution to the problem of PDF sometimes returning 0
                print("Zero detected")
                return z_prev
            else:
                return smoothing_factor * z_prev + (1 - smoothing_factor) * math.log(pdf)

        pdf_327125E = prob_dens_func(predictions_327125E)
        pdf_33559CF = prob_dens_func(predictions_33559CF)
        pdf_329089E = prob_dens_func(predictions_329089E)

        # get smoothed LL with most recent LL calculation as z_prev
        smoothed_327125E = log_likelihood(pdf_327125E, log_likelihoods_327125E[-1])
        smoothed_33559CF = log_likelihood(pdf_33559CF, log_likelihoods_33559CF[-1])
        smoothed_329089E = log_likelihood(pdf_329089E, log_likelihoods_329089E[-1])

        log_likelihoods_327125E.append(smoothed_327125E)
        log_likelihoods_33559CF.append(smoothed_33559CF)
        log_likelihoods_329089E.append(smoothed_329089E)

        anomalies_327125E.append(smoothed_327125E < threshold)
        anomalies_33559CF.append(smoothed_33559CF < threshold)
        anomalies_329089E.append(smoothed_329089E < threshold)

    kf_327125E.update(z_327125E)
    kf_33559CF.update(z_33559CF)
    kf_329089E.update(z_329089E)

plt.rcParams["font.family"] = "Times New Roman"
plt.rcParams.update({'font.size': 11})

usrp_data = {
    "327125E": (elapsed_327125E, skew_327125E, log_likelihoods_327125E, anomalies_327125E),
    "33559CF": (elapsed_33559CF, skew_33559CF, log_likelihoods_33559CF, anomalies_33559CF),
    "329089E": (elapsed_329089E, skew_329089E, log_likelihoods_329089E, anomalies_329089E),
}

for usrp_id, (elapsed, skew, log_likelihoods, anomalies) in usrp_data.items():
    fig, ax1 = plt.subplots(figsize=(4.5, 4))

    ax1.plot(elapsed, skew, label="Skew", color="black", linewidth=1)
    ax1.set_ylabel("Skew (in seconds)")
    ax1.set_xlabel("Elapsed Time (in seconds)")
    ax1.grid()

    ax2 = ax1.twinx()
    ax2.plot(elapsed[k:], log_likelihoods[1:], label="Log Likelihood", color="red", linewidth=1)  
    ax2.set_ylabel("Averaged LL of Clock Skew", color="red")
    ax2.tick_params(axis='y', labelcolor='red')

    anomaly_indices = [i for i, is_anomaly in enumerate(anomalies) if is_anomaly]
    anomaly_times = [elapsed[i + k] for i in anomaly_indices]
    anomaly_skews = [skew[i + k] for i in anomaly_indices]

    ax1.scatter(anomaly_times, anomaly_skews, color="red", marker="x", label="Anomaly", zorder=3, s=100)

    for i, (x, y) in enumerate(zip(anomaly_times, anomaly_skews)):
        ax1.annotate(
            f"{anomaly_indices[i] + k}", 
            (x, y), 
            textcoords="offset points", 
            xytext=(10,1), 
            ha='left', 
            fontsize=11, 
            color="red"
        )

    ax1.set_title(f"USRP {usrp_id}")
    ax1.grid()

    plt.subplots_adjust(top=0.9)
    plt.tight_layout()


plt.show()


