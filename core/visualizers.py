"""
Next-generation sci-fi HUD visualizers for JARVIS HUD.
Engineered for Tony Stark / Avengers holographic caliber, 60 FPS performance,
high kinetic momentum, and rich acoustic reactivity.
"""
from __future__ import annotations

import math
import random
from typing import List, Tuple

import numpy as np
from PyQt6.QtCore import QLineF, QPointF, QRectF, Qt
from PyQt6.QtGui import (
    QBrush,
    QColor,
    QFont,
    QPainter,
    QPainterPath,
    QPen,
    QPolygonF,
    QRadialGradient,
    QLinearGradient,
)


def _blend(bg: QColor, col: QColor, a: float) -> QColor:
    """Pre-mix color onto background for fast opaque rendering."""
    f = max(0.0, min(1.0, a))
    return QColor(
        int(bg.red() + (col.red() - bg.red()) * f),
        int(bg.green() + (col.green() - bg.green()) * f),
        int(bg.blue() + (col.blue() - bg.blue()) * f),
    )


def _c(col: QColor, a: float) -> QColor:
    """Return color copy with alpha clamped 0..255."""
    q = QColor(col)
    q.setAlpha(int(max(0.0, min(255.0, a))))
    return q


def _lerp_col(c1: QColor, c2: QColor, t: float) -> QColor:
    """Linearly interpolate between two colors."""
    f = max(0.0, min(1.0, t))
    return QColor(
        int(c1.red() + (c2.red() - c1.red()) * f),
        int(c1.green() + (c2.green() - c1.green()) * f),
        int(c1.blue() + (c2.blue() - c1.blue()) * f),
        int(c1.alpha() + (c2.alpha() - c1.alpha()) * f),
    )


# =============================================================================
# 1. ARC REACTOR MK-VII (Canonical Tony Stark Holographic Core - Benchmark)
# =============================================================================

class ArcReactorVisualizer:
    """Tony Stark Arc Reactor core with triple gimbals, coils & pulsating bloom."""

    def __init__(self) -> None:
        self.phase = 0.0
        self.pulse = 0.0

    def step(self, dt: float, amp: float, speaking: bool, state: str = "IDLE", muted: bool = False) -> None:
        speed = 1.0 + (2.2 if state in ("THINKING", "PROCESSING") else 0.0) + (1.5 if speaking else 0.0)
        self.phase += dt * speed
        target_pulse = amp if not muted else 0.0
        self.pulse += (target_pulse - self.pulse) * min(1.0, dt * 12.0)

    def paint(self, p: QPainter, cx: float, cy: float, r: float, primary: QColor, accent: QColor, bg: QColor) -> None:
        p.save()
        p.setRenderHint(QPainter.RenderHint.Antialiasing, True)
        t = self.phase
        amp = self.pulse

        # 1. Radial Atmospheric Bloom
        core_r = r * (0.35 + 0.15 * amp)
        grad = QRadialGradient(cx, cy, r * 1.3)
        grad.setColorAt(0.0, _c(accent, 160 + 85 * amp))
        grad.setColorAt(0.3, _c(primary, 60 + 40 * amp))
        grad.setColorAt(0.7, _c(primary, 15))
        grad.setColorAt(1.0, _c(bg, 0))
        p.setPen(Qt.PenStyle.NoPen)
        p.setBrush(QBrush(grad))
        p.drawEllipse(QPointF(cx, cy), r * 1.3, r * 1.3)

        # 2. Concentric Gimbals & Rotating Arcs
        p.setBrush(Qt.BrushStyle.NoBrush)
        rings = [
            (r * 0.98, 70, 3, 1.0, primary, 1.6),
            (r * 0.85, 45, 4, -1.3, accent, 1.3),
            (r * 0.68, 120, 2, 1.8, primary, 1.8),
            (r * 0.52, 90, 3, -2.4, accent, 2.0),
        ]
        for rad, span, segs, dirn, col, thick in rings:
            p.setPen(QPen(_blend(bg, col, 0.45 + 0.35 * amp), thick))
            box = QRectF(cx - rad, cy - rad, rad * 2, rad * 2)
            base_ang = (t * 22.0 * dirn) % 360.0
            for i in range(segs):
                ang = int((base_ang + i * (360.0 / segs)) * 16)
                p.drawArc(box, ang, int(span * 16))

        # 3. 72 Precision Graduation Ticks
        lines = []
        for i in range(72):
            ang = math.radians(i * 5.0 + t * 4.0)
            ca, sa = math.cos(ang), math.sin(ang)
            is_maj = (i % 6 == 0)
            in_r = r * (0.88 if is_maj else 0.93)
            out_r = r * 0.98
            lines.append(QLineF(cx + ca * in_r, cy + sa * in_r, cx + ca * out_r, cy + sa * out_r))
        p.setPen(QPen(_blend(bg, primary, 0.40 + 0.3 * amp), 1.2))
        p.drawLines(lines)

        # 4. 10 Toroidal Inductor Coils
        num_coils = 10
        coil_r = r * 0.44
        coil_len = r * 0.12
        for i in range(num_coils):
            ang = math.radians(i * (360.0 / num_coils) + t * 6.0)
            ca, sa = math.cos(ang), math.sin(ang)
            active = 0.5 + 0.5 * math.sin(t * 7.0 + i * 1.2)
            col = _blend(primary, accent, active)
            p.setPen(QPen(_blend(bg, col, 0.5 + 0.5 * active * amp), 3.0))
            p.drawLine(QLineF(cx + ca * (coil_r - coil_len / 2), cy + sa * (coil_r - coil_len / 2),
                             cx + ca * (coil_r + coil_len / 2), cy + sa * (coil_r + coil_len / 2)))

        # 5. Core Fusion Center (Palladium Ring + Core Star)
        p.setPen(QPen(_blend(bg, accent, 0.85), 2.0))
        p.drawEllipse(QPointF(cx, cy), core_r, core_r)
        core_grad = QRadialGradient(cx, cy, core_r)
        core_grad.setColorAt(0.0, _c(QColor(255, 255, 255), 230 + 25 * amp))
        core_grad.setColorAt(0.4, _c(accent, 190 + 50 * amp))
        core_grad.setColorAt(1.0, _c(bg, 20))
        p.setBrush(QBrush(core_grad))
        p.setPen(Qt.PenStyle.NoPen)
        p.drawEllipse(QPointF(cx, cy), core_r * 0.75, core_r * 0.75)

        # 6. Laser Audio Needles on speech
        if amp > 0.05:
            spikes = []
            for i in range(32):
                ang = math.radians(i * (360.0 / 32) - t * 12.0)
                ca, sa = math.cos(ang), math.sin(ang)
                h = r * 0.18 * amp * (0.5 + 0.5 * math.sin(t * 15.0 + i))
                spikes.append(QLineF(cx + ca * core_r, cy + sa * core_r,
                                     cx + ca * (core_r + h), cy + sa * (core_r + h)))
            p.setPen(QPen(_blend(bg, accent, 0.8), 1.5))
            p.drawLines(spikes)

        p.restore()


# =============================================================================
# 2. QUANTUM NEURAL SPHERE (F.R.I.D.A.Y. Geodesic Core - UPGRADED & RINGS REMOVED)
# =============================================================================

class QuantumSphereVisualizer:
    """
    F.R.I.D.A.Y. 3D Geodesic Neural Lattice with traveling synaptic impulses,
    dynamic volumetric audio surface ripples, 3D latitude/longitude coordinate calipers,
    and quantum singularity core (clunky tilted rings completely removed!).
    """

    def __init__(self) -> None:
        self.phase = 0.0
        self.rot = [0.25, 0.0, 0.15]
        self.amp = 0.0

        phi = (1.0 + math.sqrt(5.0)) / 2.0
        base_v = [
            (-1, phi, 0), (1, phi, 0), (-1, -phi, 0), (1, -phi, 0),
            (0, -1, phi), (0, 1, phi), (0, -1, -phi), (0, 1, -phi),
            (phi, 0, -1), (phi, 0, 1), (-phi, 0, -1), (-phi, 0, 1),
        ]
        base_v = [np.array(v, dtype=np.float32) / math.sqrt(1 + phi * phi) for v in base_v]

        faces = [
            (0, 11, 5), (0, 5, 1), (0, 1, 7), (0, 7, 10), (0, 10, 11),
            (1, 5, 9), (5, 11, 4), (11, 10, 2), (10, 7, 6), (7, 1, 8),
            (3, 9, 4), (3, 4, 2), (3, 2, 6), (3, 6, 8), (3, 8, 9),
            (4, 9, 5), (2, 4, 11), (6, 2, 10), (8, 6, 7), (9, 8, 1),
        ]

        mid_cache = {}
        all_verts = list(base_v)

        def get_mid(i1: int, i2: int) -> int:
            k = (min(i1, i2), max(i1, i2))
            if k in mid_cache:
                return mid_cache[k]
            vm = (all_verts[i1] + all_verts[i2]) * 0.5
            vm = vm / np.linalg.norm(vm)
            idx = len(all_verts)
            all_verts.append(vm)
            mid_cache[k] = idx
            return idx

        edges_set = set()
        for i1, i2, i3 in faces:
            m12 = get_mid(i1, i2)
            m23 = get_mid(i2, i3)
            m31 = get_mid(i3, i1)
            for a, b in [
                (i1, m12), (m12, i2), (i2, m23), (m23, i3),
                (i3, m31), (m31, i1), (m12, m23), (m23, m31), (m31, m12)
            ]:
                edge = (min(a, b), max(a, b))
                edges_set.add(edge)

        self.v0 = np.array(all_verts, dtype=np.float32)
        self.edges = list(edges_set)

        # 24 active synaptic action potential impulses
        self.pulses: List[List[float]] = []
        for _ in range(24):
            e_idx = random.randint(0, len(self.edges) - 1)
            self.pulses.append([float(e_idx), random.random(), random.uniform(0.9, 2.0), 1.0])

        # Floating ambient quantum spark particles around the sphere
        self.sparks = []
        for _ in range(32):
            self.sparks.append([
                random.uniform(0.0, math.pi * 2),
                random.uniform(-math.pi / 2, math.pi / 2),
                random.uniform(0.95, 1.15),
                random.uniform(0.4, 1.2),
            ])

    def step(self, dt: float, amp: float, speaking: bool, state: str = "IDLE", muted: bool = False) -> None:
        speed = 0.9 + (2.2 if state in ("THINKING", "PROCESSING") else 0.0) + (1.5 if speaking else 0.0)
        self.phase += dt * speed
        self.rot[0] += dt * 0.40 * speed
        self.rot[1] += dt * 0.60 * speed
        self.rot[2] += dt * 0.25 * speed

        target = amp if not muted else 0.0
        self.amp += (target - self.amp) * min(1.0, dt * 14.0)

        # Advance synaptic impulses
        pulse_speed_mult = 1.0 + (3.2 if speaking else 0.0) + (2.0 if state in ("THINKING", "PROCESSING") else 0.0)
        for p in self.pulses:
            p[1] += dt * p[2] * pulse_speed_mult
            if p[1] >= 1.0:
                p[1] = 0.0
                p[0] = float(random.randint(0, len(self.edges) - 1))

        # Orbit ambient sparks
        for sp in self.sparks:
            sp[0] += dt * sp[3] * 0.8 * speed

    def paint(self, p: QPainter, cx: float, cy: float, r: float, primary: QColor, accent: QColor, bg: QColor) -> None:
        p.save()
        p.setRenderHint(QPainter.RenderHint.Antialiasing, True)
        t = self.phase
        amp = self.amp
        scale = r * (0.75 + 0.16 * amp)

        # 1. Outer Holographic Quantum Atmosphere Bloom
        grad = QRadialGradient(cx, cy, r * 1.3)
        grad.setColorAt(0.0, _c(accent, 160 + 85 * amp))
        grad.setColorAt(0.35, _c(primary, 60 + 40 * amp))
        grad.setColorAt(0.75, _c(primary, 15))
        grad.setColorAt(1.0, _c(bg, 0))
        p.setPen(Qt.PenStyle.NoPen)
        p.setBrush(QBrush(grad))
        p.drawEllipse(QPointF(cx, cy), r * 1.3, r * 1.3)

        # 2. 3D Rotation Matrix Calculation
        rx, ry, rz = self.rot
        cx_c, sx_s = math.cos(rx), math.sin(rx)
        cy_c, sy_s = math.cos(ry), math.sin(ry)
        cz_c, sz_s = math.cos(rz), math.sin(rz)

        pts_2d = []
        depths = []
        for x, y, z in self.v0:
            # Volumetric acoustic surface wave displacement (rippling energy shield)
            wave1 = math.sin(t * 7.0 + x * 3.0 + y * 2.5 + z * 2.0)
            wave2 = math.sin(t * 14.0 + x * 5.0 - y * 4.0) * 0.4
            disp = 1.0 + 0.22 * amp * (wave1 + wave2)
            x1, y1, z1 = x * disp, y * disp, z * disp

            x2 = x1 * cy_c + z1 * sy_s
            z2 = -x1 * sy_s + z1 * cy_c
            y3 = y1 * cx_c - z2 * sx_s
            z3 = y1 * sx_s + z2 * cx_c
            x4 = x2 * cz_c - y3 * sz_s
            y4 = x2 * sz_s + y3 * cz_c

            fov = 2.8 / (2.8 - z3 * 0.42)
            px = cx + x4 * scale * fov
            py = cy - y4 * scale * fov
            pts_2d.append((px, py))
            depths.append(z3)

        # 3. Draw Backside Geodesic Edges (Depth z < 0)
        p.setBrush(Qt.BrushStyle.NoBrush)
        for i, j in self.edges:
            avg_z = (depths[i] + depths[j]) * 0.5
            if avg_z < 0.0:
                norm_z = (avg_z + 1.2) / 2.4
                alpha = max(0.12, min(0.35, norm_z * 0.35 + 0.1 * amp))
                p.setPen(QPen(_blend(bg, primary, alpha), 1.0))
                p.drawLine(QPointF(pts_2d[i][0], pts_2d[i][1]), QPointF(pts_2d[j][0], pts_2d[j][1]))

        # 4. Central Quantum Singularity Core
        core_r = r * (0.26 + 0.14 * amp)
        core_grad = QRadialGradient(cx, cy, core_r)
        core_grad.setColorAt(0.0, _c(QColor(255, 255, 255), 245))
        core_grad.setColorAt(0.35, _c(accent, 195 + 55 * amp))
        core_grad.setColorAt(0.70, _c(primary, 85 + 40 * amp))
        core_grad.setColorAt(1.0, _c(bg, 0))
        p.setPen(Qt.PenStyle.NoPen)
        p.setBrush(QBrush(core_grad))
        p.drawEllipse(QPointF(cx, cy), core_r, core_r)

        # 5. Draw Frontside Geodesic Edges (Depth z >= 0)
        p.setBrush(Qt.BrushStyle.NoBrush)
        for i, j in self.edges:
            avg_z = (depths[i] + depths[j]) * 0.5
            if avg_z >= 0.0:
                norm_z = (avg_z + 1.2) / 2.4
                alpha = max(0.40, min(0.98, norm_z * 0.85 + 0.25 * amp))
                col = _blend(primary, accent, norm_z)
                p.setPen(QPen(_blend(bg, col, alpha), 1.3 + 1.6 * norm_z))
                p.drawLine(QPointF(pts_2d[i][0], pts_2d[i][1]), QPointF(pts_2d[j][0], pts_2d[j][1]))

        # 6. Active Traveling Synaptic Impulses (Action Potentials)
        for edge_idx, progress, _, _ in self.pulses:
            idx = int(edge_idx) % len(self.edges)
            i, j = self.edges[idx]
            avg_z = (depths[i] + depths[j]) * 0.5
            if avg_z > -0.2:
                x1, y1 = pts_2d[i]
                x2, y2 = pts_2d[j]
                pulse_x = x1 + (x2 - x1) * progress
                pulse_y = y1 + (y2 - y1) * progress
                pulse_r = 2.4 + 2.6 * amp
                p.setPen(Qt.PenStyle.NoPen)
                p.setBrush(QBrush(_blend(bg, QColor(255, 255, 255), 0.95)))
                p.drawEllipse(QPointF(pulse_x, pulse_y), pulse_r, pulse_r)

        # 7. Draw Geodesic Nodes (Front facing with glow halo)
        for i, (px, py) in enumerate(pts_2d):
            z = depths[i]
            if z > -0.4:
                norm_z = (z + 1.2) / 2.4
                node_r = 2.0 + 3.0 * norm_z + 2.2 * amp
                p.setPen(Qt.PenStyle.NoPen)
                p.setBrush(QBrush(_blend(bg, accent, 0.45 + 0.55 * norm_z)))
                p.drawEllipse(QPointF(px, py), node_r, node_r)
                if z > 0.4:
                    p.setBrush(QBrush(_c(QColor(255, 255, 255), 235)))
                    p.drawEllipse(QPointF(px, py), node_r * 0.45, node_r * 0.45)

        # 8. Floating Ambient Quantum Sparks in 3D Space
        for theta, phi_ang, r_dist, _ in self.sparks:
            # Convert spherical to 3D Cartesian
            sx = r_dist * math.cos(phi_ang) * math.cos(theta)
            sy = r_dist * math.sin(phi_ang)
            sz = r_dist * math.cos(phi_ang) * math.sin(theta)

            # Apply 3D rotation
            sx2 = sx * cy_c + sz * sy_s
            sz2 = -sx * sy_s + sz * cy_c
            sy3 = sy * cx_c - sz2 * sx_s
            sz3 = sy * sx_s + sz2 * cx_c
            sx4 = sx2 * cz_c - sy3 * sz_s
            sy4 = sx2 * sz_s + sy3 * cz_c

            if sz3 > -0.3:
                sp_fov = 2.8 / (2.8 - sz3 * 0.42)
                sp_px = cx + sx4 * scale * sp_fov
                sp_py = cy - sy4 * scale * sp_fov
                sp_alpha = 0.5 + 0.5 * sz3
                p.setBrush(QBrush(_blend(bg, QColor(255, 255, 255), sp_alpha)))
                p.drawEllipse(QPointF(sp_px, sp_py), 1.8 + amp * 1.5, 1.8 + amp * 1.5)

        # 9. Outer Corner Tactical Reticles (No bottom text line!)
        p.setBrush(Qt.BrushStyle.NoBrush)
        bracket_len = r * 0.18
        br_r = r * 0.98
        p.setPen(QPen(_blend(bg, primary, 0.45 + 0.35 * amp), 1.5))
        for sx, sy in ((-1, -1), (1, -1), (-1, 1), (1, 1)):
            bx = cx + sx * br_r
            by = cy + sy * br_r
            p.drawLine(QLineF(bx, by, bx - sx * bracket_len, by))
            p.drawLine(QLineF(bx, by, bx, by - sy * bracket_len))

        p.restore()


# =============================================================================
# 3. CYBERNETIC VECTOR IRIS (E.D.I.T.H. Holographic Vector Diaphragm - REMADE)
# =============================================================================

class CyberIrisVisualizer:
    """
    E.D.I.T.H. Holographic Vector Aperture Diaphragm.
    Solid orange wedges removed! Replaced with sleek concentric vector shutter rings,
    laser-etched telemetry tracks, translucent sapphire/amber holographic glass sheens,
    360° circular equalizer, and live dual-trace oscilloscope beam.
    """

    def __init__(self) -> None:
        self.phase = 0.0
        self.amp = 0.0
        self.peak_bars = [0.0] * 72

    def step(self, dt: float, amp: float, speaking: bool, state: str = "IDLE", muted: bool = False) -> None:
        speed = 1.0 + (2.2 if state in ("THINKING", "PROCESSING") else 0.0) + (1.4 if speaking else 0.0)
        self.phase += dt * speed
        target = amp if not muted else 0.0
        self.amp += (target - self.amp) * min(1.0, dt * 14.0)

        for i in range(72):
            w = 0.5 + 0.5 * math.sin(self.phase * 8.0 + i * 0.35)
            cur = self.amp * w
            if cur > self.peak_bars[i]:
                self.peak_bars[i] = cur
            else:
                self.peak_bars[i] = max(0.0, self.peak_bars[i] - dt * 0.8)

    def paint(self, p: QPainter, cx: float, cy: float, r: float, primary: QColor, accent: QColor, bg: QColor) -> None:
        p.save()
        p.setRenderHint(QPainter.RenderHint.Antialiasing, True)
        t = self.phase
        amp = self.amp

        # 1. Outer Atmospheric Tactical Bloom
        grad = QRadialGradient(cx, cy, r * 1.25)
        grad.setColorAt(0.0, _c(primary, 130 + 80 * amp))
        grad.setColorAt(0.4, _c(accent, 45 + 35 * amp))
        grad.setColorAt(0.8, _c(primary, 10))
        grad.setColorAt(1.0, _c(bg, 0))
        p.setPen(Qt.PenStyle.NoPen)
        p.setBrush(QBrush(grad))
        p.drawEllipse(QPointF(cx, cy), r * 1.25, r * 1.25)

        # 2. Outer Heavy Titanium Chassis Ring & Azimuth Marks
        p.setBrush(Qt.BrushStyle.NoBrush)
        p.setPen(QPen(_blend(bg, primary, 0.4), 1.8))
        p.drawEllipse(QPointF(cx, cy), r * 0.98, r * 0.98)
        p.drawEllipse(QPointF(cx, cy), r * 0.76, r * 0.76)

        ticks = []
        for i in range(72):
            ang = math.radians(i * 5.0 + t * 2.0)
            ca, sa = math.cos(ang), math.sin(ang)
            is_cardinal = (i % 18 == 0)
            in_r = r * (0.91 if is_cardinal else 0.95)
            ticks.append(QLineF(cx + ca * in_r, cy + sa * in_r, cx + ca * r * 0.98, cy + sa * r * 0.98))
        p.setPen(QPen(_blend(bg, primary, 0.40 + 0.3 * amp), 1.2))
        p.drawLines(ticks)

        # 3. 360° Circular Equalizer Corona with Peak Hold Dots
        eq_base_r = r * 0.76
        eq_max_h = r * 0.17
        bar_lines = []
        peak_dots = []
        for i in range(72):
            ang = math.radians(i * (360.0 / 72) - t * 4.0)
            ca, sa = math.cos(ang), math.sin(ang)
            wave = 0.5 + 0.5 * math.sin(t * 9.0 + i * 0.45)
            h = eq_max_h * (0.15 + 0.85 * amp * wave)
            bar_lines.append(QLineF(cx + ca * eq_base_r, cy + sa * eq_base_r,
                                    cx + ca * (eq_base_r + h), cy + sa * (eq_base_r + h)))

            pk_h = eq_max_h * (0.15 + 0.85 * self.peak_bars[i])
            peak_dots.append(QPointF(cx + ca * (eq_base_r + pk_h + 2.0), cy + sa * (eq_base_r + pk_h + 2.0)))

        p.setPen(QPen(_blend(bg, accent, 0.65 + 0.35 * amp), 1.6))
        p.drawLines(bar_lines)

        p.setPen(Qt.PenStyle.NoPen)
        p.setBrush(QBrush(_blend(bg, QColor(255, 255, 255), 0.85)))
        for pt in peak_dots:
            p.drawEllipse(pt, 1.5, 1.5)

        # 4. HOLOGRAPHIC VECTOR APERTURE DIAPHRAGM (NO SOLID ORANGE WEDGES!)
        # Rendered as multi-tiered concentric holographic vector shutter rings with glowing circuit tracks
        outer_iris_r = r * 0.74
        aperture_r = outer_iris_r * (0.24 + 0.44 * amp)

        # Translucent holographic glass diaphragm background
        p.setBrush(QBrush(_c(primary, int((0.10 + 0.12 * amp) * 255))))
        p.setPen(Qt.PenStyle.NoPen)
        p.drawEllipse(QPointF(cx, cy), outer_iris_r, outer_iris_r)

        # Concentric rotating vector gear and calibration tracks
        p.setBrush(Qt.BrushStyle.NoBrush)
        p.setPen(QPen(_blend(bg, primary, 0.45 + 0.35 * amp), 1.2))
        p.drawEllipse(QPointF(cx, cy), outer_iris_r * 0.90, outer_iris_r * 0.90)
        p.drawEllipse(QPointF(cx, cy), outer_iris_r * 0.72, outer_iris_r * 0.72)

        # Rotating servo gear notches
        gear_ticks = []
        for g_i in range(36):
            ang_g = math.radians(g_i * 10.0 + t * 6.0)
            cg, sg = math.cos(ang_g), math.sin(ang_g)
            gear_ticks.append(QLineF(cx + cg * outer_iris_r * 0.86, cy + sg * outer_iris_r * 0.86,
                                     cx + cg * outer_iris_r * 0.90, cy + sg * outer_iris_r * 0.90))
        p.setPen(QPen(_blend(bg, accent, 0.55 + 0.35 * amp), 1.2))
        p.drawLines(gear_ticks)

        # 12 Curved Holographic Shutter Calipers (Glowing wireframe vector lines & translucent glass sheens)
        num_blades = 12
        for i in range(num_blades):
            ang_pivot = math.radians(i * (360.0 / num_blades) - t * 1.8)
            ang_rim_end = math.radians((i + 1) * (360.0 / num_blades) - t * 1.8)
            ang_inner = ang_pivot + math.radians(45.0)

            p_pivot = QPointF(cx + math.cos(ang_pivot) * outer_iris_r, cy + math.sin(ang_pivot) * outer_iris_r)
            p_rim = QPointF(cx + math.cos(ang_rim_end) * outer_iris_r, cy + math.sin(ang_rim_end) * outer_iris_r)
            p_inner = QPointF(cx + math.cos(ang_inner) * aperture_r, cy + math.sin(ang_inner) * aperture_r)

            path = QPainterPath()
            path.moveTo(p_pivot)
            path.lineTo(p_rim)
            cp = QPointF(cx + math.cos(ang_pivot + math.radians(25.0)) * (outer_iris_r + aperture_r) * 0.5,
                         cy + math.sin(ang_pivot + math.radians(25.0)) * (outer_iris_r + aperture_r) * 0.5)
            path.quadTo(cp, p_inner)
            path.closeSubpath()

            # Translucent holographic sheen (subtle gradient, NOT solid color)
            blade_sheen = _lerp_col(primary, accent, (i % 3) * 0.35)
            p.setBrush(QBrush(_c(blade_sheen, int((0.08 + 0.10 * amp) * 255))))
            p.setPen(QPen(_blend(bg, primary, 0.60 + 0.30 * amp), 1.3))
            p.drawPath(path)

            # Luminous pivot rivet node
            p.setPen(Qt.PenStyle.NoPen)
            p.setBrush(QBrush(_blend(bg, accent, 0.85)))
            p.drawEllipse(p_pivot, 2.0, 2.0)

            # Glowing inner tangent caliper bead
            p.setBrush(QBrush(_blend(bg, QColor(255, 255, 255), 0.90)))
            p.drawEllipse(p_inner, 1.8, 1.8)

        # 5. Multi-Coated Optical Lens Core (Revealed through aperture)
        lens_grad = QRadialGradient(cx, cy, aperture_r)
        lens_grad.setColorAt(0.0, _c(QColor(255, 255, 255), 235 + 20 * amp))
        lens_grad.setColorAt(0.4, _c(accent, 185 + 50 * amp))
        lens_grad.setColorAt(0.85, _c(primary, 90 + 40 * amp))
        lens_grad.setColorAt(1.0, _c(bg, 0))
        p.setPen(Qt.PenStyle.NoPen)
        p.setBrush(QBrush(lens_grad))
        p.drawEllipse(QPointF(cx, cy), aperture_r, aperture_r)

        # Concentric glass reticle rings
        p.setBrush(Qt.BrushStyle.NoBrush)
        p.setPen(QPen(_blend(bg, accent, 0.50 + 0.4 * amp), 1.3))
        p.drawEllipse(QPointF(cx, cy), aperture_r * 0.72, aperture_r * 0.72)
        p.drawEllipse(QPointF(cx, cy), aperture_r * 0.38, aperture_r * 0.38)

        # 6. Tactical Audio Oscilloscope Scanning Beam
        beam_w = aperture_r * 1.5
        beam_pts = []
        num_beam_pts = 32
        for step in range(num_beam_pts):
            frac = (step / (num_beam_pts - 1)) * 2.0 - 1.0
            bx = cx + frac * (beam_w * 0.5)
            wave1 = math.sin(t * 18.0 + frac * 5.0)
            wave2 = math.sin(t * 36.0 + frac * 11.0) * 0.3
            by = cy + (wave1 + wave2) * (aperture_r * 0.35 * amp)
            beam_pts.append(QPointF(bx, by))

        p.setPen(QPen(_blend(bg, QColor(255, 255, 255), 0.95), 1.8))
        p.drawPolyline(beam_pts)

        # 7. Tactical Targeting Crosshairs
        cross_len = aperture_r * 0.25
        p.setPen(QPen(_blend(bg, primary, 0.70), 1.3))
        p.drawLine(QLineF(cx - cross_len, cy, cx + cross_len, cy))
        p.drawLine(QLineF(cx, cy - cross_len, cx, cy + cross_len))

        # (No bottom telemetry text line!)
        p.restore()


# =============================================================================
# 4. STARK ORBITAL TACTICAL RADAR (Replaces Chronos Tesseract completely)
# =============================================================================

class TacticalRadarVisualizer:
    """
    Stark Holographic Orbital Tactical Radar & Global Satellite Defense Grid.
    Features 3D rotating planetary wireframe globe, active sweeping radar beam with
    phosphor persistence, orbital defense satellites leaving plasma trails,
    acoustic sonar burst rings, and tactical target acquisition reticles.
    """

    def __init__(self) -> None:
        self.phase = 0.0
        self.amp = 0.0
        self.sweep_angle = 0.0

        # Satellites on orbital planes: (radius, speed, angle, tilt_deg, color_type)
        self.satellites = [
            [0.72, 1.2, 0.0, 25.0, 0],
            [0.85, -0.9, 1.5, -40.0, 1],
            [0.96, 0.7, 3.2, 60.0, 0],
            [0.60, -1.5, 4.8, -15.0, 1],
            [0.80, 1.1, 2.1, 75.0, 0],
        ]

        # Target acquisition blips that ping on radar
        self.targets = [
            [0.55, 0.8, 1.0],
            [0.78, 2.4, 0.8],
            [0.42, 4.2, 0.9],
            [0.68, 5.5, 0.7],
        ]

    def step(self, dt: float, amp: float, speaking: bool, state: str = "IDLE", muted: bool = False) -> None:
        speed = 1.0 + (2.0 if state in ("THINKING", "PROCESSING") else 0.0) + (1.4 if speaking else 0.0)
        self.phase += dt * speed
        self.sweep_angle = (self.sweep_angle + dt * 140.0 * speed) % 360.0

        target = amp if not muted else 0.0
        self.amp += (target - self.amp) * min(1.0, dt * 14.0)

        # Update satellites
        for sat in self.satellites:
            sat[2] = (sat[2] + dt * sat[1] * speed) % (math.pi * 2.0)

    def paint(self, p: QPainter, cx: float, cy: float, r: float, primary: QColor, accent: QColor, bg: QColor) -> None:
        p.save()
        p.setRenderHint(QPainter.RenderHint.Antialiasing, True)
        t = self.phase
        amp = self.amp

        # 1. Radial Atmospheric Tactical Radar Glow
        grad = QRadialGradient(cx, cy, r * 1.25)
        grad.setColorAt(0.0, _c(primary, 130 + 80 * amp))
        grad.setColorAt(0.35, _c(accent, 45 + 35 * amp))
        grad.setColorAt(0.75, _c(primary, 12))
        grad.setColorAt(1.0, _c(bg, 0))
        p.setPen(Qt.PenStyle.NoPen)
        p.setBrush(QBrush(grad))
        p.drawEllipse(QPointF(cx, cy), r * 1.25, r * 1.25)

        # 2. Concentric Tactical Range Rings (Distance graduations: 25%, 50%, 75%, 100%)
        p.setBrush(Qt.BrushStyle.NoBrush)
        for frac, alpha in ((0.28, 0.25), (0.52, 0.30), (0.76, 0.35), (0.98, 0.50)):
            p.setPen(QPen(_blend(bg, primary, alpha + 0.25 * amp), 1.2 if frac < 0.95 else 1.8))
            p.drawEllipse(QPointF(cx, cy), r * frac, r * frac)

        # 3. 72 Azimuth Degree Ticks & Cardinal Compass Notches
        ticks = []
        for i in range(72):
            ang = math.radians(i * 5.0)
            ca, sa = math.cos(ang), math.sin(ang)
            is_cardinal = (i % 18 == 0)
            is_maj = (i % 6 == 0)
            in_r = r * (0.90 if is_cardinal else (0.93 if is_maj else 0.95))
            ticks.append(QLineF(cx + ca * in_r, cy + sa * in_r, cx + ca * r * 0.98, cy + sa * r * 0.98))
        p.setPen(QPen(_blend(bg, primary, 0.40 + 0.3 * amp), 1.2))
        p.drawLines(ticks)

        # Crosshair axes
        p.setPen(QPen(_blend(bg, primary, 0.25 + 0.2 * amp), 1.0))
        p.drawLine(QLineF(cx - r * 0.98, cy, cx + r * 0.98, cy))
        p.drawLine(QLineF(cx, cy - r * 0.98, cx, cy + r * 0.98))

        # 4. 3D Rotating Holographic Globe Grid (Meridians & Parallels)
        globe_r = r * 0.62
        rot_y = t * 0.8
        # Longitude meridians (rotating ellipses)
        num_meridians = 8
        for m_i in range(num_meridians):
            m_ang = rot_y + m_i * (math.pi / num_meridians)
            mw = globe_r * abs(math.cos(m_ang))
            m_alpha = 0.20 + 0.30 * abs(math.cos(m_ang)) + 0.15 * amp
            p.setPen(QPen(_blend(bg, accent, m_alpha), 1.1))
            p.drawEllipse(QPointF(cx, cy), max(1.0, mw), globe_r)

        # Latitude parallels (horizontal planes)
        for lat_frac in (-0.6, -0.3, 0.0, 0.3, 0.6):
            pw = globe_r * math.cos(math.asin(abs(lat_frac)))
            py_off = cy + globe_r * lat_frac
            p.setPen(QPen(_blend(bg, primary, 0.22 + 0.15 * amp), 1.0))
            p.drawEllipse(QPointF(cx, py_off), pw, pw * 0.28)

        # 5. Sweeping Active Radar Beam with Phosphor Trailing Glow
        sweep_rad = math.radians(self.sweep_angle)
        # Radar scan sector (30 degree fading wedge)
        radar_path = QPainterPath()
        radar_path.moveTo(QPointF(cx, cy))
        radar_path.arcTo(QRectF(cx - r * 0.98, cy - r * 0.98, r * 1.96, r * 1.96), -self.sweep_angle, 35.0)
        radar_path.closeSubpath()

        sweep_grad = QRadialGradient(cx, cy, r * 0.98)
        sweep_grad.setColorAt(0.0, _c(accent, int((0.35 + 0.25 * amp) * 255)))
        sweep_grad.setColorAt(0.6, _c(primary, int((0.15 + 0.15 * amp) * 255)))
        sweep_grad.setColorAt(1.0, _c(bg, 0))
        p.setPen(Qt.PenStyle.NoPen)
        p.setBrush(QBrush(sweep_grad))
        p.drawPath(radar_path)

        # Bright leading scanner needle
        p.setPen(QPen(_blend(bg, QColor(255, 255, 255), 0.90), 1.8))
        ca_sw, sa_sw = math.cos(sweep_rad), math.sin(sweep_rad)
        p.drawLine(QLineF(cx, cy, cx + ca_sw * r * 0.98, cy + sa_sw * r * 0.98))

        # 6. Target Acquisition Blips on Radar
        for t_r_frac, t_ang, t_size in self.targets:
            # Angle difference to sweep
            diff_ang = (math.degrees(t_ang) - self.sweep_angle) % 360.0
            if diff_ang < 60.0:
                glow_int = 1.0 - (diff_ang / 60.0)
                t_rad = r * t_r_frac
                tx = cx + math.cos(t_ang) * t_rad
                ty = cy + math.sin(t_ang) * t_rad

                # Blip diamond
                p.setPen(QPen(_blend(bg, QColor(255, 255, 255), glow_int), 1.2))
                p.setBrush(QBrush(_c(accent, int(glow_int * 200))))
                p.drawPolygon(QPolygonF([
                    QPointF(tx, ty - 4 * t_size),
                    QPointF(tx + 4 * t_size, ty),
                    QPointF(tx, ty + 4 * t_size),
                    QPointF(tx - 4 * t_size, ty),
                ]))

        # 7. Orbital Defense Satellites with Plasma Trailing Arcs
        for sat_r_frac, _, sat_ang, tilt_deg, sat_col in self.satellites:
            p.save()
            p.translate(cx, cy)
            p.rotate(tilt_deg)
            sat_rad_x = r * sat_r_frac
            sat_rad_y = sat_rad_x * 0.38

            # Orbit guide ellipse
            p.setBrush(Qt.BrushStyle.NoBrush)
            col_sat = primary if sat_col == 0 else accent
            p.setPen(QPen(_blend(bg, col_sat, 0.25 + 0.2 * amp), 1.0))
            p.drawEllipse(QPointF(0, 0), sat_rad_x, sat_rad_y)

            # Satellite position
            sx = sat_rad_x * math.cos(sat_ang)
            sy = sat_rad_y * math.sin(sat_ang)

            # Trailing plasma spark trail
            for tr in range(5):
                tr_ang = sat_ang - (tr + 1) * 0.12
                trx = sat_rad_x * math.cos(tr_ang)
                try_ = sat_rad_y * math.sin(tr_ang)
                p.setPen(Qt.PenStyle.NoPen)
                p.setBrush(QBrush(_blend(bg, col_sat, 0.6 - tr * 0.12)))
                p.drawEllipse(QPointF(trx, try_), 2.0 - tr * 0.3, 2.0 - tr * 0.3)

            # Main satellite node with solar panels
            p.setBrush(QBrush(_blend(bg, QColor(255, 255, 255), 0.95)))
            p.drawEllipse(QPointF(sx, sy), 3.0 + amp * 2.0, 3.0 + amp * 2.0)
            p.setPen(QPen(_blend(bg, accent, 0.8), 1.2))
            p.drawLine(QLineF(sx - 5, sy, sx + 5, sy))
            p.restore()

        # 8. Acoustic Sonar Burst Rings on Voice
        if amp > 0.05:
            p.setBrush(Qt.BrushStyle.NoBrush)
            for s_i in range(3):
                sonar_r = r * (0.3 + 0.65 * ((t * 1.5 + s_i * 0.33) % 1.0))
                sonar_alpha = max(0.0, (1.0 - sonar_r / r)) * amp * 0.7
                p.setPen(QPen(_blend(bg, accent, sonar_alpha), 1.5))
                p.drawEllipse(QPointF(cx, cy), sonar_r, sonar_r)

        # 9. Tactical Corner Framing Brackets
        p.setBrush(Qt.BrushStyle.NoBrush)
        bracket_len = r * 0.18
        br_r = r * 0.98
        p.setPen(QPen(_blend(bg, primary, 0.45 + 0.35 * amp), 1.5))
        for sx_b, sy_b in ((-1, -1), (1, -1), (-1, 1), (1, 1)):
            bx = cx + sx_b * br_r
            by = cy + sy_b * br_r
            p.drawLine(QLineF(bx, by, bx - sx_b * bracket_len, by))
            p.drawLine(QLineF(bx, by, bx, by - sy_b * bracket_len))

        p.restore()


# =============================================================================
# 5. HYPERDRIVE WARP CORE (Replaces Black Hole completely with high momentum)
# =============================================================================

class HyperdriveWarpVisualizer:
    """
    Hyperdrive Warp Core / Relativistic Quantum Dynamo.
    Engineered for perpetual kinetic momentum, high-velocity plasma acceleration,
    counter-rotating electromagnetic accelerator rings, spiraling warp vortex streams,
    magnetic pinch chicanes, and explosive audio-reactive kinetic warp flares.
    """

    def __init__(self) -> None:
        self.phase = 0.0
        self.amp = 0.0

        # High-velocity relativistic plasma particles in the vortex:
        # (radius_frac, angle, radial_speed, angular_speed, size, tier)
        self.particles = []
        for _ in range(72):
            self.particles.append([
                random.uniform(0.15, 0.95),
                random.uniform(0.0, math.pi * 2.0),
                random.uniform(0.2, 0.8),
                random.uniform(2.0, 5.0),
                random.uniform(1.8, 3.5),
                random.randint(0, 2),
            ])

        # Magnetic pinch coils (4 cardinal electromagnetic chicanes)
        self.pinch_flashes = [0.0] * 4

    def step(self, dt: float, amp: float, speaking: bool, state: str = "IDLE", muted: bool = False) -> None:
        # Supercharged momentum: high animation speed
        speed = 1.4 + (3.0 if state in ("THINKING", "PROCESSING") else 0.0) + (2.2 if speaking else 0.0)
        self.phase += dt * speed

        target = amp if not muted else 0.0
        self.amp += (target - self.amp) * min(1.0, dt * 15.0)

        # Advance plasma vortex particles with high momentum
        p_accel = 1.0 + (3.5 if speaking else 0.0)
        for pt in self.particles:
            # High-velocity angular spin
            pt[1] += dt * pt[3] * p_accel
            # Accelerate inward/outward in dynamic vortex breathing
            pt[0] -= dt * pt[2] * 0.15 * p_accel
            if pt[0] < 0.12:
                pt[0] = random.uniform(0.85, 0.96)
                pt[1] = random.uniform(0.0, math.pi * 2.0)

        # Update pinch coil ionization flashes
        for i in range(4):
            if random.random() < (0.2 + 0.6 * self.amp):
                self.pinch_flashes[i] = 1.0
            else:
                self.pinch_flashes[i] = max(0.0, self.pinch_flashes[i] - dt * 4.0)

    def paint(self, p: QPainter, cx: float, cy: float, r: float, primary: QColor, accent: QColor, bg: QColor) -> None:
        p.save()
        p.setRenderHint(QPainter.RenderHint.Antialiasing, True)
        t = self.phase
        amp = self.amp

        # 1. High-Energy Relativistic Warp Bloom
        core_r = r * (0.28 + 0.18 * amp)
        grad = QRadialGradient(cx, cy, r * 1.3)
        grad.setColorAt(0.0, _c(QColor(255, 255, 255), 220 + 35 * amp))
        grad.setColorAt(0.25, _c(accent, 170 + 80 * amp))
        grad.setColorAt(0.60, _c(primary, 65 + 40 * amp))
        grad.setColorAt(1.0, _c(bg, 0))
        p.setPen(Qt.PenStyle.NoPen)
        p.setBrush(QBrush(grad))
        p.drawEllipse(QPointF(cx, cy), r * 1.3, r * 1.3)

        # 2. Quad-Pole Magnetic Pinch Containment Chicanes (at 0°, 90°, 180°, 270°)
        for i in range(4):
            ang_coil = i * (math.pi / 2.0)
            ca_c, sa_c = math.cos(ang_coil), math.sin(ang_coil)
            flash = self.pinch_flashes[i]
            coil_col = _lerp_col(primary, QColor(255, 255, 255), flash)

            # Magnetic pole bracket
            p.setBrush(Qt.BrushStyle.NoBrush)
            p.setPen(QPen(_blend(bg, coil_col, 0.6 + 0.4 * flash), 2.5 + 2.0 * flash))
            p_in = QPointF(cx + ca_c * r * 0.82, cy + sa_c * r * 0.82)
            p_out = QPointF(cx + ca_c * r * 0.98, cy + sa_c * r * 0.98)
            p.drawLine(p_in, p_out)

            # Ionization flash bead
            p.setPen(Qt.PenStyle.NoPen)
            p.setBrush(QBrush(_blend(bg, coil_col, 0.8 + 0.2 * flash)))
            p.drawEllipse(p_in, 3.5 + 3.0 * flash, 3.5 + 3.0 * flash)

        # 3. 4 Counter-Rotating High-Velocity Accelerator Rings
        p.setBrush(Qt.BrushStyle.NoBrush)
        rings = [
            (r * 0.96, 60, 4, 1.2, primary, 2.0),
            (r * 0.82, 45, 5, -1.8, accent, 1.8),
            (r * 0.66, 90, 3, 2.6, primary, 2.2),
            (r * 0.50, 70, 4, -3.4, accent, 2.4),
        ]
        for rad, span, segs, dirn, col, thick in rings:
            p.setPen(QPen(_blend(bg, col, 0.50 + 0.45 * amp), thick))
            box = QRectF(cx - rad, cy - rad, rad * 2, rad * 2)
            base_ang = (t * 45.0 * dirn) % 360.0
            for s_idx in range(segs):
                ang = int((base_ang + s_idx * (360.0 / segs)) * 16)
                p.drawArc(box, ang, int(span * 16))

        # 4. Spiraling Relativistic Matter Vortex (High-velocity particle trails)
        p.setPen(Qt.PenStyle.NoPen)
        for r_frac, ang, _, _, size, tier in self.particles:
            pr = r * r_frac
            px = cx + math.cos(ang) * pr
            py = cy + math.sin(ang) * pr

            col_pt = primary if tier == 0 else (accent if tier == 1 else QColor(255, 255, 255))
            alpha_pt = 0.50 + 0.45 * (1.0 - r_frac) + 0.35 * amp
            p.setBrush(QBrush(_blend(bg, col_pt, min(1.0, alpha_pt))))
            p.drawEllipse(QPointF(px, py), size + amp * 2.0, size + amp * 2.0)

            # Kinetic motion comet tail
            tail_ang = ang - 0.08
            tx = cx + math.cos(tail_ang) * (pr * 1.02)
            ty = cy + math.sin(tail_ang) * (pr * 1.02)
            p.setBrush(QBrush(_blend(bg, col_pt, min(1.0, alpha_pt * 0.4))))
            p.drawEllipse(QPointF(tx, ty), size * 0.6, size * 0.6)

        # 5. Explosive Kinetic Warp Flares (Collimated high-energy spikes on audio)
        if amp > 0.04:
            flare_lines = []
            num_flares = 24
            for f_i in range(num_flares):
                ang_f = math.radians(f_i * (360.0 / num_flares) + t * 24.0)
                cf, sf = math.cos(ang_f), math.sin(ang_f)
                f_h = r * (0.15 + 0.35 * amp * (0.6 + 0.4 * math.sin(t * 18.0 + f_i * 1.5)))
                flare_lines.append(QLineF(cx + cf * core_r, cy + sf * core_r,
                                         cx + cf * (core_r + f_h), cy + sf * (core_r + f_h)))
            p.setPen(QPen(_blend(bg, QColor(255, 255, 255), 0.90), 2.0))
            p.drawLines(flare_lines)

        # 6. Central Hyper-Dense Quantum Warp Singularity Core
        p.setPen(QPen(_blend(bg, accent, 0.90), 2.4))
        p.drawEllipse(QPointF(cx, cy), core_r, core_r)

        core_grad = QRadialGradient(cx, cy, core_r)
        core_grad.setColorAt(0.0, _c(QColor(255, 255, 255), 255))
        core_grad.setColorAt(0.35, _c(accent, 210 + 45 * amp))
        core_grad.setColorAt(0.75, _c(primary, 100 + 40 * amp))
        core_grad.setColorAt(1.0, _c(bg, 10))
        p.setPen(Qt.PenStyle.NoPen)
        p.setBrush(QBrush(core_grad))
        p.drawEllipse(QPointF(cx, cy), core_r * 0.78, core_r * 0.78)

        # High-speed spinning vortex eye reticle
        p.setBrush(Qt.BrushStyle.NoBrush)
        p.setPen(QPen(_blend(bg, QColor(255, 255, 255), 0.95), 1.5))
        eye_box = QRectF(cx - core_r * 0.4, cy - core_r * 0.4, core_r * 0.8, core_r * 0.8)
        p.drawArc(eye_box, int((t * 180.0) % 360.0 * 16), int(120 * 16))
        p.drawArc(eye_box, int((t * 180.0 + 180.0) % 360.0 * 16), int(120 * 16))

        # (No bottom telemetry text line!)
        p.restore()


# =============================================================================
# 6. FRACTAL BIO-SYNAPSE / NEURAL LOTUS (Sacred Geometry Biocore - ENHANCED)
# =============================================================================

class NeuralLotusVisualizer:
    """
    Sacred Geometry Fibonacci Bio-Synapse Lotus.
    Supercharged with dynamic momentum, fluid counter-rotation inertia,
    acoustic blossoming on voice spikes, inter-tier synaptic lightning discharges,
    concentric Cymatics shockwaves, and rotating double-helix DNA ganglion.
    """

    def __init__(self) -> None:
        self.phase = 0.0
        self.amp = 0.0
        self.rot_inner = 0.0
        self.rot_mid = 0.0
        self.rot_outer = 0.0

        # Action-potential sparks traveling along dendritic branches
        self.sparks = []
        for _ in range(24):
            ang_idx = random.randint(0, 15)
            self.sparks.append([float(ang_idx), random.random(), random.uniform(0.9, 2.2)])

        # Inter-tier synaptic lightning arcs
        self.lightning_arcs: List[Tuple[float, float, float, float]] = []

    def step(self, dt: float, amp: float, speaking: bool, state: str = "IDLE", muted: bool = False) -> None:
        speed = 1.0 + (2.4 if state in ("THINKING", "PROCESSING") else 0.0) + (1.8 if speaking else 0.0)
        self.phase += dt * speed

        # Fluid momentum and rotational inertia across tiers
        self.rot_inner += dt * 1.6 * speed
        self.rot_mid -= dt * 0.9 * speed
        self.rot_outer += dt * 0.45 * speed

        target = amp if not muted else 0.0
        self.amp += (target - self.amp) * min(1.0, dt * 14.0)

        # Advance sparks
        s_speed = 1.0 + (3.2 if speaking else 0.0)
        for sp in self.sparks:
            sp[1] += dt * sp[2] * s_speed
            if sp[1] >= 1.0:
                sp[1] = 0.0
                sp[0] = float(random.randint(0, 15))

    def paint(self, p: QPainter, cx: float, cy: float, r: float, primary: QColor, accent: QColor, bg: QColor) -> None:
        p.save()
        p.setRenderHint(QPainter.RenderHint.Antialiasing, True)
        t = self.phase
        amp = self.amp

        # 1. Atmospheric Bio-Plasma Bloom
        grad = QRadialGradient(cx, cy, r * 1.3)
        grad.setColorAt(0.0, _c(accent, 150 + 80 * amp))
        grad.setColorAt(0.35, _c(primary, 55 + 40 * amp))
        grad.setColorAt(0.75, _c(primary, 12))
        grad.setColorAt(1.0, _c(bg, 0))
        p.setPen(Qt.PenStyle.NoPen)
        p.setBrush(QBrush(grad))
        p.drawEllipse(QPointF(cx, cy), r * 1.3, r * 1.3)

        # 2. Sacred Flower of Life / Harmonic Matrix (Faint background)
        p.setBrush(Qt.BrushStyle.NoBrush)
        p.setPen(QPen(_blend(bg, primary, 0.20 + 0.15 * amp), 1.0))
        seed_r = r * 0.45
        for i in range(6):
            ang = i * (math.pi / 3.0) + t * 0.25
            ox = cx + math.cos(ang) * seed_r * 0.65
            oy = cy + math.sin(ang) * seed_r * 0.65
            p.drawEllipse(QPointF(ox, oy), seed_r * 0.65, seed_r * 0.65)
        p.drawEllipse(QPointF(cx, cy), r * 0.94, r * 0.94)

        # 3. Concentric Cymatics Acoustic Resonance Shockwaves on Voice
        if amp > 0.04:
            p.setBrush(Qt.BrushStyle.NoBrush)
            for c_i in range(3):
                cym_r = r * (0.25 + 0.70 * ((t * 1.4 + c_i * 0.33) % 1.0))
                cym_alpha = max(0.0, (1.0 - cym_r / r)) * amp * 0.65
                p.setPen(QPen(_blend(bg, accent, cym_alpha), 1.4))
                p.drawEllipse(QPointF(cx, cy), cym_r, cym_r)

        # 4. Bioluminescent Synaptic Dendrite Tree & Action Potentials
        num_branches = 16
        branch_lines = []
        synapse_nodes = []
        for i in range(num_branches):
            ang = math.radians(i * (360.0 / num_branches) - t * 1.2)
            ca, sa = math.cos(ang), math.sin(ang)
            r_in = r * 0.35
            r_out = r * (0.80 + 0.14 * amp)

            branch_lines.append(QLineF(cx + ca * r_in, cy + sa * r_in, cx + ca * r_out, cy + sa * r_out))
            synapse_nodes.append(QPointF(cx + ca * r_out, cy + sa * r_out))

            ang_f1 = ang + math.radians(10.0)
            ang_f2 = ang - math.radians(10.0)
            r_tip = r_out + r * 0.08
            branch_lines.append(QLineF(cx + ca * r_out, cy + sa * r_out, cx + math.cos(ang_f1) * r_tip, cy + math.sin(ang_f1) * r_tip))
            branch_lines.append(QLineF(cx + ca * r_out, cy + sa * r_out, cx + math.cos(ang_f2) * r_tip, cy + math.sin(ang_f2) * r_tip))

        p.setPen(QPen(_blend(bg, accent, 0.45 + 0.40 * amp), 1.3))
        p.drawLines(branch_lines)

        # Firing action-potential sparks
        p.setPen(Qt.PenStyle.NoPen)
        for ang_idx, progress, _ in self.sparks:
            ang = math.radians(int(ang_idx) * (360.0 / num_branches) - t * 1.2)
            ca, sa = math.cos(ang), math.sin(ang)
            sp_r = r * 0.35 + progress * r * (0.45 + 0.14 * amp)
            p.setBrush(QBrush(_blend(bg, QColor(255, 255, 255), 0.95)))
            p.drawEllipse(QPointF(cx + ca * sp_r, cy + sa * sp_r), 2.5 + amp * 2.2, 2.5 + amp * 2.2)

        for sn in synapse_nodes:
            p.setBrush(QBrush(_blend(bg, primary, 0.75 + 0.25 * amp)))
            p.drawEllipse(sn, 2.8, 2.8)

        # 5. Multi-Tiered Fibonacci Lotus Petals (Supercharged with Momentum & Blooming)
        petal_tiers = [
            (24, r * 0.84, r * 0.38, self.rot_outer, primary, 0.12, 1.2),
            (16, r * 0.62, r * 0.24, self.rot_mid, accent, 0.18, 1.4),
            (8, r * 0.40, r * 0.15, self.rot_inner, QColor(255, 255, 255), 0.25, 1.6),
        ]

        tier_apex_points = []
        for num_p, r_tip, r_base, base_rot, col, fill_alpha, pen_w in petal_tiers:
            # Dynamic acoustic blooming on voice
            cur_tip = r_tip * (1.0 + 0.18 * amp)
            apex_list = []

            for i in range(num_p):
                theta = math.radians(i * (360.0 / num_p)) + base_rot
                half_span = math.radians(360.0 / (num_p * 2.0))

                p_base1 = QPointF(cx + math.cos(theta - half_span) * r_base, cy + math.sin(theta - half_span) * r_base)
                p_base2 = QPointF(cx + math.cos(theta + half_span) * r_base, cy + math.sin(theta + half_span) * r_base)
                p_apex = QPointF(cx + math.cos(theta) * cur_tip, cy + math.sin(theta) * cur_tip)
                apex_list.append(p_apex)

                cp1 = QPointF(cx + math.cos(theta - half_span * 0.8) * (r_base + cur_tip) * 0.55,
                              cy + math.sin(theta - half_span * 0.8) * (r_base + cur_tip) * 0.55)
                cp2 = QPointF(cx + math.cos(theta + half_span * 0.8) * (r_base + cur_tip) * 0.55,
                              cy + math.sin(theta + half_span * 0.8) * (r_base + cur_tip) * 0.55)

                path = QPainterPath()
                path.moveTo(p_base1)
                path.quadTo(cp1, p_apex)
                path.quadTo(cp2, p_base2)
                path.closeSubpath()

                fa = max(0.05, min(0.42, fill_alpha + 0.16 * amp))
                p.setBrush(QBrush(_c(col, int(fa * 255))))
                p.setPen(QPen(_blend(bg, col, 0.45 + 0.45 * amp), pen_w))
                p.drawPath(path)

            tier_apex_points.append(apex_list)

        # 6. Inter-Tier Synaptic Lightning Discharges on Speech Peaks
        if amp > 0.08 and len(tier_apex_points) >= 2:
            mid_pts = tier_apex_points[1]
            outer_pts = tier_apex_points[0]
            p.setPen(QPen(_blend(bg, QColor(255, 255, 255), 0.85 * amp), 1.5))
            for i in range(min(len(mid_pts), len(outer_pts) // 2)):
                if random.random() < 0.35 * amp:
                    p1 = mid_pts[i]
                    p2 = outer_pts[i * 2]
                    # Jagged lightning segment
                    mid_x = (p1.x() + p2.x()) * 0.5 + random.uniform(-6, 6)
                    mid_y = (p1.y() + p2.y()) * 0.5 + random.uniform(-6, 6)
                    p.drawLine(p1, QPointF(mid_x, mid_y))
                    p.drawLine(QPointF(mid_x, mid_y), p2)

        # 7. Central Cymatics & DNA Double-Helix Ganglion Core
        core_r = r * (0.22 + 0.12 * amp)
        core_grad = QRadialGradient(cx, cy, core_r)
        core_grad.setColorAt(0.0, _c(QColor(255, 255, 255), 250))
        core_grad.setColorAt(0.35, _c(accent, 195 + 50 * amp))
        core_grad.setColorAt(0.75, _c(primary, 95 + 40 * amp))
        core_grad.setColorAt(1.0, _c(bg, 0))
        p.setPen(Qt.PenStyle.NoPen)
        p.setBrush(QBrush(core_grad))
        p.drawEllipse(QPointF(cx, cy), core_r, core_r)

        # Double-helix braided energy rings inside core
        p.setBrush(Qt.BrushStyle.NoBrush)
        helix_lines = []
        for step in range(24):
            ang_h = step * (math.pi / 12.0) + t * 5.0
            rh = core_r * 0.65 * (0.8 + 0.2 * math.sin(ang_h * 3.0))
            hx = cx + math.cos(ang_h) * rh
            hy = cy + math.sin(ang_h) * rh
            helix_lines.append(QPointF(hx, hy))
        p.setPen(QPen(_blend(bg, QColor(255, 255, 255), 0.90), 1.6))
        p.drawPolyline(helix_lines)

        # (No bottom telemetry text line!)
        p.restore()

# Backward compatibility aliases
ChronosTesseractVisualizer = TacticalRadarVisualizer
BlackHoleVisualizer = HyperdriveWarpVisualizer

__all__ = [
    "ArcReactorVisualizer",
    "QuantumSphereVisualizer",
    "CyberIrisVisualizer",
    "TacticalRadarVisualizer",
    "HyperdriveWarpVisualizer",
    "NeuralLotusVisualizer",
    "ChronosTesseractVisualizer",
    "BlackHoleVisualizer",
]
