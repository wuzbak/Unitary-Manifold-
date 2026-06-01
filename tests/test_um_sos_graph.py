from src.core.um_sos_graph import export_derivation_graph


def test_graph_export_shape():
    out = export_derivation_graph()
    assert out["metadata"]["acyclicity_verdict"] == "PASS"
    assert len(out["nodes"]) > 40
    assert len(out["links"]) > 40
