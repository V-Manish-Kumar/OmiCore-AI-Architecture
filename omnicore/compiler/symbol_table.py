from typing import Dict, List, Optional

class Symbol:
    """
    Represents a symbol (e.g. data reference, parameter, node name) in the symbol table.
    """
    def __init__(self, name: str, symbol_type: str, producer_node_id: Optional[str] = None):
        self.name = name.lower().strip()
        self.symbol_type = symbol_type  # e.g., 'data', 'node', 'parameter'
        self.producer_node_id = producer_node_id
        self.consumers: List[str] = []  # list of node_ids consuming this symbol

    def __repr__(self) -> str:
        return f"Symbol(name='{self.name}', type='{self.symbol_type}', producer='{self.producer_node_id}', consumers={self.consumers})"


class SymbolTable:
    """
    Compiler symbol table to track variables, data flow, and dependency resolution.
    """
    def __init__(self):
        self.symbols: Dict[str, Symbol] = {}

    def insert(self, name: str, symbol_type: str, producer_node_id: Optional[str] = None) -> Symbol:
        """
        Inserts a new symbol or updates an existing one.
        """
        name_key = name.lower().strip()
        if name_key in self.symbols:
            sym = self.symbols[name_key]
            if producer_node_id and not sym.producer_node_id:
                sym.producer_node_id = producer_node_id
            return sym

        sym = Symbol(name_key, symbol_type, producer_node_id)
        self.symbols[name_key] = sym
        return sym

    def lookup(self, name: str) -> Optional[Symbol]:
        """
        Looks up a symbol by name.
        """
        return self.symbols.get(name.lower().strip())

    def add_consumer(self, name: str, consumer_node_id: str) -> None:
        """
        Registers a node ID that consumes the given symbol.
        """
        name_key = name.lower().strip()
        sym = self.lookup(name_key)
        if not sym:
            # Create a symbol if it doesn't exist (implicit forward declaration)
            sym = self.insert(name_key, "data")
        if consumer_node_id not in sym.consumers:
            sym.consumers.append(consumer_node_id)

    def get_all_symbols(self) -> List[Symbol]:
        """
        Returns all symbols registered in the table.
        """
        return list(self.symbols.values())

    def clear(self) -> None:
        """
        Clears all symbol declarations.
        """
        self.symbols.clear()
