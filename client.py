# -*- coding: utf-8 -*-
"""
GenPark Ctrip Destination Crowd Density Router Client
Optimizes real-time attraction visitor dispersion and queueing wait times using queuing theory and dynamic heatmap routing.
Zero external dependencies -- Python 3.9+ standard library only.
"""

import math
from typing import Dict, Any, List

class GenParkCtripDestinationCrowdDensityRouter:
    """
    Evaluates real-time attraction visitor capacity saturation and queue delay (M/M/c approximation),
    recommending off-peak time shifts and alternative sister attractions.
    """

    DEFAULT_HOURLY_CONGESTION_CURVE = {
        8: 0.20, 9: 0.45, 10: 0.85, 11: 0.98, 12: 0.92,
        13: 0.88, 14: 0.95, 15: 0.90, 16: 0.70, 17: 0.40, 18: 0.25
    }

    def __init__(self, service_capacity_rate_per_min: float = 45.0):
        self.mu = service_capacity_rate_per_min

    def estimate_queue_wait_mins(self, saturation_pct: float) -> int:
        """
        Approximates queueing wait time based on non-linear queue saturation.
        """
        rho = min(0.98, max(0.05, saturation_pct / 100.0))
        # Non-linear queuing expansion
        expected_wait = (rho / (1.0 - rho)) * 4.5
        return int(round(expected_wait))

    def optimize_attraction_visitation(
        self,
        attraction_name: str,
        maximum_daily_capacity: int = 40000,
        requested_visit_hour: float = 11.0,
        current_live_visitors: int = 36000,
        alternative_sister_pois: List[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Evaluates crowd density and calculates optimal off-peak dispersion.
        """
        if alternative_sister_pois is None:
            alternative_sister_pois = [
                {"name": "Jingshan Park & Panorama Hill", "dist_km": 0.8, "current_saturation_pct": 28.0, "highlight": "Panoramic view overlooking the Forbidden City without queues"},
                {"name": "Beihai Imperial Royal Park", "dist_km": 1.4, "current_saturation_pct": 32.0, "highlight": "Lakeside classical garden architecture and tranquil pavilions"},
                {"name": "Prince Kung's Mansion", "dist_km": 2.5, "current_saturation_pct": 45.0, "highlight": "Largest Qing Dynasty princely mansion in Beijing"}
            ]

        saturation_pct = round((current_live_visitors / max(1, maximum_daily_capacity)) * 100.0, 1)
        est_queue_mins = self.estimate_queue_wait_mins(saturation_pct)

        # Evaluate best alternative off-peak time slots (morning early-bird vs late afternoon)
        optimal_slots = []
        for h, load in sorted(self.DEFAULT_HOURLY_CONGESTION_CURVE.items()):
            if load <= 0.45:
                optimal_slots.append({
                    "time_window": f"{h:02d}:00 - {h+1:02d}:30",
                    "historical_load_pct": round(load * 100.0, 1),
                    "estimated_wait_mins": int(round(self.estimate_queue_wait_mins(load * 100.0)))
                })

        # Classification
        if saturation_pct >= 85.0:
            congestion_tier = "EXTREME_RED_PEAK"
            dispersion_advice = "Severe bottleneck queues. Highly recommended to shift arrival time or explore nearby sister POIs."
        elif saturation_pct >= 60.0:
            congestion_tier = "MODERATE_YELLOW_BUSY"
            dispersion_advice = "Normal tourist flow. Expect manageable queues at security check and ticket gates."
        else:
            congestion_tier = "OPTIMAL_GREEN_FLOW"
            dispersion_advice = "Low crowd density. Ideal visitation window with virtually zero wait time."

        return {
            "attraction_name": attraction_name,
            "requested_visit_hour": f"{int(requested_visit_hour):02d}:{int((requested_visit_hour % 1)*60):02d}",
            "current_saturation_pct": saturation_pct,
            "congestion_tier": congestion_tier,
            "estimated_entry_wait_mins": est_queue_mins,
            "dispersion_advice": dispersion_advice,
            "recommended_offpeak_windows": optimal_slots[:2],
            "nearby_low_density_alternatives": alternative_sister_pois
        }
