import numpy as np
import matplotlib.pyplot as plt

def generate_and_plot_cpc(r_width=1.0, theta_c_deg=30.0, truncation_pct=100.0, num_points=500):
    """
    Generates the 2D profile coordinates for a Compound Parabolic Concentrator (CPC),
    calculates metrics (concentration ratios, truncation losses), and plots the profile.
    
    Parameters:
    -----------
    r_width : float
        Width of the flat plate receiver at the base (centered at x=0, y=0).
    theta_c_deg : float
        Acceptance half-angle in degrees.
    truncation_pct : float
        Truncation level of the total height expressed as a percentage (1 to 100).
    num_points : int
        Number of discrete points to compute along each reflector profile.
        
    Returns:
    --------
    dict
        A dictionary containing the coordinates of the profiles and calculated metrics.
    """
    # 1. Geometry and Parametric Configuration
    theta_c = np.radians(theta_c_deg)
    sin_tc = np.sin(theta_c)
    
    # Full un-truncated design metrics
    a_full = r_width / sin_tc  # Full aperture width
    C_max = 1.0 / sin_tc       # Maximum theoretical concentration ratio
    
    # Generate fine array for parametric angle phi
    # For a left reflector focusing on the right receiver tip (r_width/2, 0):
    # phi = pi/2 + theta_c represents the bottom point, 2*theta_c represents the top point.
    phi = np.linspace(np.pi / 2 + theta_c, 2 * theta_c, num_points * 10)
    
    # Polar radius equation from the focus point
    r = (r_width * (1.0 + sin_tc)) / (1.0 - np.cos(phi))
    
    # Transform to Cartesian coordinates with receiver centered at (0, 0)
    x_left_full = r_width / 2.0 - r * np.sin(phi - theta_c)
    y_left_full = r * np.cos(phi - theta_c)
    
    # 2. Handle Height Truncation
    H_max = y_left_full[-1]
    H_target = H_max * (truncation_pct / 100.0)
    
    # Filter points matching the height threshold
    trunc_mask = y_left_full <= H_target
    x_left = x_left_full[trunc_mask]
    y_left = y_left_full[trunc_mask]
    
    # Downsample arrays to exact requested resolution
    idx = np.linspace(0, len(x_left) - 1, num_points, dtype=int)
    x_left, y_left = x_left[idx], y_left[idx]
    
    # Generate perfectly symmetrical right side reflector
    x_right = -x_left
    y_right = y_left.copy()
    
    # 3. Calculate Performance Metrics
    a_trunc = 2.0 * abs(x_left[-1])  # Top aperture width after truncation
    C_trunc = a_trunc / r_width      # New actual concentration ratio
    
    # Intercepted energy loss estimation based on lost aperture capture area
    efficiency_loss = ((a_full - a_trunc) / a_full) * 100.0
    
    # 4. Generate the Matplotlib Visualization
    fig, ax = plt.subplots(figsize=(8, 8))
    
    # Plot components
    ax.plot(x_left, y_left, color='blue', linewidth=2.5, label='Left Reflector')
    ax.plot(x_right, y_right, color='red', linewidth=2.5, label='Right Reflector')
    
    # Plot Receiver Plate (Bottom) and Aperture Plane (Top)
    ax.plot([-r_width/2, r_width/2], [0, 0], color='black', linewidth=4, label='Flat Plate Receiver')
    ax.plot([x_left[-1], x_right[-1]], [y_left[-1], y_right[-1]], color='green', 
            linestyle='--', linewidth=1.5, label='Aperture Width')
    
    # Reference Markers to show alignment visually
    ax.scatter([-r_width/2, r_width/2], [0, 0], color='purple', zorder=5)
    ax.scatter([x_left[-1], x_right[-1]], [y_left[-1], y_right[-1]], color='purple', zorder=5)
    
    # Set strict 1:1 Aspect Ratio constraints
    ax.set_aspect('equal', adjustable='box')
    
    # Titles and Meta Information
    ax.set_title(f"Compound Parabolic Concentrator (CPC) Profile\nHeight Truncated to {truncation_pct}%", 
                 fontsize=14, fontweight='bold', pad=15)
    ax.set_xlabel("X Coordinate", fontsize=11)
    ax.set_ylabel("Y Coordinate", fontsize=11)
    ax.grid(True, linestyle=':', alpha=0.6)
    
    # Structured summary text inside plot
    info_text = (
        f"Receiver Width ($r$): {r_width:.2f}\n"
        f"Acceptance Angle ($\\theta_c$): {theta_c_deg:.1f}°\n"
        f"Full Aperture Width: {a_full:.3f}\n"
        f"Truncated Aperture Width: {a_trunc:.3f}\n"
        f"Max Concentration Ratio ($C_{{max}}$): {C_max:.3f}\n"
        f"Actual Concentration Ratio ($C$): {C_trunc:.3f}\n"
        f"Max Design Height ($H_{{max}}$): {H_max:.3f}\n"
        f"Actual Profile Height ($H$): {H_target:.3f}\n"
        f"Efficiency Loss: {efficiency_loss:.2f}%"
    )
    
    # Place text box inside the plot area safely away from the profiles
    ax.text(0.05, 0.95, info_text, transform=ax.transAxes, fontsize=10,
            verticalalignment='top', bbox=dict(boxstyle='round,pad=0.5', facecolor='white', alpha=0.85, edgecolor='gray'))
    
    ax.legend(loc='lower right', framealpha=0.9)
    plt.tight_layout()
    plt.show()
    
    # Return numerical profile information for validation scripts
    return {
        'receiver': (-r_width/2.0, r_width/2.0),
        'aperture': (x_left[-1], x_right[-1]),
        'left_profile': (x_left, y_left),
        'right_profile': (x_right, y_right),
        'efficiency_loss': efficiency_loss,
        'C_actual': C_trunc
    }

def test_cpc_endpoints():
    """
    Automated verification suite ensuring reflector profile boundary points
    connect perfectly with the receiver base and top aperture edge.
    """
    print("=" * 60)
    print("RUNNING CPC PROFILE ENDPOINT VERIFICATION SUITE")
    print("=" * 60)
    
    # Test Parameters
    r_width = 0.5
    theta_c_deg = 12.0
    truncation_pct = 50.0  # Test non-standard conditions
    num_points = 4 # how many points to use for the height of the profiles

    data = generate_and_plot_cpc(r_width=r_width, theta_c_deg=theta_c_deg, truncation_pct=truncation_pct, num_points=num_points)
    
    # Extract calculated coordinates
    x_l, y_l = data['left_profile']
    x_r, y_r = data['right_profile']
    rec_left, rec_right = data['receiver']
    ap_left, ap_right = data['aperture']
    
    # Define acceptable numerical precision error threshold
    tolerance = 1e-4
    
    # Assertions for Left Profile Endpoints
    left_bottom_match = np.allclose([x_l[0], y_l[0]], [rec_left, 0.0], atol=tolerance)
    left_top_match = np.allclose([x_l[-1], y_l[-1]], [ap_left, y_l[-1]], atol=tolerance)
    
    # Assertions for Right Profile Endpoints
    right_bottom_match = np.allclose([x_r[0], y_r[0]], [rec_right, 0.0], atol=tolerance)
    right_top_match = np.allclose([x_r[-1], y_r[-1]], [ap_right, y_r[-1]], atol=tolerance)
    
    print(f"[-] Left Base Connection: Profile ({x_l[0]:.4f}, {y_l[0]:.4f}) vs Receiver ({rec_left:.4f}, 0.0000) -> {'PASSED' if left_bottom_match else 'FAILED'}")
    print(f"[-] Left Top Connection:  Profile ({x_l[-1]:.4f}, {y_l[-1]:.4f}) vs Aperture ({ap_left:.4f}, {y_l[-1]:.4f}) -> {'PASSED' if left_top_match else 'FAILED'}")
    print(f"[-] Right Base Connection: Profile ({x_r[0]:.4f}, {y_r[0]:.4f}) vs Receiver ({rec_right:.4f}, 0.0000) -> {'PASSED' if right_bottom_match else 'FAILED'}")
    print(f"[-] Right Top Connection:  Profile ({x_r[-1]:.4f}, {y_r[-1]:.4f}) vs Aperture ({ap_right:.4f}, {y_r[-1]:.4f}) -> {'PASSED' if right_top_match else 'FAILED'}")
    
    assert left_bottom_match, "Left reflector bottom does not align with left receiver point."
    assert left_top_match, "Left reflector top does not align with left aperture point."
    assert right_bottom_match, "Right reflector bottom does not align with right receiver point."
    assert right_top_match, "Right reflector top does not align with right aperture point."
    
    print("=" * 60)
    print("SUCCESS: All geometric endpoint constraints successfully verified!")
    print("=" * 60)

# --- Function Usage Example ---
if __name__ == "__main__":
    # Example 1: Run the verification test suite (Generates a 85% Truncated Profile)
    test_cpc_endpoints()
    
    # Example 2: Call the function normally for a full un-truncated profile (100% Height)
    # generate_and_plot_cpc(r_width=1.0, theta_c_deg=30.0, truncation_pct=100.0)
