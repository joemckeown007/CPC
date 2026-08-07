import numpy as np
import matplotlib.pyplot as plt
from typing import Dict, Any

def generate_cpc_profile(r_width: float, theta_c_deg: float, truncation_pct: float, num_points: int) -> Dict[str, Any]:
    """
    Generates the Compound Parabolic Concentrator (CPC) profile data.

    Args:
        r_width: The width of the receiver.
        theta_c_deg: The cone angle in degrees.
        truncation_pct: The percentage for truncation.
        num_points: The number of points to use for downsampling references.

    Returns:
        A dictionary containing the structured profile data.
    """
    # 1. Compute: theta_c = np.radians(theta_c_deg)
    theta_c = np.radians(theta_c_deg)
    
    # 2. Compute: sin_tc = np.sin(theta_c)
    sin_tc = np.sin(theta_c)
    
    # 3. Compute full metrics:
    # a_full = r_width / sin_tc
    a_full = r_width / sin_tc
    # C_max = 1.0 / sin_tc
    C_max = 1.0 / sin_tc

    # 4. Generate angle grid: phi = np.linspace(np.pi / 2 + theta_c, 2 * theta_c, num_points * 10)
    phi = np.linspace(np.pi / 2 + theta_c, 2 * theta_c, num_points * 10)

    # 5. Compute polar radius: r = (r_width * (1.0 + sin_tc)) / (1.0 - np.cos(phi))
    r = (r_width * (1.0 + sin_tc)) / (1.0 - np.cos(phi))

    # 6. Transform to Cartesian coordinates:
    # x_left_full = r_width / 2.0 - r * np.sin(phi - theta_c)
    x_left_full = r_width / 2.0 - r * np.sin(phi - theta_c)
    # y_left_full = r * np.cos(phi - theta_c)
    y_left_full = r * np.cos(phi - theta_c)

    # 7. Create downsampled full references matching length "num_points":
    # idx_full = np.linspace(0, len(x_left_full) - 1, num_points, dtype=int)
    idx_full = np.linspace(0, len(x_left_full) - 1, num_points, dtype=int)
    x_left_ref = x_left_full[idx_full]
    y_left_ref = y_left_full[idx_full]

    # 8. Calculate height boundaries:
    # H_max = y_left_full[-1]
    H_max = y_left_full[-1]
    # H_target = H_max * (truncation_pct / 100.0)
    H_target = H_max * (truncation_pct / 100.0)

    # 9. Filter coordinates using truncation mask: trunc_mask = y_left_full <= H_target
    trunc_mask = y_left_full <= H_target
    x_left = x_left_full[trunc_mask]
    y_left = y_left_full[trunc_mask]

    # 10. Downsample active profile to exact resolution:
    # idx_trunc = np.linspace(0, len(x_left) - 1, num_points, dtype=int)
    idx_trunc = np.linspace(0, len(x_left) - 1, num_points, dtype=int)
    x_left = x_left[idx_trunc]
    y_left = y_left[idx_trunc]

    # 11. Construct symmetrical right-side mirrors:
    # x_right = -x_left
    x_right = -x_left
    # y_right = y_left.copy()
    y_right = y_left.copy()
    # x_right_ref = -x_left_ref
    x_right_ref = -x_left_ref
    # y_right_ref = y_left_ref.copy()
    y_right_ref = y_left_ref.copy()

    # 12. Store all results inside the structured "profile_data" dictionary and return it.
    profile_data = {
        "inputs": {
            "r_width": r_width,
            "theta_c_deg": theta_c_deg,
            "truncation_pct": truncation_pct
        },
        "metrics": {
            "a_full": a_full,
            "C_max": C_max,
            "H_max": H_max,
            "H_target": H_target
        },
        "profiles": {
            "x_left": x_left,
            "y_left": y_left,
            "x_right": x_right,
            "y_right": y_right,
            "x_left_ref": x_left_ref,
            "y_left_ref": y_left_ref,
            "x_right_ref": x_right_ref,
            "y_right_ref": y_right_ref
        }
    }
    return profile_data

def analyze_2d_cpc(profile_data: Dict[str, Any]) -> Dict[str, float]:
    """
    Analyzes the 2D profile data to compute 2D metrics.

    Args:
        profile_data: The master dictionary containing CPC profile data.

    Returns:
        A flat dictionary with 2D analytical results.
    """
    # 1. Read r_width and a_full from profile_data.
    r_width = profile_data["inputs"]["r_width"]
    a_full = profile_data["metrics"]["a_full"]
    
    # 2. Read x_left array from profile_data.
    x_left = profile_data["profiles"]["x_left"]

    # 3. Compute the active width at cutting plane: a_trunc = 2.0 * abs(x_left[-1])
    a_trunc = 2.0 * np.abs(x_left[-1])

    # 4. Compute new profile concentration: C_trunc = a_trunc / r_width
    C_trunc = a_trunc / r_width

    # 5. Compute lost aperture percentage: efficiency_loss = ((a_full - a_trunc) / a_full) * 100.0
    efficiency_loss = ((a_full - a_trunc) / a_full) * 100.0

    # 6. Build and return a flat dictionary containing these precise text keys:
    return {
        "a_full_2d": a_full,
        "a_trunc_2d": a_trunc,
        "r_width_2d": r_width,
        "C_max_2d": profile_data["metrics"]["C_max"],
        "C_trunc_2d": C_trunc,
        "efficiency_loss_2d": efficiency_loss
    }

def analyze_3d_cpc(profile_data: Dict[str, Any]) -> Dict[str, float]:
    """
    Analyzes the 3D profile data to compute 3D geometric ratios.

    Args:
        profile_data: The master dictionary containing CPC profile data.

    Returns:
        A flat dictionary with 3D analytical results.
    """
    # 1. Read r_width and a_full from profile_data.
    r_width = profile_data["inputs"]["r_width"]
    a_full = profile_data["metrics"]["a_full"]
    x_left = profile_data["profiles"]["x_left"]

    # 2. Calculate the active top edge width: a_trunc = 2.0 * abs(x_left[-1])
    a_trunc = 2.0 * np.abs(x_left[-1])

    # 3. Treat lengths as radii of axisymmetric 3D shapes and calculate circular areas:
    # area_full_3d = np.pi * (a_full / 2.0)**2
    area_full_3d = np.pi * (a_full / 2.0)**2
    # area_trunc_3d = np.pi * (a_trunc / 2.0)**2
    area_trunc_3d = np.pi * (a_trunc / 2.0)**2
    # area_receiver_3d = np.pi * (r_width / 2.0)**2
    area_receiver_3d = np.pi * (r_width / 2.0)**2

    # 4. Compute 3D geometric ratios:
    # C_max_3d = area_full_3d / area_receiver_3d
    C_max_3d = area_full_3d / area_receiver_3d
    # C_trunc_3d = area_trunc_3d / area_receiver_3d
    C_trunc_3d = area_trunc_3d / area_receiver_3d
    # efficiency_loss_3d = ((area_full_3d - area_trunc_3d) / area_full_3d) * 100.0
    efficiency_loss_3d = ((area_full_3d - area_trunc_3d) / area_full_3d) * 100.0

    # 5. Build and return a flat dictionary containing these precise text keys:
    return {
        "area_full_3d": area_full_3d,
        "area_trunc_3d": area_trunc_3d,
        "area_receiver_3d": area_receiver_3d,
        "C_max_3d": C_max_3d,
        "C_trunc_3d": C_trunc_3d,
        "efficiency_loss_3d": efficiency_loss_3d
    }

def plot_cpc(profile_data: Dict[str, Any], analytics_2d: Dict[str, float], analytics_3d: Dict[str, float]) -> None:
    """
    Plots the Compound Parabolic Concentrator (CPC) profile and analytical results.

    Args:
        profile_data: The master dictionary containing CPC profile data.
        analytics_2d: Dictionary containing 2D analysis results.
        analytics_3d: Dictionary containing 3D analysis results.
    """
    fig, ax = plt.subplots()

    # Extract necessary data for plotting and text box
    r_width = profile_data["inputs"]["r_width"]
    theta_c_deg = profile_data["inputs"]["theta_c_deg"]
    H_target = profile_data["metrics"]["H_target"]
    x_left = profile_data["profiles"]["x_left"]
    y_left = profile_data["profiles"]["y_left"]
    x_right = profile_data["profiles"]["x_right"]
    y_right = profile_data["profiles"]["y_right"]
    x_left_ref = profile_data["profiles"]["x_left_ref"]
    y_left_ref = profile_data["profiles"]["y_left_ref"]
    x_right_ref = profile_data["profiles"]["x_right_ref"]
    y_right_ref = profile_data["profiles"]["y_right_ref"]

    # 2. Plot full references ("x_left_ref", "y_left_ref" and "x_right_ref", "y_right_ref")
    ax.plot(x_left_ref, y_left_ref, linestyle=':', alpha=0.15)
    ax.plot(x_right_ref, y_right_ref, linestyle=':', alpha=0.15)

    # 3. Plot active elements ("x_left", "y_left" and "x_right", "y_right") using standard lines.
    ax.plot(x_left, y_left)
    ax.plot(x_right, y_right)

    # 4. Draw flat receiver line at y=0 base: ax.plot([-r_width/2, r_width/2], [0, 0])
    ax.plot([-r_width / 2, r_width / 2], [0, 0])

    # 5. Draw active top opening line across current width coordinates:
    ax.plot([x_left[-1], x_right[-1]], [y_left[-1], y_right[-1]])

    # 6. Add horizontal truncation boundary level marker line across full profile span:
    x_max_span = max(x_left_ref[-1], x_right_ref[-1])
    ax.hlines(y=H_target, xmin=-x_max_span, xmax=x_max_span, linestyle='-.')

    # 7. Render an internal multi-line text information box using dynamic values.
    info_text = f"""
Receiver Width: {r_width:.4f}
Acceptance Angle (deg): {theta_c_deg:.2f}
Max Design Height: {profile_data['metrics']['H_max']:.4f}
Actual Profile Height (Truncated): {profile_data['metrics']['H_target']:.4f}

2D Full Aperture Width: {analytics_2d['a_full_2d']:.4f}
2D Truncated Aperture Width: {analytics_2d['a_trunc_2d']:.4f}
2D Receiver Width: {r_width:.4f}
2D Max Concentration Ratio: {analytics_2d['C_max_2d']:.4f}
2D Actual Concentration Ratio: {analytics_2d['C_trunc_2d']:.4f}
2D Efficiency Loss: {analytics_2d['efficiency_loss_2d']:.2f}%

3D Full Aperture Area: {analytics_3d['area_full_3d']:.4f}
3D Truncated Aperture Area: {analytics_3d['area_trunc_3d']:.4f}
2D Receiver Area: {np.pi * (r_width / 2.0)**2:.4f}
3D Max Concentration Ratio: {analytics_3d['C_max_3d']:.4f}
3D Actual Concentration Ratio: {analytics_3d['C_trunc_3d']:.4f}
3D Efficiency Loss: {analytics_3d['efficiency_loss_3d']:.2f}%
"""

    # Place the text box in a visible area, e.g., top left corner
    ax.text(0.05, 0.95, info_text.strip(), transform=ax.transAxes, fontsize=10, verticalalignment='top', bbox=dict(boxstyle="round,pad=0.5", fc="white", alpha=0.7))

    plt.title("CPC Profile Visualization")
    plt.xlabel("X Coordinate")
    plt.ylabel("Y Coordinate")
    plt.grid(True)
    plt.show()


def xplot_cpc(profile_data: Dict[str, Any], analytics_2d: Dict[str, float], analytics_3d: Dict[str, float]) -> None:
    """
    Plots the Compound Parabolic Concentrator (CPC) profile and analytical results.

    Args:
        profile_data: The master dictionary containing CPC profile data.
        analytics_2d: Dictionary containing 2D analysis results.
        analytics_3d: Dictionary containing 3D analysis results.
    """
    fig, ax = plt.subplots()

    # 1. Initialize a plot figure. Force a square geometry canvas layout:
    ax.set_aspect('equal', adjustable='box')

    # Extract necessary data for plotting and text box
    r_width = profile_data["inputs"]["r_width"]
    H_target = profile_data["metrics"]["H_target"]
    x_left = profile_data["profiles"]["x_left"]
    y_left = profile_data["profiles"]["y_left"]
    x_right = profile_data["profiles"]["x_right"]
    y_right = profile_data["profiles"]["y_right"]
    x_left_ref = profile_data["profiles"]["x_left_ref"]
    y_left_ref = profile_data["profiles"]["y_left_ref"]
    x_right_ref = profile_data["profiles"]["x_right_ref"]
    y_right_ref = profile_data["profiles"]["y_right_ref"]

    # 2. Plot full references ("x_left_ref", "y_left_ref" and "x_right_ref", "y_right_ref")
    ax.plot(x_left_ref, y_left_ref, linestyle=':', alpha=0.15)
    ax.plot(x_right_ref, y_right_ref, linestyle=':', alpha=0.15)

    # 3. Plot active elements ("x_left", "y_left" and "x_right", "y_right") using standard lines.
    ax.plot(x_left, y_left)
    ax.plot(x_right, y_right)

    # 4. Draw flat receiver line at y=0 base: ax.plot([-r_width/2, r_width/2], [0, 0])
    ax.plot([-r_width / 2, r_width / 2], [0, 0])

    # 5. Draw active top opening line across current width coordinates:
    ax.plot([x_left[-1], x_right[-1]], [y_left[-1], y_right[-1]])

    # 6. Add horizontal truncation boundary level marker line across full profile span:
    x_max_span = max(x_left_ref[-1], x_right_ref[-1])
    ax.hlines(y=H_target, xmin=-x_max_span, xmax=x_max_span, linestyle='-.')

    # 7. Render an internal multi-line text information box using standard string blocks.
    info_text = f"""
Receiver Width
Acceptance Angle
Max Design Height
Actual Profile Height

2D Full Aperture Width
2D Truncated Aperture Width
2D Receiver Width
2D Max Concentration Ratio
2D Actual Concentration Ratio
2D Efficiency Loss

3D Full Aperture Area
3D Truncated Aperture Area
2D Receiver Area
3D Max Concentration Ratio
3D Actual Concentration Ratio
3D Efficiency Loss
"""
    # Place the text box in a visible area, e.g., top left corner
    ax.text(0.05, 0.95, info_text.strip(), transform=ax.transAxes, fontsize=10, verticalalignment='top', bbox=dict(boxstyle="round,pad=0.5", fc="white", alpha=0.7))

    plt.title("CPC Profile Visualization")
    plt.xlabel("X Coordinate")
    plt.ylabel("Y Coordinate")
    plt.grid(True)
    plt.show()

def run_pipeline_example():
    """
    Organizes and runs the full CPC pipeline example.
    """
    # 1. data = generate_cpc_profile(r_width=1.0, theta_c_deg=25.0, truncation_pct=75.0, num_points=500)
    data = generate_cpc_profile(r_width=0.5, theta_c_deg=12.0, truncation_pct=50.0, num_points=10)
    
    # 2. res_2d = analyze_2d_cpc(data)
    res_2d = analyze_2d_cpc(data)
    
    # 3. res_3d = analyze_3d_cpc(data)
    res_3d = analyze_3d_cpc(data)
    
    # 4. plot_cpc(data, res_2d, res_3d)
    plot_cpc(data, res_2d, res_3d)

if __name__ == "__main__":
    run_pipeline_example()