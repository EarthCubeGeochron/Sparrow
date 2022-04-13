# A sample dataset from Becky Flowers' lab
fixture = {
    "member_of": {
        "project": [{"name": "Baker – 7 samples"}],
        "name": "BF03-175-Agt_1",
        "material": "rock",
    },
    "name": "BF03-175-Agt_1_1",
    "material": "zircon",
    "session": [
        {
            "technique": {"id": "Grain quality inspection"},
            "instrument": {"name": "Leica microscope"},
            "date": "1900-01-01 00:00:00+00",
            "analysis": [
                {
                    "analysis_type": "Grain shape",
                    "datum": [
                        {
                            "value": 757.0,
                            "error": None,
                            "type": {"parameter": "length 1", "unit": "mm"},
                        },
                        {
                            "value": 361.5,
                            "error": None,
                            "type": {"parameter": "width 1", "unit": "mm"},
                        },
                        {
                            "value": 702.0,
                            "error": None,
                            "type": {"parameter": "length 2", "unit": "mm"},
                        },
                        {
                            "value": 362.0,
                            "error": None,
                            "type": {"parameter": "width 2", "unit": "mm"},
                        },
                        {
                            "value": 400.9511457,
                            "error": None,
                            "type": {"parameter": "Dim Mass", "unit": "mg"},
                        },
                        {
                            "value": 212.4797446456212,
                            "error": None,
                            "type": {"parameter": "rs", "unit": "mm"},
                        },
                    ],
                    "attribute": [
                        {
                            "parameter": "Crystal termination",
                            "value": "double-terminated",
                        },
                        {"parameter": "Crystal geometry", "value": "Orthorhombic"},
                        {"parameter": "note", "value": "best apatite ever"},
                    ],
                }
            ],
        },
        {
            "technique": {"id": "Noble-gas mass spectrometry"},
            "instrument": {"name": "ASI Alphachron → Pfeiffer Balzers QMS"},
            "date": "1900-01-01 00:00:00+00",
            "analysis": [
                {
                    "analysis_type": "Noble gas measurements",
                    "datum": [
                        {
                            "value": 2.629053588580897,
                            "error": 0.002913187828792837,
                            "type": {
                                "parameter": "4He",
                                "unit": "nmol/g",
                                "error_unit": None,
                            },
                        }
                    ],
                    "attribute": [],
                }
            ],
        },
        {
            "technique": "Trace element measurement",
            "instrument": {"name": "Agilent 7900 Quadrupole ICP-MS"},
            "date": "1900-01-01 00:00:00+00",
            "analysis": [
                {
                    "analysis_type": "Element data",
                    "datum": [
                        {
                            "value": 0.041570724871064016,
                            "error": 0.0030298128161217754,
                            "type": {
                                "parameter": "U",
                                "unit": "ppm",
                                "error_unit": None,
                            },
                        },
                        {
                            "value": 0.5512344479329546,
                            "error": 0.01146952652671369,
                            "type": {
                                "parameter": "Th",
                                "unit": "ppm",
                                "error_unit": None,
                            },
                        },
                        {
                            "value": 0.0,
                            "error": None,
                            "type": {
                                "parameter": "Sm",
                                "unit": "ppm",
                                "error_unit": None,
                            },
                        },
                    ],
                    "attribute": [],
                }
            ],
        },
        {
            "technique": {"id": "(U+Th)/He age estimation"},
            "date": "1900-01-01 00:00:00+00",
            "analysis": [
                {
                    "analysis_type": "Derived parameters",
                    "datum": [
                        {
                            "value": 0.17111082013530832,
                            "error": None,
                            "type": {"unit": "ppm", "parameter": "eU"},
                        },
                        {
                            "value": 23.62666994509874,
                            "error": 0.02618011577166803,
                            "type": {
                                "parameter": "4He",
                                "unit": "ncc",
                                "error_unit": None,
                            },
                        },
                        {
                            "value": 21.004551540923245,
                            "error": None,
                            "type": {"parameter": "Re", "unit": "%"},
                        },
                        {
                            "value": 0.016667829764632602,
                            "error": 0.0012148069198805694,
                            "type": {
                                "parameter": "U",
                                "unit": "ng",
                                "error_unit": None,
                            },
                        },
                        {
                            "value": 0.22101808344802518,
                            "error": 0.0045987198015223964,
                            "type": {
                                "parameter": "Th",
                                "unit": "ng",
                                "error_unit": None,
                            },
                        },
                        {
                            "value": 0.0,
                            "error": 0.0,
                            "type": {
                                "parameter": "Sm",
                                "unit": "ng",
                                "error_unit": None,
                            },
                        },
                        {
                            "value": 13.260159634999544,
                            "error": None,
                            "type": {"unit": "ratio", "parameter": "Th/U"},
                        },
                    ],
                    "attribute": [],
                },
                {
                    "analysis_type": "Raw date",
                    "datum": [
                        {
                            "value": 2542.8048470305966,
                            "error": 59.10134475387011,
                            "type": {
                                "parameter": "Raw Date",
                                "unit": "Ma",
                                "error_unit": None,
                            },
                        },
                        {
                            "value": 2500.624415026046,
                            "error": 59.10134475387011,
                            "type": {
                                "parameter": "Raw Date It",
                                "unit": "Ma",
                                "error_unit": None,
                            },
                        },
                    ],
                    "attribute": [],
                },
                {
                    "analysis_type": "Corrected date",
                    "datum": [
                        {
                            "value": 0.9381391869759617,
                            "error": None,
                            "type": {
                                "parameter": "alpha-ejection factor",
                                "unit": "dimensionless",
                            },
                        },
                        {
                            "value": 2703.951208022106,
                            "error": 125.69360384032265,
                            "type": {
                                "is_interpreted": True,
                                "parameter": "Corrected Date",
                                "unit": "Ma",
                                "error_unit": "Ma",
                            },
                        },
                        {
                            "value": 2640.8439962947537,
                            "error": 125.69360384032265,
                            "type": {
                                "is_interpreted": True,
                                "parameter": "Corrected Date (It)",
                                "unit": "Ma",
                                "error_unit": "Ma",
                            },
                        },
                    ],
                    "attribute": [],
                },
            ],
        },
    ],
}


class TestReimportData:
    def test_import_data(self, db):
        db.load_data("sample", fixture)

    def test_reimport_data(self, db):
        db.load_data("sample", fixture)
