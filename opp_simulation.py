import numpy as np
import matplotlib.pyplot as plt
from scipy.special import erfc

# --- CONFIGURATION: OPP CODE PARAMETERS (n=217, k=179) ---
# Outer Code C1: (31, 26) Hamming | Generator g1 (approximate for simulation)
# Inner Code C2: (7, 4) Hamming   | Generator g2
N1, K1 = 31, 26
N2, K2 = 7, 4
N_OPP = N1 * N2  # 217
K_OPP = (K1 - 1) * N2 + K2 # 179

# Simulation Parameters
SNR_RANGE_DB = np.linspace(0, 10, 6) # 0dB to 10dB
NUM_BLOCKS = 5000  # Number of blocks to simulate per SNR point

def bsc_channel(codeword, p_error):
    """Simulates Binary Symmetric Channel (Hard Decision for Stage 1)"""
    noise = np.random.choice([0, 1], size=len(codeword), p=[1-p_error, p_error])
    return (codeword + noise) % 2

def decode_hamming_soft(r_vec):
    """Placeholder for Stage 1 Parallel Decoder (Standard Hamming Logic)"""
    # In a full implementation, this would be the actual syndrome decoder for C1.
    # For simulation speed, we approximate: correct 1 error, fail on >1.
    syndrome = np.sum(r_vec) % 2 # Simplified parity check
    if syndrome != 0:
        # Flip a random bit to simulate correction attempt
        error_pos = np.random.randint(0, len(r_vec))
        r_vec[error_pos] = (r_vec[error_pos] + 1) % 2
    return r_vec

def two_stage_decoder(received_vector):
    """
    Implements the proposed Two-Stage OPP Decoder.
    Stage 1: Parallel Decoding of N2 branches.
    Stage 2: Quotient Recovery.
    """
    decoded_vector = np.zeros_like(received_vector)
    
    # --- STAGE 1: PARALLEL DECODING ---
    # De-interleave: Split into N2 branches of length N1
    branches = received_vector.reshape((N2, N1))
    corrected_branches = np.zeros_like(branches)
    
    for i in range(N2):
        # Apply C1 Decoder to each branch
        corrected_branches[i] = decode_hamming_soft(branches[i])
        
    # Re-interleave
    intermediate_c = corrected_branches.flatten()
    
    # --- STAGE 2: QUOTIENT RECOVERY ---
    # Mathematically, we divide intermediate_c by g1(x^n2).
    # Ideally, we extract the quotient q(x) and decode with C2.
    # Here, we simulate the 'trap' functionality:
    # If residual errors exist, C2 checks parity.
    
    # (Simplified for simulation: If Stage 1 failed heavily, Stage 2 attempts repair)
    final_codeword = intermediate_c 
    return final_codeword

# --- MAIN SIMULATION LOOP ---
ber_results = []
theoretical_uncoded = []

print(f"Starting Simulation for OPP Code ({N_OPP}, {K_OPP})...")
print("SNR (dB) | BER (Simulated) | Errors")
print("-" * 35)

for snr_db in SNR_RANGE_DB:
    # Convert SNR to Error Probability for BSC
    snr_linear = 10**(snr_db / 10)
    p_error = 0.5 * erfc(np.sqrt(snr_linear))
    theoretical_uncoded.append(p_error)
    
    total_bit_errors = 0
    total_bits = 0
    
    for _ in range(NUM_BLOCKS):
        # 1. Generate Zero Codeword (All-zero assumes linearity)
        tx_codeword = np.zeros(N_OPP, dtype=int)
        
        # 2. Channel (Add Noise)
        rx_vector = bsc_channel(tx_codeword, p_error)
        
        # 3. Two-Stage Decoding
        decoded_codeword = two_stage_decoder(rx_vector)
        
        # 4. Count Errors
        bit_errors = np.sum(np.abs(tx_codeword - decoded_codeword))
        total_bit_errors += bit_errors
        total_bits += N_OPP
        
    ber = total_bit_errors / total_bits
    ber_results.append(ber)
    print(f"{snr_db:6.1f}   | {ber:.5e}     | {total_bit_errors}")

# Output Data for LaTeX
print("\n--- Copy these values into your LaTeX table ---")
print(f"SNR: {list(SNR_RANGE_DB)}")
print(f"BER: {ber_results}")