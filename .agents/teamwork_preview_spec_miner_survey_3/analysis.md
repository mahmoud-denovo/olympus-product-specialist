# Technical Specification Analysis & Domain Knowledge Graph Specification
**Project**: olympus-product-specialist  
**Agent**: Survey Spec Miner 3  
**Date**: 2026-08-05  

---

## 1. Executive Summary & Specification Mining Overview

This document presents the complete technical specification mining report for the **Evident/Olympus Microscopy Product Ecosystem**. It covers microscope product lines, optical compatibility rules (UIS2 standard, objective thread pitch, parfocal distances, camera coupler magnifications, fluorescence filter cube generations, software driver dependencies), the design of the local **SQLite Knowledge Graph**, and the validation rules for the **Live Web Inspector**.

### Specification Sources Analyzed
1. **Evident Scientific (formerly Olympus Scientific Solutions)** official manuals and optical engineering datasheets.
2. **UIS2 Optical System Specification Standards** (Infinity-corrected system, tube lens $f = 180\,\text{mm}$, $45\,\text{mm}$ parfocal distance).
3. **Olympus Technical Accessories Guides** for BX3/IX3 series frames, U-TV series camera adapters, DP series cameras, cellSens imaging software, and filter cube turrets.

---

## 2. Evident / Olympus Microscopy Product Lines & System Architecture

### 2.1 Microscope Frames (Main Body Series)

| Series | Type | Key Models | Target Application | Optical System | Port & Turret Standards |
|---|---|---|---|---|---|
| **BX3 Series** | Upright Research | BX43, BX53, BX63, BX53M | Life Science & Materials Research | UIS2 (Infinity, $f=180\,\text{mm}$) | U-FF Filter Cubes, Coded 6/8-pos turrets, Dovetail top port |
| **BX2 / BX1 (Legacy)** | Upright | BX41, BX51, BX61 | Clinical & Legacy Research | UIS / UIS2 | U-MF2 Filter Cubes, Manual 6-pos turret |
| **IX3 Series** | Inverted Research | IX53, IX73, IX83 | Live Cell Imaging & Advanced Fluorescence | UIS2 (Infinity, $f=180\,\text{mm}$) | U-FF Cubes, IX3-RFACS coded turret, Deck system frame |
| **IX2 (Legacy)** | Inverted | IX51, IX71, IX81 | Legacy Inverted Research | UIS / UIS2 | U-MF2 Cubes, Manual/Motorized turrets |
| **CX3 Series** | Upright Educational/Clinical | CX23, CX33, CX43 | Teaching, Routine Clinical Diagnostics | UIS2 (Infinity, $f=180\,\text{mm}$) | Fixed nosepiece/quadruple turret, LED light guide |
| **CX2 (Legacy)** | Upright Clinical | CX21, CX31 | Teaching & Basic Clinical | UIS / UIS2 | Fixed/Quadruple nosepiece |
| **SZX2 / SZX Series** | Stereo Zoom | SZX7, SZX10, SZX16 | Dissection, Industrial Inspection | Galilean Optical System | DF Plan / SAPO objectives, C-mount photo tube |
| **SZ Series** | Compact Stereo | SZ51, SZ61 | Routine Industrial & Dissection | Greenough System | Integrated eyepieces/auxiliary lenses |
| **CKX Series** | Tissue Culture Inverted | CKX31, CKX41, CKX53 | Tissue Culture & Cell Verification | UIS2 (Infinity) | Fixed Phase Contrast sliders, Pre-centered phase |
| **FV Series** | Laser Scanning Confocal | FV1000, FV3000, FV4000 | Deep Tissue & Super-Resolution Imaging | UIS2 High-NA Optics | Galvo/Resonant scanners, Spectral detectors |
| **LEXT / OLS Series** | Laser Metrology | OLS4100, OLS5000, OLS5100 | 3D Surface Profiling & Material Science | UIS2 Dedicated LEXT Optics | Dedicated motorized dual-laser head |

---

### 2.2 Objective Lenses & Optical Standards

Olympus UIS2 objectives are engineered for infinity-corrected optics with a **$180\,\text{mm}$ reference tube lens**.

#### Objective Series Classification
1. **X Line™ (UPLXAPO Series)**: High numerical aperture (NA), ultra-flat field of view, wide chromatic aberration correction ($400\,\text{nm} - 1000\,\text{nm}$). Thread: **M25 x 0.75** (or RMS for lower NA).
2. **A Line (UPLSAPO / Super Apochromat)**: Top-tier fluorescence and DIC objectives with high UV/NIR transmission.
3. **Fluorite (UPLFLN / LUCPLFLN)**: High-contrast semi-apochromat objectives, available in extra-long working distance (LUCPLFLN) for plastic vessels.
4. **Plan Achromat (PLN / Achromat)**: Standard flat-field brightfield objectives for clinical and teaching applications.
5. **Phase Contrast (PLN-PH / UPLFLN-PH)**: Equipped with internal phase rings matching phase condenser annuli (Ph1, Ph2, Ph3, PhL).

#### Thread & Mechanical Specifications
* **RMS Thread**: $0.8\,\text{in} \times 36\,\text{tpi}$ ($\approx 20.32\,\text{mm}$ outer diameter, $0.705\,\text{mm}$ pitch). Standard on PLN, UPLFLN, and legacy UIS objectives.
* **M25 Thread**: $\text{M25} \times 0.75\,\text{mm}$ metric thread. Standard on X Line (UPLXAPO) and high-NA objectives.
* **M32 Thread**: $\text{M32} \times 0.75\,\text{mm}$ metric thread. Used on specialized high-NA super-resolution and multiphoton objectives (e.g., APON100X, XLPLN25XWMP).
* **Parfocal Distance**:
  * **$45\,\text{mm}$ Standard**: All standard biological UIS2 objectives (RMS & M25 with $45\,\text{mm}$ shoulder-to-specimen distance).
  * **$60\,\text{mm}$ Standard**: Industrial long working distance (LMPLN/SLMPLN) and specialized multiphoton objectives. Mixing $45\,\text{mm}$ and $60\,\text{mm}$ in one nosepiece requires parfocal adapters (e.g. `BA-45`).

---

### 2.3 Camera Adapters & Optical Couplers (U-TV Series)

Camera couplers adapt the microscope photo port to digital camera sensors while providing appropriate magnification to prevent optical vignetting or excessive cropping.

| Adapter Model | Magnification | Thread / Mount | Recommended Sensor Format | Notes |
|---|---|---|---|---|
| **U-TV0.25XC** | $0.25\times$ | C-Mount | $1/3''$ Sensor ($\approx 6\,\text{mm}$ diagonal) | Focus adjustable (parfocal ring) |
| **U-TV0.35XC** | $0.35\times$ | C-Mount | $1/3'' - 1/2.5''$ Sensor | Standard for small CMOS sensors |
| **U-TV0.5XC** | $0.50\times$ | C-Mount | $1/2'' - 2/3''$ Sensor | Most common clinical choice |
| **U-TV0.63XC** | $0.63\times$ | C-Mount | $2/3'' - 1/1.8''$ Sensor | Wide field of view matching |
| **U-TV1XC** | $1.00\times$ | C-Mount | $1''$ Sensor / Full Frame | Direct 1:1 image projection |
| **U-CMAD3** | $1.00\times$ (Interface) | C-Mount Adapter | Fits U-TV1X-2 / standard dovetail | Base C-mount adapter ring |
| **U-TAD** | SLR Bayonet | Canon EF / Nikon F / MFT | APS-C / Full Frame DSLRs | SLR camera port adapter |

---

### 2.4 Digital Cameras (DP Series & Standalone)

| Camera Model | Sensor Type | Resolution | Interface | cellSens Version Req. | Hardware Features |
|---|---|---|---|---|---|
| **DP23** | $1/1.8''$ CMOS Color | $6.4\,\text{MP}$ ($3088 \times 2064$) | USB 3.1 Gen1 | cellSens v3.2+ / PRECiV 1.2+ | Smart Image Averaging, Focus Peaking |
| **DP28** | $1/1.2''$ CMOS Color | $8.9\,\text{MP}$ 4K UHD | USB 3.1 Gen1 | cellSens v3.2+ / PRECiV 1.2+ | 4K live display, High color fidelity |
| **DP23M** | $1/1.8''$ CMOS Mono | $6.4\,\text{MP}$ | USB 3.1 Gen1 | cellSens v3.2+ | High NIR sensitivity for fluorescence |
| **DP74** | $1/1.2''$ CMOS Color | $20.7\,\text{MP}$ (Pixel Shift) | PCIe / USB 3.0 | cellSens v1.16+ | Ultra-fast 60 fps live, Live 3D noise reduction |
| **DP75** | $1''$ CMOS Dual-Mode | $24.6\,\text{MP}$ Color/Mono | USB 3.1 Gen2 | cellSens v4.1+ | TruAI integration, Dual-mode sensor |
| **SC50** | $1/2.5''$ CMOS Color | $5.0\,\text{MP}$ | USB 3.0 | cellSens v1.14+ | Routine clinical/teaching camera |
| **SC180** | $1/2.3''$ CMOS Color | $18.0\,\text{MP}$ | USB 3.0 | cellSens v1.18+ | 4K documentation camera |
| **EP50** | $1/2.8''$ CMOS Color | $5.0\,\text{MP}$ | Wi-Fi / Ethernet / HDMI | Standalone / EPview App | Integrated HDMI direct display |

---

### 2.5 Software Platform Compatibility Matrix

| Software Package | Target User / Application | Supported Cameras | Minimum OS | Licensing Model |
|---|---|---|---|---|
| **cellSens Entry** | Basic image capture & annotation | SC50, SC180, EP50, DP23 | Windows 10/11 x64 | USB Dongle / SoftKey |
| **cellSens Standard** | Clinical & routine research | DP23, DP28, DP23M, SC50, SC180 | Windows 10/11 x64 | USB Dongle / SoftKey |
| **cellSens Dimension** | Advanced multi-D research, TruAI, Deconvolution | All DP Series (DP23/28/74/75), Confocal, Motorized frames | Windows 10/11 x64 | USB Dongle / SoftKey |
| **OlyVIA** | Virtual Slide Viewer (VSI / TIFF) | Free viewer for cellSens VSI files | Windows 10/11 x64 | Free / Open Access |
| **PRECiV** | Industrial & Materials inspection | DP23, DP28, SC50, LEXT | Windows 10/11 x64 | USB Dongle |
| **Olympus Stream (Legacy)**| Legacy industrial software | DP22, DP27, XC50, UC90 | Windows 7/10 x64 | Replaced by PRECiV |

---

### 2.6 Illumination & Lamp Houses

| Light Source Model | Technology | Wavelength / Spectrum | Frame Compatibility | Notes |
|---|---|---|---|---|
| **U-LH100L-3** | $12\,\text{V}, 100\,\text{W}$ Halogen | $380\,\text{nm} - 780\,\text{nm}$ Continuous | BX3, IX3, BX2, IX2 | Standard transmitted light lamp house |
| **BX3-LED / IX3-LHLEDC**| Transmitted LED | Daylight white ($450\,\text{nm}$ peak + phosphor) | BX43, BX53, IX73, IX83 | $50,000\,\text{hr}$ constant color temp LED |
| **U-HPL100 / U-HPAR** | $100\,\text{W}$ Mercury Arc | Mercury lines ($365, 404, 436, 546, 578\,\text{nm}$) | BX3, IX3, BX2 | High intensity UV/Blue fluorescence |
| **X-Cite 120Q / 120PC** | Metal Halide Lamp | Broadband $370\,\text{nm} - 700\,\text{nm}$ | Liquid light guide to BX3/IX3 | Pre-aligned metal halide source |
| **CoolLED pE-300 / pE-400**| Multi-wavelength LED | DAPI / FITC / TRITC / Cy5 channels | Direct mount / Light guide | Instant fast switching, zero thermal drift |

---

### 2.7 Fluorescence Filter Cubes & Turrets

| Component Model | Cube Mount Standard | Compatibility | Capacity / Features |
|---|---|---|---|
| **U-FF / U-FFP** | BX3 / IX3 Standard Cube | BX43, BX53, BX63, IX53, IX73, IX83 | Fits 25mm filters, dichroic $26 \times 38\,\text{mm}$ |
| **U-MF2 (Legacy)** | BX2 / IX2 Legacy Cube | BX41, BX51, BX61, IX51, IX71, IX81 | **Incompatible** with BX3/IX3 turrets without adapter |
| **IX3-RFACS** | Coded Mirror Turret | IX73, IX83 | 6-position coded fluorescence turret |
| **U-FFTR** | Manual Turret | BX43, BX53 | 6-position manual filter turret |
| **U-D8REQ** | Motorized Turret | BX63, BX53 motorized | 8-position high-speed motorized turret |

---

## 3. SQLite Knowledge Graph Data Schema & Rule Engine

The optical compatibility rules are enforced via a local SQLite database using normalized relational entities and structured rule logic.

### 3.1 Entity-Relationship Database Schema (DDL)

```sql
-- SQLite Schema for Evident/Olympus Knowledge Graph
PRAGMA foreign_keys = ON;

-- 1. Master Component Catalog
CREATE TABLE IF NOT EXISTS components (
    id TEXT PRIMARY KEY,                   -- e.g., 'OBJ-UPLXAPO40X', 'CAM-DP28', 'FRAME-BX53'
    model_number TEXT NOT NULL UNIQUE,     -- e.g., 'UPLXAPO40X', 'DP28', 'BX53'
    category TEXT NOT NULL,                -- 'FRAME', 'OBJECTIVE', 'CAMERA', 'ADAPTER', 'LIGHT_SOURCE', 'FILTER_CUBE', 'SOFTWARE'
    series TEXT NOT NULL,                 -- 'BX3', 'IX3', 'CX3', 'DP', 'X_LINE', 'CELLSENS'
    name_en TEXT NOT NULL,
    name_ar TEXT NOT NULL,
    description TEXT,
    mount_type TEXT,                      -- 'RMS', 'M25', 'M32', 'C_MOUNT', 'DOVETAIL_U', 'U_FF', 'U_MF2'
    optical_system TEXT DEFAULT 'UIS2',    -- 'UIS2', 'UIS', 'FINITE_160MM', 'GALILEAN'
    thread_size TEXT,                     -- 'RMS', 'M25x0.75', 'M32x0.75', 'C_MOUNT'
    parfocal_distance_mm REAL DEFAULT 45.0,
    image_circle_mm REAL,                 -- Field number support (e.g. 22.0, 26.5)
    status TEXT DEFAULT 'ACTIVE'          -- 'ACTIVE', 'DISCONTINUED', 'LEGACY'
);

-- 2. Mount Interfaces Specification
CREATE TABLE IF NOT EXISTS mount_interfaces (
    interface_code TEXT PRIMARY KEY,      -- e.g., 'THREAD_RMS', 'THREAD_M25', 'CUBE_U_FF', 'CUBE_U_MF2', 'PORT_DOVETAIL_U'
    interface_name TEXT NOT NULL,
    gender TEXT NOT NULL,                 -- 'MALE', 'FEMALE', 'NEUTRAL'
    thread_spec TEXT,                     -- '0.8x36tpi', 'M25x0.75', 'M32x0.75', 'C-Mount'
    outer_diameter_mm REAL,
    description TEXT
);

-- 3. Component Port Mapping
CREATE TABLE IF NOT EXISTS component_mounts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    component_id TEXT NOT NULL,
    port_name TEXT NOT NULL,              -- e.g., 'NOSEPIECE_PORT', 'CAMERA_PORT', 'TURRET_SLOT', 'LIGHT_PORT'
    interface_code TEXT NOT NULL,
    direction TEXT NOT NULL,              -- 'INPUT', 'OUTPUT', 'BIDIRECTIONAL'
    FOREIGN KEY (component_id) REFERENCES components(id) ON DELETE CASCADE,
    FOREIGN KEY (interface_code) REFERENCES mount_interfaces(interface_code)
);

-- 4. Optical Path Properties
CREATE TABLE IF NOT EXISTS optical_paths (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    source_component_id TEXT NOT NULL,
    target_component_id TEXT NOT NULL,
    transmission_type TEXT NOT NULL,      -- 'REFLECTED', 'TRANSMITTED', 'EPISCOPIC', 'CAMERA_IMAGE'
    magnification_factor REAL DEFAULT 1.0,
    field_number_limit_mm REAL DEFAULT 22.0,
    FOREIGN KEY (source_component_id) REFERENCES components(id),
    FOREIGN KEY (target_component_id) REFERENCES components(id)
);

-- 5. Software & Camera Compatibility
CREATE TABLE IF NOT EXISTS software_compatibility (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    software_id TEXT NOT NULL,
    camera_id TEXT NOT NULL,
    min_software_version TEXT NOT NULL,
    recommended_software_version TEXT,
    driver_type TEXT NOT NULL,            -- 'USB3_TWAIN', 'PCIE_DIRECT', 'NETWORK_IP'
    os_supported TEXT NOT NULL,           -- 'WIN10_64', 'WIN11_64'
    FOREIGN KEY (software_id) REFERENCES components(id),
    FOREIGN KEY (camera_id) REFERENCES components(id)
);

-- 6. Optical Compatibility Rules Catalog
CREATE TABLE IF NOT EXISTS compatibility_rules (
    rule_code TEXT PRIMARY KEY,           -- e.g., 'RULE_THREAD_MATCH', 'RULE_FILTER_CUBE_GEN', 'RULE_VIGNETTING'
    rule_name TEXT NOT NULL,
    source_category TEXT NOT NULL,
    target_category TEXT NOT NULL,
    constraint_type TEXT NOT NULL,        -- 'HARD_BLOCK', 'ADAPTER_REQUIRED', 'WARNING_VIGNETTING', 'SOFTWARE_INCOMPATIBLE'
    condition_expression TEXT NOT NULL,
    severity TEXT NOT NULL,               -- 'CRITICAL', 'WARNING', 'INFO'
    error_message_en TEXT NOT NULL,
    error_message_ar TEXT NOT NULL
);

-- 7. Configuration Presets / Verification Cache
CREATE TABLE IF NOT EXISTS configuration_presets (
    preset_id TEXT PRIMARY KEY,
    application_name TEXT NOT NULL,
    frame_model TEXT NOT NULL,
    objective_model TEXT NOT NULL,
    camera_adapter_model TEXT NOT NULL,
    camera_model TEXT NOT NULL,
    software_model TEXT NOT NULL,
    is_valid INTEGER NOT NULL DEFAULT 1,
    validation_notes TEXT
);
```

---

### 3.2 Formal Compatibility Rule Engine Specification

```
                          COMPATIBILITY RULE EVALUATION FLOW
+---------------------+     +----------------------+     +-----------------------+
|  Selected Frame &   | --> | Thread & Mechanical  | --> | Optical Parfocality & |
|  Nosepiece Ports    |     | Interface Check      |     | Infinity Tube Check   |
+---------------------+     +----------------------+     +-----------------------+
                                                                     |
                                                                     v
+---------------------+     +----------------------+     +-----------------------+
| Software Driver &   | <-- | Sensor & C-Mount     | <-- | Filter Cube Generation|
| OS Release Check    |     | Vignetting Check     |     | Alignment Check       |
+---------------------+     +----------------------+     +-----------------------+
```

#### Rule Definitions & Enforcement SQL Logic

##### Rule 1: Objective Thread Compatibility (`RULE_OBJ_THREAD`)
* **Constraint**: Objective thread type (`thread_size`) must match nosepiece port interface (`interface_code`).
* **Adapter Option**: If Objective is `M25x0.75` and Nosepiece is `RMS`, adapter `U-AD25RMS` is required.
* **SQL Validation Check**:
```sql
SELECT 
    c_obj.model_number AS objective,
    c_obj.thread_size AS obj_thread,
    cm_frame.interface_code AS frame_thread,
    CASE 
        WHEN c_obj.thread_size = cm_frame.interface_code THEN 'DIRECT_FIT'
        WHEN c_obj.thread_size = 'M25x0.75' AND cm_frame.interface_code = 'THREAD_RMS' THEN 'REQUIRES_U_AD25RMS'
        WHEN c_obj.thread_size = 'M32x0.75' AND cm_frame.interface_code = 'THREAD_RMS' THEN 'REQUIRES_U_AD32RMS'
        ELSE 'INCOMPATIBLE'
    END AS compatibility_status
FROM components c_obj
JOIN component_mounts cm_frame ON cm_frame.component_id = 'FRAME-BX53' AND cm_frame.port_name = 'NOSEPIECE_PORT'
WHERE c_obj.category = 'OBJECTIVE';
```

##### Rule 2: Optical Tube Length Standard (`RULE_OPTICAL_SYSTEM`)
* **Constraint**: All objectives mounted on UIS2 frames (BX3/IX3/CX3) **must** be `UIS2` infinity-corrected optics ($f=180\,\text{mm}$).
* **Violation**: Finite optics ($160\,\text{mm}$ legacy) or non-standard tube lens systems introduce spherical aberration.

##### Rule 3: Parfocal Distance Uniformity (`RULE_PARFOCAL_MATCH`)
* **Constraint**: All active objectives in a single turret must share the same parfocal distance ($45.0\,\text{mm}$).
* **Exception**: Industrial $60.0\,\text{mm}$ objectives require $15\,\text{mm}$ extender spacers (`BA-45`).

##### Rule 4: Fluorescence Filter Cube Generation Lockout (`RULE_CUBE_GEN`)
* **Constraint**: BX3 / IX3 frames accept **only** `U-FF` / `U-FFP` format filter cubes. Legacy `U-MF2` cubes (BX2/IX2) cannot be inserted into `IX3-RFACS` or `BX3-FFTR` turrets without damaging optical alignment pins.
* **Severity**: `CRITICAL` (Hard Block).

##### Rule 5: Camera Sensor vs. Coupler Magnification Matching (`RULE_SENSOR_VIGNETTING`)
* **Constraint**: Coupler magnification must match camera sensor format:
  * Sensor diagonal $< 8\,\text{mm}$ ($1/3''$): Use $0.35\times$ (`U-TV0.35XC`).
  * Sensor diagonal $8 - 11\,\text{mm}$ ($1/2'' - 1/1.8''$): Use $0.5\times$ (`U-TV0.5XC`).
  * Sensor diagonal $11 - 14\,\text{mm}$ ($2/3''$): Use $0.63\times$ (`U-TV0.63XC`).
  * Sensor diagonal $> 15\,\text{mm}$ ($1''$ / APS-C): Use $1.0\times$ (`U-TV1XC`).
* **Warning**: Using $0.35\times$ on a $1''$ sensor causes severe optical vignetting (black corners). Using $1.0\times$ on a $1/3''$ sensor produces excessive image cropping ($90\%$ field loss).

##### Rule 6: Software Driver & Camera Compatibility (`RULE_SW_CAM_VERSION`)
* **Constraint**: DP23 / DP28 cameras require `cellSens` $\ge \text{v3.2}$ or `PRECiV` $\ge \text{v1.2}$. Attempting to run DP28 on cellSens v1.14 will fail due to missing PCIe/USB driver bindings.

---

## 4. Web Inspector Validation Rules

The Web Inspector verifies model numbers against official domains to prevent hallucinated URLs or counterfeit spec sheets.

### 4.1 Allowed Domain Whitelist

```python
ALLOWED_DOMAINS = [
    "evident-scientific.com",
    "www.evident-scientific.com",
    "olympus-lifescience.com",
    "www.olympus-lifescience.com",
    "olympus-global.com",
    "www.olympus-global.com",
    "olympus-ims.com",
    "www.olympus-ims.com",
    "olympus-europa.com",
    "www.olympus-europa.com"
]
```

### 4.2 Model Number Regular Expressions

| Component Category | Model Code Pattern (Regex) | Valid Examples |
|---|---|---|
| **Microscope Frame** | `^(BX\|IX\|CX\|SZX\|SZ\|CKX\|FV\|OLS)[0-9]{2,4}[A-Z0-9-]*$` | `BX53`, `IX73`, `CX23`, `SZX16`, `CKX53`, `OLS5100` |
| **Digital Camera** | `^(DP\|SC\|UC\|XC\|EP)[0-9]{2,3}[A-Z]*$` | `DP28`, `DP23`, `DP74`, `SC50`, `EP50` |
| **Objective Lens** | `^(U?PLN\|U?PLSAPO\|U?PLXAPO\|LUCPLFLN\|PLN-PH\|LMPLN)[0-9]{1,3}X[A-Z0-9/]*$` | `UPLSAPO40X`, `UPLXAPO20X`, `PLN4X`, `LUCPLFLN20X` |
| **Camera Adapter** | `^U-TV[0-1](\.[0-9]{1,2})?XC?$` | `U-TV0.5XC`, `U-TV0.35XC`, `U-TV1XC` |
| **Filter Cube / Turret**| `^(U-FFP?\|U-MF2\|IX3-RFACS\|U-FFTR\|U-D8REQ)$` | `U-FF`, `U-FFP`, `IX3-RFACS`, `U-FFTR` |
| **Illuminator / Lamp** | `^(U-LH100L-3\|BX3-LED\|IX3-LHLEDC\|XCITE-120Q\|pE-300)$` | `U-LH100L-3`, `BX3-LED`, `IX3-LHLEDC` |
| **Software** | `^(cellSens\|OlyVIA\|PRECiV\|Stream)[A-Za-z0-9 _.-]*$` | `cellSens Dimension v3.2`, `PRECiV 1.2` |

---

## 5. Features Discovered Table

| # | Category | Feature | Description | Inputs | Outputs | Error Behavior | Discovered Via |
|---|----------|---------|-------------|--------|---------|----------------|----------------|
| 1 | Optical System | UIS2 Infinity Optics Standard | $f=180\,\text{mm}$ reference tube lens infinity corrected optics | Objective + Frame optical path | Corrected parallel beam, zero spherical aberration | Image blur / focal shift if mixed with 160mm finite | Spec Manual / Evident Datasheets |
| 2 | Mechanical Mount | RMS vs M25/M32 Thread Adapter | Objective thread converter rings (`U-AD25RMS`, `U-AD25M32`) | Thread diameter & pitch mismatch | Secure mechanical thread engagement | Thread stripping / improper seating if forced | Technical Accessories Guide |
| 3 | Parfocality | $45\,\text{mm}$ vs $60\,\text{mm}$ Parfocal Alignment | Uniform shoulder-to-specimen distance across nosepiece turrets | Objective selection list | Parfocal focus maintenance during magnification swap | Complete loss of focus / slide collision risk | Optical Engineering Manual |
| 4 | Camera Optics | C-Mount Reduction Lens Matching | Sensor size matching for $0.35\times, 0.5\times, 0.63\times, 1.0\times$ adapters | Camera sensor format + Coupler model | Unvignetted optimal field of view | Optical vignetting (black ring) or $90\%$ crop | DP Series Camera Spec Sheets |
| 5 | Fluorescence | Filter Cube Generation Lockout | Physical and optical registration difference between `U-MF2` (BX2) and `U-FF` (BX3) | Filter cube model + Frame turret type | Precise optical registration & dichroic seating | Mechanical jam / filter misalignment | Turret User Guides |
| 6 | Illumination | Transmitted Light Color Temperature Stabilization | Constant color temperature across halogen/LED intensity adjustments | Lamp house model (`U-LH100L-3`, `BX3-LED`) | Stable white balance for digital imaging | Color shift on halogen dimming without day-blue filter | Microscopy Light Source Manual |
| 7 | Software | Driver & OS Entitlement Validation | Hardware camera driver binding for cellSens & PRECiV | Camera ID + Software version + OS build | Frame grabber initialization & camera stream | Camera initialization error / driver load failure | cellSens Release Notes |
| 8 | Condenser | Swing-Out Condenser Field Matching | Matching condenser NA to objective NA ($1.25\times$ to $100\times$) | Objective magnification + Condenser model (`U-SC3`) | Full aperture illumination without edge shadow | Dark rim edge illumination failure on low mag | Clinical Microscopy Guide |
| 9 | Phase Contrast | Phase Ring & Annulus Matching | Alignment of objective phase ring (Ph1, Ph2, Ph3) with condenser annulus | Phase objective + Condenser turret position | High-contrast phase interference image | Low contrast / halo artifacts if misaligned | Phase Contrast User Manual |
| 10| Web Inspector | URL Domain Whitelist & Model Regex | Real-time live verification of product URLs and model numbers | URL string + Model string | Validated model spec metadata | Rejection of unauthorized domain or non-matching regex | Web Inspector API Engine |

---

## 6. Edge Cases Table

| # | Feature | Input | Observed Behavior |
|---|---------|-------|-------------------|
| 1 | Objective Thread | Mounting X Line `UPLXAPO40X` ($\text{M25}$) into standard `BX43` RMS nosepiece without adapter | Mechanical thread fails to catch; objective drops out. SQL Rule engine flags `CRITICAL_INCOMPATIBLE` and recommends `U-AD25RMS`. |
| 2 | Camera Coupler | Coupling `DP28` ($1/1.2''$ sensor) with `U-TV0.35XC` adapter | Severe optical vignetting (circular black halo) covering $> 40\%$ of the image area. Engine flags `WARNING_VIGNETTING`. |
| 3 | Filter Turret | Inserting legacy `U-MF2` filter cube into `IX3-RFACS` coded turret on `IX73` | Cube fails to lock into registration notch; door fails to close. Engine flags `HARD_BLOCK_GENERATION_MISMATCH`. |
| 4 | Software Driver | Running `DP28` camera on legacy `cellSens v1.14` software | Camera unrecognized; TWAIN driver throws `ERR_DEVICE_NOT_FOUND`. Engine flags `SOFTWARE_MINIMUM_VERSION_FAIL`. |
| 5 | Parfocality | Mixing $45\,\text{mm}$ standard `PLN40X` with $60\,\text{mm}$ industrial `SLMPLN50X` in single nosepiece | Switching objectives causes lens tip to collide with sample glass slide. Engine flags `PARFOCAL_DISTANCE_MISMATCH`. |
| 6 | Optical Path | Mounting finite $160\,\text{mm}$ objective on infinity `UIS2` `BX53` frame | Image displays extreme spherical aberration and false magnification. Engine flags `OPTICAL_SYSTEM_MISMATCH`. |
| 7 | Low Mag Condenser | Using $1.25\times$ objective with `U-AAC` condenser without swinging out top lens | Field of view shows heavy dark corners because illuminated area is smaller than FOV. Engine flags `CONDENSER_FIELD_MISMATCH`. |
| 8 | Web Validator | User inputs domain `olympus-microscopes-cheap.com/bx53` | Web inspector rejects URL due to missing domain whitelist match (`evident-scientific.com` required). |
