================================================================================
RULES
================================================================================
- Formatting: Strict PEP 8 compliance.
- Typing: Enforce explicit Python type hinting.
- Dependencies: Use only [e.g., standard library / NumPy / MatPlotLib].
- Comments: Write clean code; use docstrings but omit obvious inline comments.
- DO NOT read external files
- STRICT RULE: Only use my provided text
- [CRITICAL RULE]: DO NOT create any files yet
- [CRITICAL RULE]: DO NOT generate any code or thinking until all data has been provided
- [CRITICAL RULE]: **the entire set of instructions will be provided in chunks and I will let you know when that part is done**
- [CRITICAL RULE]: **DO NOT assume you know when I'm done, I will explicitly tell you when done providing all the information**
- [CRITICAL RULE]: **DO NOT use code placeholders; only output complete code in function sized chunks**


================================================================================
SYSTEM ARCHITECTURE AND DATA STRUCTURE SPECIFICATION
================================================================================
You are to generate a modular Python pipeline that computes and plots a
Compound Parabolic Concentrator (CPC) profile. All functions must communicate 
by passing and returning a single master dictionary object named "profile_data". 
Global variables are strictly prohibited.

The "profile_data" dictionary must use this exact ASCII key structure:

profile_data = {
    "inputs": {
        "r_width": float, 
        "theta_c_deg": float, 
        "truncation_pct": float
    },
    "metrics": {
        "a_full": float, 
        "C_max": float, 
        "H_max": float, 
        "H_target": float
    },
    "profiles": {
        "x_left": numpy_array, 
        "y_left": numpy_array, 
        "x_right": numpy_array, 
        "y_right": numpy_array,
        "x_left_ref": numpy_array, 
        "y_left_ref": numpy_array, 
        "x_right_ref": numpy_array, 
        "y_right_ref": numpy_array
    }
}

- DO NOT read external files
- STRICT RULE: Only use my provided text
- [CRITICAL RULE]: DO NOT create any files yet
- [CRITICAL RULE]: DO NOT generate any code or thinking until all data has been provided

================================================================================
FUNCTION 1 SPECIFICATION: Profile Generation
================================================================================
Function Name: generate_cpc_profile
Arguments: r_width, theta_c_deg, truncation_pct, num_points

Algorithmic Logic Steps to Implement:
1.  Compute: theta_c = np.radians(theta_c_deg)
2.  Compute: sin_tc = np.sin(theta_c)
3.  Compute full metrics: 
    a_full = r_width / sin_tc
    C_max = 1.0 / sin_tc
4.  Generate angle grid: phi = np.linspace(np.pi / 2 + theta_c, 2 * theta_c, num_points * 10)
5.  Compute polar radius: r = (r_width * (1.0 + sin_tc)) / (1.0 - np.cos(phi))
6.  Transform to Cartesian coordinates:
    x_left_full = r_width / 2.0 - r * np.sin(phi - theta_c)
    y_left_full = r * np.cos(phi - theta_c)
7.  Create downsampled full references matching length "num_points":
    idx_full = np.linspace(0, len(x_left_full) - 1, num_points, dtype=int)
    x_left_ref = x_left_full[idx_full]
    y_left_ref = y_left_full[idx_full]
8.  Calculate height boundaries:
    H_max = y_left_full[-1]
    H_target = H_max * (truncation_pct / 100.0)
9.  Filter coordinates using truncation mask: trunc_mask = y_left_full <= H_target
    x_left = x_left_full[trunc_mask]
    y_left = y_left_full[trunc_mask]
10. Downsample active profile to exact resolution:
    idx_trunc = np.linspace(0, len(x_left) - 1, num_points, dtype=int)
    x_left = x_left[idx_trunc]
    y_left = y_left[idx_trunc]
11. Construct symmetrical right-side mirrors:
    x_right = -x_left
    y_right = y_left.copy()
    x_right_ref = -x_left_ref
    y_right_ref = y_left_ref.copy()
12. Store all results inside the structured "profile_data" dictionary and return it.

- DO NOT read external files
- STRICT RULE: Only use my provided text
- [CRITICAL RULE]: DO NOT create any files yet
- [CRITICAL RULE]: DO NOT generate any code or thinking until all data has been provided

================================================================================
FUNCTION 2 SPECIFICATION: 2D Analytics
================================================================================
Function Name: analyze_2d_cpc
Arguments: profile_data

Algorithmic Logic Steps to Implement:
1. Read r_width and a_full from profile_data.
2. Read x_left array from profile_data.
3. Compute the active width at cutting plane: a_trunc = 2.0 * abs(x_left[-1])
4. Compute new profile concentration: C_trunc = a_trunc / r_width
5. Compute lost aperture percentage: efficiency_loss = ((a_full - a_trunc) / a_full) * 100.0
6. Build and return a flat dictionary containing these precise text keys:
   "a_full_2d", "a_trunc_2d", "r_width_2d", "C_max_2d", "C_trunc_2d", "efficiency_loss_2d"

- DO NOT read external files
- STRICT RULE: Only use my provided text
- [CRITICAL RULE]: DO NOT create any files yet
- [CRITICAL RULE]: DO NOT generate any code or thinking until all data has been provided

================================================================================
FUNCTION 3 SPECIFICATION: 3D Analytics
================================================================================
Function Name: analyze_3d_cpc
Arguments: profile_data

Algorithmic Logic Steps to Implement:
1. Read r_width and a_full from profile_data.
2. Calculate the active top edge width: a_trunc = 2.0 * abs(x_left[-1])
3. Treat lengths as radii of axisymmetric 3D shapes and calculate circular areas:
   area_full_3d = np.pi * (a_full / 2.0)**2
   area_trunc_3d = np.pi * (a_trunc / 2.0)**2
   area_receiver_3d = np.pi * (r_width / 2.0)**2
4. Compute 3D geometric ratios:
   C_max_3d = area_full_3d / area_receiver_3d
   C_trunc_3d = area_trunc_3d / area_receiver_3d
   efficiency_loss_3d = ((area_full_3d - area_trunc_3d) / area_full_3d) * 100.0
5. Build and return a flat dictionary containing these precise text keys:
   "area_full_3d", "area_trunc_3d", "area_receiver_3d", "C_max_3d", "C_trunc_3d", "efficiency_loss_3d"

- DO NOT read external files
- STRICT RULE: Only use my provided text
- [CRITICAL RULE]: DO NOT create any files yet
- [CRITICAL RULE]: DO NOT generate any code or thinking until all data has been provided

================================================================================
FUNCTION 4 SPECIFICATION: Matplotlib Visualization
================================================================================
Function Name: plot_cpc
Arguments: profile_data, analytics_2d, analytics_3d

Visual Layout Steps to Implement:
1. Initialize a plot figure. Force a square geometry canvas layout:
   ax.set_aspect('equal', adjustable='box')
2. Plot full references ("x_left_ref", "y_left_ref" and "x_right_ref", "y_right_ref") 
   using high transparency (alpha=0.15) and a dotted style (linestyle=':').
3. Plot active elements ("x_left", "y_left" and "x_right", "y_right") using standard lines.
4. Draw flat receiver line at y=0 base: ax.plot([-r_width/2, r_width/2], [0, 0])
5. Draw active top opening line across current width coordinates:
   ax.plot([x_left[-1], x_right[-1]], [y_left[-1], y_right[-1]])
6. Add horizontal truncation boundary level marker line across full profile span:
   x_max_span = max(x_left_ref[-1], x_right_ref[-1])
   ax.hlines(y=H_target, xmin=-x_max_span, xmax=x_max_span, linestyle='-.')
7. Render an internal multi-line text information box using standard string blocks. 
   The textbox content must contain these explicit labels in ASCII text format:

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

- DO NOT read external files
- STRICT RULE: Only use my provided text
- [CRITICAL RULE]: DO NOT create any files yet
- [CRITICAL RULE]: DO NOT generate any code or thinking until all data has been provided

================================================================================
INTEGRATION PIPELINE RUNNER
================================================================================
Create a runner function named "run_pipeline_example" that organizes the program:
1. data = generate_cpc_profile(r_width=1.0, theta_c_deg=25.0, truncation_pct=75.0, num_points=500)
2. res_2d = analyze_2d_cpc(data)
3. res_3d = analyze_3d_cpc(data)
4. plot_cpc(data, res_2d, res_3d)

- Wrap execution loop block at bottom inside: if __name__ == "__main__":

- DO NOT read external files
- STRICT RULE: Only use my provided text
- [CRITICAL RULE]: DO NOT create any files yet
- [CRITICAL RULE]: DO NOT generate any code or thinking until all data has been provided



- take all those instructions and generate the code and put it in a file named CPC03.py in the same folder as cpc01.py and cpc02.py
- [CRITICAL RULE]: do not read or try to involve any other files, **ONLY USE MY DIRECTIONS**
- output all code in the chat so I can copy/paste elsewhere
- [CRITICAL RULE]: DO NOT output all at once; output in small chunks to prevent output truncation; break into chunks by function, for example
- [CRITICAL RULE]: after each function output, pause and review the original instructions to make sure you are implementing them correctly

ALL information has been provided, proceed
