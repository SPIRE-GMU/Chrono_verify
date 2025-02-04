import pandas as pd
import numpy as np
import math
import matplotlib.pyplot as plt
from filterpy.kalman import KalmanFilter

# Load CSV

filename = r"j:\SynchData\DriftScaledSynch_2025-01-27_10-59-45.csv" # when the variance gets too small this code does NOT work
df = pd.read_csv(filename)

# Extract Skew and Elapsed Time for each USRP
time_steps = df["Iteration"].values
elapsed_327125E = df["Elapsed_327125E"].values
skew_327125E = df["Skew_327125E"].values
elapsed_33559CF = df["Elapsed_33559CF"].values
skew_33559CF = df["Skew_33559CF"].values
elapsed_329089E = df["Elapsed_329089E"].values
skew_329089E = df["Skew_329089E"].values

def kalman():
    delta_t = 1 # change to follow either iterations (which increases by 1 anyways) or to follow elapsed time for a given device
    q1, q2, q3 = 0.001, 0.000001, 0.000000001  # Process noise parameters


    # clock-state is a column vector of
    # x(t) = [time offset state, frequency offset state, frequency drift state] = 3 states (3 dimensions)
    # dim_z is 1 because the observation is 1 dimentional

    filter = KalmanFilter(dim_x=3, dim_z=1)

    # State Transition Matrix Fn
    # matrix...

    filter.F = np.array([[1, delta_t, (delta_t**2)/2],
                        [0,1,delta_t],
                        [0,0,1]])

    # Process Noise Covariance Matrix Q

    filter.Q = np.array([[q1*delta_t + q2*(delta_t**3)/3 + q3*(delta_t**5)/20, q2*(delta_t**2)/2 + q3*(delta_t**4)/8, q3*(delta_t**3)/6],
                        [q2*(delta_t**2)/2 + q3*(delta_t**4)/8, q2*delta_t + q3*(delta_t**3)/3, q3*(delta_t**2)/2],
                        [q3*(delta_t**3)/6, q3*(delta_t**2)/2, q3*delta_t]])

    # Measurement Matrix H

    filter.H = np.array([[1,0,0]])

    # Measurement Noise Covariance R TODO figure out how and when to change this

    filter.R = np.array([[0]])

    # Initial State Estimate m0

    # this corresponds to the x dim!!!
    filter.x = np.array([[0],
                        [0],
                        [0]])

    # Initial Covariance Matrix P <- assuming that this is identity of a 3x3 matrix
    # scale this up if unsure about if clock offset starts at 0 or not
    filter.P = np.eye(3)

    return filter


# Filters for each device
kf_327125E = kalman()
kf_33559CF = kalman()
kf_329089E = kalman()

smoothing_factor = 0.01
threshold = 0
k = 128

predictions_batch_327125E = []
predictions_batch_33559CF = []
predictions_batch_329089E = []

log_likelihoods_327125E = [1]
log_likelihoods_33559CF = [1]
log_likelihoods_329089E = [1]

anomalies_327125E = []
anomalies_33559CF = []
anomalies_329089E = []

# Store results
estimates_327125E = []
estimates_33559CF = []
estimates_329089E = []

def prob_dens_func(predictions):

    m_in = predictions[-1]

    mean = np.mean(predictions[:-1])
    print(f"mean: {mean}")
    print(f"m_in: {m_in}")
    
    variance = pd.Series(predictions[:-1]).var()
    print(f"variance: {variance}")

    print(f"{np.exp(-((m_in - mean) ** 2) / (variance))}")
    print(f"{(1 / np.sqrt(2 * np.pi * variance))}") # currently an issue when the time between measurements is too small that the variance becomes too low resulting in useless pdf
    pdf = (np.exp(-((m_in - mean) ** 2) / (variance)) / np.sqrt(2 * np.pi * variance))
    print(f"pdf: {pdf}")
    return pdf

def log_likelihood(pdf, z_prev):
    z_i = smoothing_factor*z_prev + (1-smoothing_factor)*math.log(pdf)
    print(f"log_likelihood: {z_i} threshold: {threshold}")
    return z_i

for i in range(len(time_steps)):
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

    predictions_batch_327125E.append(predicted_327125E)
    predictions_batch_33559CF.append(predicted_33559CF)
    predictions_batch_329089E.append(predicted_329089E)

    if len(predictions_batch_327125E) == k:
        pdf_327125E = prob_dens_func(predictions_batch_327125E)
        smoothed_327125E = log_likelihood(pdf_327125E, log_likelihoods_327125E[-1])
        pdf_33559CF = prob_dens_func(predictions_batch_33559CF)
        smoothed_33559CF = log_likelihood(pdf_33559CF, log_likelihoods_33559CF[-1])
        pdf_329089E = prob_dens_func(predictions_batch_329089E)
        smoothed_329089E = log_likelihood(pdf_329089E, log_likelihoods_329089E[-1])

        log_likelihoods_327125E.append(smoothed_327125E)
        log_likelihoods_33559CF.append(smoothed_33559CF)
        log_likelihoods_329089E.append(smoothed_329089E)

        anomalies_327125E.append(smoothed_327125E < threshold)
        anomalies_33559CF.append(smoothed_33559CF < threshold)
        anomalies_329089E.append(smoothed_329089E < threshold)

        predictions_batch_327125E.clear()
        predictions_batch_33559CF.clear()
        predictions_batch_329089E.clear()

    # Update with measured skew
    kf_327125E.update(z_327125E)
    kf_33559CF.update(z_33559CF)
    kf_329089E.update(z_329089E)

    # Store estimated time offset
    estimates_327125E.append(kf_327125E.x[0, 0])
    estimates_33559CF.append(kf_33559CF.x[0, 0])
    estimates_329089E.append(kf_329089E.x[0, 0])

# Create the subplots
fig, axes = plt.subplots(3, 1, figsize=(8, 10))  # 3 rows, 1 column

# First device (327125E)
axes[0].plot(time_steps, estimates_327125E, label="Kalman Estimate - 327125E", color="blue")
axes[0].plot(time_steps, skew_327125E, label="Actual Skew - 327125E", color="cyan", linestyle="--")  # Actual skew

axes[0].set_xlabel("Iteration")
axes[0].set_ylabel("Time Offset / Skew")
axes[0].set_title("Kalman Filter - 327125E")
axes[0].legend()

# Second device (33559CF)
axes[1].plot(time_steps, estimates_33559CF, label="Kalman Estimate - 33559CF", color="green")
axes[1].plot(time_steps, skew_33559CF, label="Actual Skew - 33559CF", color="lime", linestyle="--")  # Actual skew

# Third device (329089E)
axes[2].plot(time_steps, estimates_329089E, label="Kalman Estimate - 329089E", color="purple")
axes[2].plot(time_steps, skew_329089E, label="Actual Skew - 329089E", color="violet", linestyle="--")  # Actual skew

# Show the plots
plt.tight_layout()
plt.show()





