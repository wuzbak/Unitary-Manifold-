"""
TerraOS — Pure Python soil and water analyzers (no API keys required).
"""
from __future__ import annotations


class SoilAnalyzer:
    def analyze(self, data: dict) -> dict:
        issues: list[str] = []
        recommendations: list[str] = []
        score = 100.0

        ph = data.get("ph")
        if ph is not None:
            if ph < 5.5:
                issues.append(f"Soil pH {ph} is too acidic (optimal: 6.0–7.0)")
                recommendations.append("Apply agricultural lime to raise pH")
                score -= 20
            elif ph > 7.5:
                issues.append(f"Soil pH {ph} is too alkaline (optimal: 6.0–7.0)")
                recommendations.append("Apply sulfur or acidifying fertilizer to lower pH")
                score -= 15
            else:
                recommendations.append(f"Soil pH {ph} is in optimal range")

        om = data.get("organic_matter_pct")
        if om is not None:
            if om < 1.0:
                issues.append(f"Organic matter {om}% is critically low (target >3%)")
                recommendations.append("Add compost or cover crops to build organic matter")
                score -= 25
            elif om < 2.5:
                issues.append(f"Organic matter {om}% is below target (>3%)")
                recommendations.append("Add 5–10 cm compost layer annually")
                score -= 10
            else:
                recommendations.append(f"Organic matter {om}% is adequate")

        sand = data.get("sand_pct")
        silt = data.get("silt_pct")
        clay = data.get("clay_pct")
        if sand is not None and silt is not None and clay is not None:
            total = sand + silt + clay
            if abs(total - 100) > 5:
                issues.append(f"Sand+Silt+Clay total {total}% — should be ~100%")
            if clay > 40:
                issues.append("High clay content — risk of waterlogging and compaction")
                recommendations.append("Add gypsum or organic matter to improve structure")
                score -= 10
            elif sand > 70:
                issues.append("High sand content — poor water and nutrient retention")
                recommendations.append("Add compost or vermiculite to improve retention")
                score -= 10

        cec = data.get("cec")
        if cec is not None:
            if cec < 5:
                issues.append(f"CEC {cec} is very low — poor nutrient-holding capacity")
                score -= 15
            elif cec > 50:
                recommendations.append(f"CEC {cec} is very high (clay/peat dominant)")

        score = max(0.0, min(100.0, score))
        summary = "Good soil conditions." if score >= 70 else ("Moderate concerns." if score >= 40 else "Significant soil issues detected.")
        return {
            "analysis_type": "soil",
            "summary": summary,
            "issues": issues,
            "recommendations": recommendations,
            "score": round(score, 1),
        }


class WaterAnalyzer:
    def analyze(self, data: dict) -> dict:
        issues: list[str] = []
        recommendations: list[str] = []
        score = 100.0

        ph = data.get("ph")
        if ph is not None:
            if ph < 6.5:
                issues.append(f"Water pH {ph} is acidic (WHO: 6.5–8.5)")
                recommendations.append("Add pH correction (e.g., lime) or aerate")
                score -= 20
            elif ph > 8.5:
                issues.append(f"Water pH {ph} is alkaline (WHO: 6.5–8.5)")
                recommendations.append("Add CO2 or acidic buffer")
                score -= 15

        tds = data.get("tds_ppm")
        if tds is not None:
            if tds > 1000:
                issues.append(f"TDS {tds} ppm exceeds 1000 ppm limit")
                recommendations.append("Install reverse osmosis or ion exchange")
                score -= 20
            elif tds > 500:
                issues.append(f"TDS {tds} ppm exceeds preferred 500 ppm")
                score -= 10

        nitrate = data.get("nitrate_ppm")
        if nitrate is not None:
            if nitrate > 50:
                issues.append(f"Nitrate {nitrate} mg/L exceeds WHO limit of 50 mg/L")
                recommendations.append("Reduce agricultural runoff; use denitrification filter")
                score -= 30
            elif nitrate > 10:
                issues.append(f"Nitrate {nitrate} mg/L exceeds US EPA MCL of 10 mg/L")
                recommendations.append("Seek alternative source or install nitrate filter")
                score -= 15

        do2 = data.get("dissolved_o2_ppm")
        if do2 is not None:
            if do2 < 2.0:
                issues.append(f"Dissolved oxygen {do2} mg/L is critically low (anoxic)")
                recommendations.append("Aerate water; check for organic pollution")
                score -= 25
            elif do2 < 5.0:
                issues.append(f"Dissolved oxygen {do2} mg/L is below healthy threshold (5 mg/L)")
                score -= 10

        hardness = data.get("hardness_ppm")
        if hardness is not None:
            if hardness > 500:
                issues.append(f"Water hardness {hardness} ppm is very hard")
                recommendations.append("Install water softener for household use")
                score -= 10

        score = max(0.0, min(100.0, score))
        summary = "Water quality is acceptable." if score >= 70 else ("Moderate water quality concerns." if score >= 40 else "Significant water quality issues detected.")
        return {
            "analysis_type": "water",
            "summary": summary,
            "issues": issues,
            "recommendations": recommendations,
            "score": round(score, 1),
        }
