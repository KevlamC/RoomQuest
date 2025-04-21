from flask import Blueprint, request, jsonify

maps = Blueprint("maps", __name__)

building_to_file = {
    "BI": "BI_-_Biological_Sciences.pdf",
    "CHC": "CHC_-_Craigie_Hall_Block_C.pdf",
    "CHE": "CHE_-_Craigie_Hall_Block_E.pdf",
    "CHF": "CHF_-_Craigie_Hall_Block_F.pdf",
    "CHG": "CHG_-_Craigie_Hall_Block_G.pdf",
    "EDC": "EDC_-_Education_Classroom_Block.pdf",
    "EEEL": "EEEL_-_Energy_Environment_Experiential_Learning.pdf",
    "ENA": "ENA_-_Engineering_Block_A.pdf",
    "ENB": "ENB_-_Engineering_Block_B.pdf",
    "ENC": "ENC_-_Engineering_Block_C.pdf",
    "END": "END_-_Engineering_Block_D.pdf",
    "ENE": "ENE_-_Engineering_Block_E.pdf",
    "ENF": "ENF_-_Engineering_Block_F.pdf",
    "ENG": "ENG_-_Engineering_Block_G.pdf",
    "ES": "ES_-_Earth_Sciences.pdf",
    "HNSC": "HNSC_-_Hunter_Student_Commons.pdf",
    "ICT": "ICT_-_Information_and_Communication_Technology.pdf",
    "KNA": "KNA_-_Kinesiology_Block_A.pdf",
    "MFH": "MFH_-_Murray_Fraser_Hall.pdf",
    "MS": "MS_-_Mathematical_Sciences.pdf",
    "MTH": "MTH_-_Mathison_Hall.pdf",
    "PF": "PF_-_Professional_Faculties.pdf",
    "SA": "SA_-_Science_A.pdf",
    "SH": "SH_-_Scurfield_Hall.pdf",
    "SS": "SS_-_Social_Sciences.pdf",
    "ST": "ST_-_Science_Theatres.pdf",
    "TFDL": "TFDL_-_Taylor_Family_Digital_Library.pdf"
}

@maps.route("/api/building-map", methods=["GET"])
def get_map_url():
    building = request.args.get("building")
    if not building:
        return jsonify({"error": "Missing 'building' parameter"}), 400

    pdf_file = building_to_file.get(building.upper())
    if not pdf_file:
        return jsonify({"error": "No map found for this building"}), 404

    base_url = "https://roomquest-g0ekbbd4csf3cscz.canadacentral-01.azurewebsites.net/static/maps/"
    return jsonify({"mapURL": base_url + pdf_file})
