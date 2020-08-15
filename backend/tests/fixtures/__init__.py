from datetime import datetime

basic_data = {
    "date": str(datetime.now()),
    "name": "Declarative import test",
    "sample": {"name": "Soil 001"},
    "analysis": [
        {
            "analysis_type": {
                "id": "Soil aliquot pyrolysis",
                "description": "I guess this could be an actual technique?",
            },
            "session_index": 0,
            "datum": [
                {
                    "value": 2.25,
                    "error": 0.2,
                    "type": {
                        "parameter": {"id": "soil water content"},
                        "unit": {"id": "weight %"},
                    },
                }
            ],
        }
    ],
}

basic_d18O_data = {
    "filename": None,
    "data": {
        "name": "Test session 1",
        "sample": {"name": "Test sample"},
        "date": "2020-01-01T00:00:00",
        "analysis": [
            {
                "analysis_type": "d18O measurement trial",
                "datum": [
                    {
                        "value": 9.414,
                        "type": {"parameter": "d18Omeas", "unit": "permille"},
                    }
                ],
            }
        ],
    },
}

incomplete_analysis = {
    # Can't seem to get or create this instance from the database
    "analysis_type": "Soil aliquot pyrolysis",
    "session_index": 0,
    "datum": [
        {
            "value": 0.1,
            "error": 0.025,
            "type": {"parameter": "soil water content", "unit": "weight %"},
        }
    ],
}
