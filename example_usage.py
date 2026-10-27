# -*- coding: utf-8 -*-
"""
Example usage of GenParkCtripDestinationCrowdDensityRouter
Demonstrates peak hour dispersion and sister POI recommendations.
"""

from client import GenParkCtripDestinationCrowdDensityRouter

def main():
    router = GenParkCtripDestinationCrowdDensityRouter()

    res = router.optimize_attraction_visitation(
        attraction_name="The Palace Museum (Forbidden City)",
        maximum_daily_capacity=40000,
        requested_visit_hour=11.5,
        current_live_visitors=36500
    )

    print("================================================================")
    print("GenPark Ctrip Destination Crowd Density Router - Live Runs")
    print("================================================================\n")
    print(f"Target Attraction     : {res['attraction_name']}")
    print(f"Requested Visit Hour  : {res['requested_visit_hour']}")
    print(f"Live Saturation       : {res['current_saturation_pct']}% [{res['congestion_tier']}]")
    print(f"Estimated Wait Time   : ~{res['estimated_entry_wait_mins']} minutes")
    print(f"Dispersion Advice     : {res['dispersion_advice']}\n")
    print("Recommended Off-Peak Windows:")
    for w in res["recommended_offpeak_windows"]:
        print(f"  * {w['time_window']:<15} (Historical Load: {w['historical_load_pct']}%, Est Wait: {w['estimated_wait_mins']}m)")
    print("\nNearby Lower Density Sister POIs:")
    for poi in res["nearby_low_density_alternatives"]:
        print(f"  * {poi['name']:<30} ({poi['dist_km']}km away, Saturation: {poi['current_saturation_pct']}%) -> {poi['highlight']}")

if __name__ == "__main__":
    main()
