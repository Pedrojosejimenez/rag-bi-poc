from src.bi.load_data import load_all
import pandas as pd

def test_bi_data_shapes():
    sales, support = load_all()
    assert {"date","region","product","sales","cost"}.issubset(set(sales.columns))
    assert {"created_at","resolved_at","priority","resolution_hours"}.issubset(set(support.columns))
    assert len(sales) > 0
    assert len(support) > 0
