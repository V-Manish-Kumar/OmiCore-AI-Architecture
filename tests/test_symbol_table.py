from omnicore.compiler.symbol_table import SymbolTable, Symbol

def test_symbol_insertion_and_lookup():
    table = SymbolTable()
    sym1 = table.insert("findings", "data", producer_node_id="search_1")
    assert sym1.name == "findings"
    assert sym1.producer_node_id == "search_1"

    sym2 = table.lookup("findings")
    assert sym2 is not None
    assert sym2.producer_node_id == "search_1"

    sym3 = table.lookup("nonexistent")
    assert sym3 is None

def test_consumers_tracking():
    table = SymbolTable()
    table.insert("findings", "data", producer_node_id="search_1")
    table.add_consumer("findings", "summarize_1")
    table.add_consumer("findings", "compare_1")

    sym = table.lookup("findings")
    assert "summarize_1" in sym.consumers
    assert "compare_1" in sym.consumers
    assert len(sym.consumers) == 2

def test_implicit_declaration():
    table = SymbolTable()
    # Adding consumer to unregistered symbol should implicitly declare it
    table.add_consumer("unregistered_data", "process_1")
    
    sym = table.lookup("unregistered_data")
    assert sym is not None
    assert sym.producer_node_id is None
    assert "process_1" in sym.consumers
