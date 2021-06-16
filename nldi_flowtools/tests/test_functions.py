from nldi_flowtools.src.nldi_flowtools import splitcatchment, flowtrace
# from nldi_flowtools import splitcatchment, flowtrace


def test_splitcatchment():
    actual = None
    actual = splitcatchment(-93, 45, True)
    expected = {"features": [{"geometry": {"coordinates": [[[-93.0047, 44.9929], [-93.0053, 44.993], [-93.0051, 44.9944], [-93.0067, 44.9949], [-93.0091, 44.9959],
                [-93.01, 44.9974], [-93.0105, 44.9986], [-93.0098, 45.0], [-93.0125, 45.0025], [-93.0158, 45.0024], [-93.0169, 45.0033], [-93.0173, 45.0058], [-93.0182, 45.0064],
        [-93.0195, 45.0075], [-93.0164, 45.009], [-93.0159, 45.0104], [-93.0147, 45.0108], [-93.0147, 45.012], [-93.0178, 45.0116], [-93.0246, 45.0115], [-93.0279, 45.0129],
        [-93.0302, 45.0133], [-93.0306, 45.0144], [-93.0318, 45.0152], [-93.0323, 45.0156], [-93.0319, 45.0159], [-93.0313, 45.0162], [-93.0307, 45.0168], [-93.0285, 45.0173],
        [-93.0291, 45.0194], [-93.0257, 45.0199], [-93.0273, 45.0213], [-93.0276, 45.0219], [-93.028, 45.0224], [-93.0283, 45.0235], [-93.0291, 45.0235], [-93.0304, 45.0242],
        [-93.0296, 45.0251], [-93.0302, 45.0264], [-93.0313, 45.027], [-93.0304, 45.0298], [-93.032, 45.0302], [-93.0324, 45.0302], [-93.0322, 45.0309], [-93.0317, 45.0316],
        [-93.0323, 45.0329], [-93.0297, 45.0336], [-93.0298, 45.0347], [-93.0277, 45.0363], [-93.0263, 45.0354], [-93.0259, 45.0337], [-93.0256, 45.0318], [-93.0249, 45.032],
        [-93.0244, 45.0327], [-93.0228, 45.0331], [-93.0218, 45.0328], [-93.0212, 45.0322], [-93.0176, 45.0325], [-93.0162, 45.033], [-93.0134, 45.0318], [-93.0112, 45.0317],
        [-93.0108, 45.0325], [-93.0103, 45.033], [-93.0099, 45.0349], [-93.008, 45.0356], [-93.0057, 45.0357], [-93.0045, 45.0356], [-93.003, 45.0361], [-93.001, 45.0363],
        [-93.0003, 45.0372], [-92.9981, 45.0381], [-92.9963, 45.0395], [-92.9963, 45.04], [-92.9952, 45.0413], [-92.9943, 45.0444], [-92.9934, 45.0451], [-92.9927, 45.0455],
        [-92.9939, 45.046], [-92.995, 45.0469], [-92.9967, 45.048], [-92.9955, 45.0486], [-92.9949, 45.0496], [-92.9936, 45.0506], [-92.9915, 45.0503], [-92.9909, 45.0501],
        [-92.9897, 45.0499], [-92.989, 45.0486], [-92.9876, 45.0481], [-92.988, 45.0476], [-92.9892, 45.0469], [-92.9891, 45.0454], [-92.9897, 45.0446], [-92.9894, 45.0392],
        [-92.9889, 45.0389], [-92.9891, 45.0388], [-92.9917, 45.0381], [-92.9925, 45.0368], [-92.9938, 45.0356], [-92.9935, 45.0347], [-92.9921, 45.0338], [-92.992, 45.0334],
        [-92.9939, 45.0329], [-92.9958, 45.0319], [-92.996, 45.0312], [-92.9953, 45.0303], [-92.9958, 45.0285], [-92.995, 45.027], [-92.9946, 45.0265], [-92.9936, 45.0246],
        [-92.9952, 45.0238], [-92.9944, 45.023], [-92.9937, 45.0221], [-92.9921, 45.0224], [-92.9907, 45.0227], [-92.9895, 45.0226], [-92.9891, 45.0226], [-92.9883, 45.0225],
        [-92.9862, 45.0229], [-92.9849, 45.0244], [-92.9842, 45.0263], [-92.9825, 45.0253], [-92.9823, 45.0211], [-92.9816, 45.0197], [-92.9832, 45.0184], [-92.9832, 45.0179],
        [-92.9834, 45.0169], [-92.9822, 45.0157], [-92.9814, 45.0142], [-92.9803, 45.0136], [-92.9804, 45.013], [-92.9792, 45.0125], [-92.9774, 45.0122], [-92.9768, 45.0134],
        [-92.9747, 45.0126], [-92.9757, 45.0109], [-92.9789, 45.01], [-92.9792, 45.009], [-92.9772, 45.0079], [-92.9764, 45.0063], [-92.9765, 45.0056], [-92.9764, 45.0047],
        [-92.9773, 45.0039], [-92.9788, 45.0033], [-92.9804, 45.0035], [-92.9815, 45.0033], [-92.9836, 45.003], [-92.9849, 45.0016], [-92.9844, 45.0006], [-92.9837, 45.0003],
        [-92.9834, 45.0], [-92.984, 44.9996], [-92.985, 44.9969], [-92.9849, 44.9958], [-92.985, 44.9953], [-92.9866, 44.994], [-92.9871, 44.9931], [-92.9887, 44.9933],
        [-92.9914, 44.9932], [-92.993, 44.9939], [-92.994, 44.9938], [-92.9949, 44.9939], [-92.9966, 44.9938], [-92.9974, 44.9932], [-93.0001, 44.9949], [-93.0015, 44.9948],
        [-93.0028, 44.9938], [-93.0037, 44.9935], [-93.0043, 44.9931], [-93.0047, 44.9929]]], "type": "Polygon"}, "id": "catchment", "properties": {"catchmentID": "1100118"},
        "type": "Feature"}, {"geometry": {"coordinates": [[[-93.000192, 45.000058], [-93.000204, 44.999789], [-92.999442, 44.999772], [-92.99943, 45.000041], [-93.000192, 45.000058]]],
                             "type": "Polygon"}, "id": "splitCatchment", "properties": {}, "type": "Feature"}], "type": "FeatureCollection"}
    assert actual == expected


def test_flowtrace():
    actual = None
    actual = flowtrace(-93.06089554438601, 41.65410801168578, True, "up")
    expected = {
        "features": [
            {
                "geometry": {
                    "coordinates": [
                        [
                            -93.062,
                            41.6608
                        ],
                        [
                            -93.0621,
                            41.6606
                        ],
                        [
                            -93.0623,
                            41.6605
                        ],
                        [
                            -93.0626,
                            41.66
                        ],
                        [
                            -93.0627,
                            41.6596
                        ],
                        [
                            -93.0629,
                            41.6593
                        ],
                        [
                            -93.0645,
                            41.658
                        ],
                        [
                            -93.0665,
                            41.6566
                        ],
                        [
                            -93.0672,
                            41.6558
                        ],
                        [
                            -93.0684,
                            41.6549
                        ]
                    ],
                    "type": "LineString"
                },
                "id": "upstreamFlowline",
                "properties": {
                    "comid": 6981570,
                    "gnis_name": "Sewer Creek",
                    "intersectionPoint": (41.6549, -93.0684),
                    "measure": 3.75,
                    "raindropPathDist": 685.73,
                    "reachcode": "07080105001380"
                },
                "type": "Feature"
            },
            {
                "geometry": {
                    "coordinates": [
                        [
                            -93.060983,
                            41.654114
                        ],
                        [
                            -93.061346,
                            41.654122
                        ],
                        [
                            -93.061697,
                            41.654398
                        ],
                        [
                            -93.06206,
                            41.654406
                        ],
                        [
                            -93.062422,
                            41.654415
                        ],
                        [
                            -93.062785,
                            41.654423
                        ],
                        [
                            -93.063148,
                            41.654431
                        ],
                        [
                            -93.063511,
                            41.65444
                        ],
                        [
                            -93.063873,
                            41.654448
                        ],
                        [
                            -93.064236,
                            41.654456
                        ],
                        [
                            -93.064599,
                            41.654464
                        ],
                        [
                            -93.064961,
                            41.654473
                        ],
                        [
                            -93.065324,
                            41.654481
                        ],
                        [
                            -93.065687,
                            41.654489
                        ],
                        [
                            -93.066038,
                            41.654765
                        ],
                        [
                            -93.06639,
                            41.655042
                        ],
                        [
                            -93.066752,
                            41.65505
                        ],
                        [
                            -93.067104,
                            41.655326
                        ],
                        [
                            -93.067467,
                            41.655334
                        ],
                        [
                            -93.067841,
                            41.655075
                        ],
                        [
                            -93.0684,
                            41.6549
                        ]
                    ],
                    "type": "LineString"
                },
                "id": "raindropPath",
                "properties": {},
                "type": "Feature"
            }
        ],
        "type": "FeatureCollection"
    }
    assert actual == expected
